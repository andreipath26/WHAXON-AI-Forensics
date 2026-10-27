"""Minimal Flask server for WHAXON. Stage 1: JSON API only."""
from __future__ import annotations

import asyncio
import os
import queue
import subprocess
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from whaxon.core import Core
from whaxon.core.events import (
    JobFailed,
    JobFindings,
    JobFinished,
    JobOutput,
    JobStarted,
)


class JobRegistry:
    """SSE-only wrapper. Persistence lives in core.store; this class
    keeps the per-worker subscribe queues for Server-Sent Events."""

    def __init__(self, core: Core) -> None:
        self.core = core
        self.store = core.store
        self._subs: dict[str, list] = {}
        self._lock = threading.RLock()
        self._wire_sse_bridge()

    def _wire_sse_bridge(self) -> None:
        """Bridge core events into SSE subscriber queues. Persistence
        is handled by Core._wire_store, so we only notify subscribers here."""
        def _on_started(e):
            self._notify(e.job_id, {"type": "status", "status": "running",
                                     "tool": e.tool_id, "target": e.target})
        def _on_output(e):
            self._notify(e.job_id, {"type": "line", "stream": e.stream, "text": e.line})
        def _on_finished(e):
            self._notify(e.job_id, {"type": "finished", "exit_code": e.exit_code,
                                     "duration_s": e.duration_s})
            self._notify(e.job_id, None)
        def _on_failed(e):
            self._notify(e.job_id, {"type": "failed", "error": e.error})
            self._notify(e.job_id, None)
        self.core.bus.subscribe(JobStarted, _on_started)
        self.core.bus.subscribe(JobOutput, _on_output)
        self.core.bus.subscribe(JobFinished, _on_finished)
        self.core.bus.subscribe(JobFailed, _on_failed)

    def ensure(self, job_id: str) -> None:
        self.store.create(job_id)

    def get(self, job_id: str):
        return self.store.get(job_id)

    def get_findings(self, job_id: str):
        return self.store.get_findings(job_id)

    def history(self, limit: int = 50):
        return self.store.history(limit)

    def subscribe(self, job_id: str):
        import queue as _q
        q: _q.Queue = _q.Queue()
        with self._lock:
            self._subs.setdefault(job_id, []).append(q)
        return q

    def unsubscribe(self, job_id: str, q) -> None:
        with self._lock:
            subs = self._subs.get(job_id, [])
            if q in subs:
                subs.remove(q)

    def _notify(self, job_id: str, message) -> None:
        with self._lock:
            subs = list(self._subs.get(job_id, []))
        for q in subs:
            q.put_nowait(message)


class AsyncRunner:
    """Run tools in background threads. Avoids asyncio subprocess issues on
    non-main-thread loops (Python 3.13). Publishes events to the core bus
    using the bus's own thread-safety."""

    def __init__(self, core: Core) -> None:
        self.core = core

    def submit(self, coro_factory) -> None:
        """Accept a zero-arg callable that runs the job and returns a job_id."""
        t = threading.Thread(target=self._wrap, args=(coro_factory,), daemon=True)
        t.start()

    def _wrap(self, coro_factory) -> None:
        import traceback
        try:
            coro_factory()
        except Exception:
            traceback.print_exc()


_PROCS: dict[str, subprocess.Popen] = {}
_RUN_LOOPS: dict[str, asyncio.AbstractEventLoop] = {}
_PROCS_LOCK = threading.Lock()


def _ai_run_blocking(core, executor_factory, run_id, goal, store):
    """Run the AI executor in a background thread, recording steps."""
    import asyncio as _aio
    import traceback as _tb
    provider_name = "null"
    try:
        ex = executor_factory()
        provider_name = getattr(getattr(ex, "agent", None), "provider", None)
        provider_name = getattr(provider_name, "name", "null") or "null"
        seq = {"n": 0}
        def on_action(a):
            pass
        def on_result(r):
            seq["n"] += 1
            store.append_ai_run_step(run_id, seq["n"], r.action.to_dict(), r.to_dict())
        ex.on_result = on_result
        history = _aio.run(ex.run(goal, job_id_prefix=run_id))
        last_err = ""
        if history and not history[-1].ok:
            last_err = history[-1].error or ""
        store.set_ai_run_finished(run_id, status="done" if not last_err else "failed", error=last_err)
    except Exception as e:
        _tb.print_exc()
        store.set_ai_run_finished(run_id, status="error", error=repr(e))

def _run_job_blocking(
    core: Core, registry: JobRegistry, tool_id: str, target: str,
    job_id: str, extra_args: str = "",
) -> None:
    """Execute web-submitted jobs through the same guarded core runner as the CLI."""
    import asyncio

    from whaxon.core.events import JobFailed
    from whaxon.core.scope import OutOfScopeError

    loop = asyncio.new_event_loop()
    try:
        try:
            timeout_s = float(_os.environ.get("WHAXON_JOB_TIMEOUT_S", "900"))
        except (TypeError, ValueError):
            timeout_s = 900.0
        if timeout_s <= 0:
            timeout_s = 900.0
        with _PROCS_LOCK:
            _RUN_LOOPS[job_id] = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(core.runner.run_tool(
            tool_id=tool_id,
            target=target,
            job_id=job_id,
            extra_args=extra_args,
            timeout_s=timeout_s,
            phase="web",
        ))
    except OutOfScopeError as exc:
        core.bus.publish(JobFailed(job_id=job_id, error=f"target blocked by scope: {exc}"))
    except FileNotFoundError:
        # ToolRunner already publishes JobFailed for missing executables.
        return
    except Exception as exc:
        import traceback
        traceback.print_exc()
        core.bus.publish(JobFailed(job_id=job_id, error=f"job execution failed: {exc}"))
    finally:
        with _PROCS_LOCK:
            _RUN_LOOPS.pop(job_id, None)
        asyncio.set_event_loop(None)
        loop.close()



def _cancel_job_blocking(core: Core, job_id: str) -> bool:
    """Cancel through the job's owning event loop to clean up its process tree."""
    import asyncio

    with _PROCS_LOCK:
        loop = _RUN_LOOPS.get(job_id)
    proc = core.runner._procs.get(job_id)
    if loop is None or proc is None:
        return False
    if not getattr(loop, "is_running", lambda: False)():
        return False
    future = asyncio.run_coroutine_threadsafe(core.runner.cancel(job_id), loop)
    try:
        future.result(timeout=5)
        return True
    except Exception:
        return False



import base64 as _b64
import hashlib as _hashlib

try:
    import bcrypt as _bcrypt
except ImportError:
    _bcrypt = None
import os as _os


def _get_credentials() -> tuple[str, str] | None:
    user = _os.environ.get("WHAXON_AUTH_USER", "").strip()
    pw_hash = _os.environ.get("WHAXON_AUTH_PASS_HASH", "").strip()
    if not user or not pw_hash:
        return None
    return user, pw_hash


def _hash_pw(pw: str) -> str:
    """Hash a password. Uses bcrypt if available, otherwise SHA-256."""
    if _bcrypt is not None:
        return _bcrypt.hashpw(pw.encode("utf-8"), _bcrypt.gensalt(rounds=12)).decode("utf-8")
    return _hashlib.sha256(pw.encode("utf-8")).hexdigest()


def _remote_auth_ready(user: str, password: str, password_hash: str) -> bool:
    """Require non-default credentials and bcrypt for network-facing deployments."""
    if not user or user == "whaxon":
        return False
    if password_hash:
        if _bcrypt is None:
            return False
        parts = password_hash.split("$")
        if len(parts) != 4:
            return False
        if parts[1] not in {"2a", "2b", "2y"}:
            return False
        if not parts[2].isdigit() or int(parts[2]) < 12:
            return False
        return len(password_hash) == 60
    return bool(password and password != "whaxon" and _bcrypt is not None)


def _check_auth(header: str | None) -> bool:
    creds = _get_credentials()
    # Missing credentials must never disable authentication implicitly.
    if creds is None:
        return False
    if not header or not header.startswith("Basic "):
        return False
    try:
        decoded = _b64.b64decode(header[6:]).decode("utf-8")
        user, _, pw = decoded.partition(":")
    except Exception:
        return False
    want_user, want_hash = creds
    if user != want_user:
        return False
    # bcrypt hashes start with $2b$ / $2a$ / $2y$
    if want_hash.startswith("$2"):
        if _bcrypt is None:
            return False
        try:
            return _bcrypt.checkpw(pw.encode("utf-8"), want_hash.encode("utf-8"))
        except Exception:
            return False
    # Legacy SHA-256 fallback
    return _hashlib.sha256(pw.encode("utf-8")).hexdigest() == want_hash



_FAIL_COUNTS: dict[str, tuple[int, float]] = {}
_TOO_MANY_FAILURES = 5
_TOO_MANY_WINDOW_S = 60.0


def _too_many_requests():
    from flask import Response
    return Response(
        "Too many failed authentication attempts.",
        429,
        {"Retry-After": str(int(_TOO_MANY_WINDOW_S))},
    )


def _record_auth_failure(peer: str) -> None:
    import time
    now = time.time()
    count, first = _FAIL_COUNTS.get(peer, (0, now))
    if now - first > _TOO_MANY_WINDOW_S:
        count, first = 0, now
    _FAIL_COUNTS[peer] = (count + 1, first)


def _auth_failures_exceeded(peer: str) -> bool:
    import time
    now = time.time()
    count, first = _FAIL_COUNTS.get(peer, (0, now))
    if now - first > _TOO_MANY_WINDOW_S:
        return False
    return count >= _TOO_MANY_FAILURES


def _unauthorized():
    from flask import Response
    return Response(
        "Authentication required.",
        401,
        {"WWW-Authenticate": "Basic realm=\"WHAXON\""},
    )



def _evidence_dir(core, job_id):
    """Return a job-specific evidence directory contained inside data/evidence."""
    import re

    if not isinstance(job_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", job_id):
        raise ValueError("invalid job id for evidence storage")
    data_root = Path(core.data_dir).resolve()
    evidence_root = data_root / "evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)
    evidence_root = evidence_root.resolve()
    if not evidence_root.is_relative_to(data_root):
        raise ValueError("evidence directory resolves outside the data directory")
    job_dir = evidence_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    job_dir = job_dir.resolve()
    if not job_dir.is_relative_to(evidence_root):
        raise ValueError("job evidence directory resolves outside the evidence directory")
    return job_dir


def _resolve_evidence_path(core, relative_path):
    """Resolve a stored evidence path and reject traversal or symlink escapes."""
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("evidence path is missing")
    data_root = Path(core.data_dir).resolve()
    full_path = (data_root / relative_path).resolve()
    if not full_path.is_relative_to(data_root):
        raise ValueError("evidence path resolves outside the data directory")
    return full_path

def create_app(core: Core, registry: JobRegistry, runner: AsyncRunner) -> Flask:
    import os as _os
    _host = _os.environ.get("WHAXON_HOST", "127.0.0.1")
    if _host not in ("127.0.0.1", "::1", "localhost"):
        import sys as _sys
        print(f"  [!] WHAXON_HOST={_host} — server is exposed on a network.\n"
              f"      Basic auth is enforced for non-loopback requests.\n"
              f"      Change WHAXON_AUTH_USER / WHAXON_AUTH_PASS before exposing.",
              file=_sys.stderr)

    app = Flask(__name__)
    # Only trust forwarded client metadata when an operator explicitly enables
    # it for a known reverse proxy. This lets Origin validation work correctly
    # behind HTTPS without trusting spoofable headers on direct deployments.
    if _os.environ.get("WHAXON_TRUST_PROXY", "").strip().lower() in {"1", "true", "yes"}:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    try:
        max_upload_mb = int(_os.environ.get("WHAXON_MAX_UPLOAD_MB", "25"))
    except ValueError:
        max_upload_mb = 25
    if not 1 <= max_upload_mb <= 1024:
        max_upload_mb = 25
    app.config["MAX_CONTENT_LENGTH"] = max_upload_mb * 1024 * 1024
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per minute"],
        storage_uri="memory://",
    )
    app.config["RATELIMIT_STORAGE_URI"] = "memory://"

    @app.before_request
    def _auth_gate():
        """Protect state-changing routes from cross-origin browser requests.

        Loopback is a useful local-development trust boundary, but browsers can
        be induced by an unrelated website to send requests to localhost. Check
        the Host header to resist DNS-rebinding and validate browser Origin /
        Fetch Metadata before applying the local-peer authentication shortcut.
        """
        import ipaddress as _ipaddress
        from urllib.parse import urlsplit as _urlsplit

        configured_host = _os.environ.get("WHAXON_HOST", "127.0.0.1")
        try:
            loopback_listener = _ipaddress.ip_address(configured_host.strip("[]")).is_loopback
        except ValueError:
            loopback_listener = configured_host.lower() == "localhost"

        # Also apply the host check to loopback clients when the server is
        # bound to 0.0.0.0/::; otherwise a local browser can reach that listener
        # through an attacker-controlled DNS-rebinding hostname.
        if loopback_listener or request.remote_addr in ("127.0.0.1", "::1"):
            request_host = request.host
            if request_host.startswith("[") and "]" in request_host:
                request_hostname = request_host[1:request_host.index("]")]
            elif request_host.count(":") == 1:
                request_hostname = request_host.rsplit(":", 1)[0]
            else:
                request_hostname = request_host
            allowed_hosts = {"localhost", "127.0.0.1", "::1"}
            allowed_hosts.update(
                item.strip().lower().rstrip(".")
                for item in _os.environ.get("WHAXON_ALLOWED_HOSTS", "").split(",")
                if item.strip()
            )
            if request_hostname.lower().rstrip(".") not in allowed_hosts:
                return {"error": "invalid Host for local request"}, 403

        # Fetch Metadata and Origin are CSRF defenses for state-changing requests.
        # Applying them to GET blocks ordinary browser navigation (including /ui and
        # favicon requests) when the browser sends same-site/cross-site metadata.
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            fetch_site = request.headers.get("Sec-Fetch-Site", "").lower()
            if fetch_site in {"cross-site", "same-site"}:
                return {"error": "cross-origin browser request rejected"}, 403
            origin = request.headers.get("Origin")
            if origin:
                supplied = _urlsplit(origin)
                current = _urlsplit(request.host_url)
                if (
                    supplied.scheme.lower() != current.scheme.lower()
                    or (supplied.hostname or "").lower() != (current.hostname or "").lower()
                    or supplied.port != current.port
                ):
                    return {"error": "cross-origin browser request rejected"}, 403

        if request.remote_addr in ("127.0.0.1", "::1"):
            return None
        if _auth_failures_exceeded(request.remote_addr):
            return _too_many_requests()
        if not _check_auth(request.headers.get("Authorization")):
            _record_auth_failure(request.remote_addr)
            return _unauthorized()

    @app.errorhandler(413)
    def upload_too_large(_error):
        return {"error": f"request exceeds the configured {max_upload_mb} MiB limit"}, 413

    @app.get("/favicon.ico")
    def favicon():
        return "", 204

    @app.get("/api/health")
    def health_probe():
        """Readiness probe: returns 200 when OK, 503 when MSF is down."""
        import time
        checks = {}
        try:
            checks["msf"] = "up" if registry.core.msf.is_up() else "down"
        except Exception as e:
            checks["msf"] = f"error: {e}"
        try:
            data_dir = Path(os.environ.get("WHAXON_DATA", "data"))
            data_dir.mkdir(parents=True, exist_ok=True)
            probe = data_dir / ".healthz"
            probe.write_text(str(time.time()))
            probe.unlink()
            checks["data"] = "writable"
        except Exception as e:
            checks["data"] = f"error: {e}"
        ok = checks.get("msf") == "up" and checks.get("data") == "writable"
        return jsonify({"status": "ok" if ok else "degraded", "checks": checks}), (200 if ok else 503)

    @app.get("/api/health/simple")
    def health_simple():
        return {"ok": True, "tools": len(core.catalog.list())}

    @app.get("/api/tools")
    def list_tools():
        import shutil

        from whaxon.adapters import get_adapter

        result = []
        for tool in core.catalog.list():
            try:
                adapter_available = get_adapter(tool.id) is not None
            except Exception:
                app.logger.exception("Adapter lookup failed for catalog tool %s", tool.id)
                adapter_available = False
            binary_available = bool(
                tool.binary
                and (
                    shutil.which(tool.binary)
                    or (
                        os.path.isabs(tool.binary)
                        and os.path.isfile(tool.binary)
                        and os.access(tool.binary, os.X_OK)
                    )
                )
            )
            result.append({
                "binary_available": binary_available,
                "transport": tool.transport,
                "id": tool.id,
                "name": tool.name,
                "category": tool.category,
                "binary": tool.binary,
                "description": tool.description,
                "available": bool(tool.available),
                "package": tool.package or "",
                "adapter_available": adapter_available,
            })
        return jsonify(result)

    @app.post("/api/run")
    @limiter.limit("30 per minute")
    def run_tool():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "request body must be a JSON object"}, 400
        tool_id = data.get("tool_id")
        target = data.get("target")
        extra_args = data.get("extra_args", "")
        if not isinstance(tool_id, str) or not tool_id.strip():
            return {"error": "tool_id must be a non-empty string"}, 400
        if not isinstance(target, str) or not target.strip():
            return {"error": "target must be a non-empty string"}, 400
        tool_id = tool_id.strip()
        target = target.strip()
        if len(tool_id) > 128 or len(target) > 2048 or "\\x00" in target:
            return {"error": "tool_id or target exceeds allowed limits"}, 400
        if extra_args is None:
            extra_args = ""
        # The web runner intentionally does not accept arbitrary command-line
        # arguments from clients. The current runner path does not implement a
        # safe per-tool argument allowlist, so reject rather than silently ignore.
        if not isinstance(extra_args, str) or extra_args.strip():
            return {"error": "extra_args are not supported by the web runner"}, 400

        # Scope enforcement is mandatory. Web out-of-scope overrides are
        # disabled until an operator-confirmed, target-bound audit flow exists.
        try:
            match = registry.core.scope.check(target)
        except Exception:
            # Authorization must fail closed: a broken scope engine must never
            # turn a target into an implicitly authorized one.
            app.logger.exception("Scope evaluation failed for tool run")
            return {"error": "scope evaluation failed; no job was started"}, 503
        if match is None:
            return {"error": "target could not be confirmed in scope; no job was started"}, 403
        if not match.allowed:
            # Do not accept a client-supplied flag as authorization. A safe,
            # auditable, operator-confirmed override flow must be implemented
            # before web requests can run out-of-scope targets.
            return {"error": f"target out of scope: {match.reason}",
                    "matched_rule": match.matched_rule}, 403
        if core.catalog.get(tool_id) is None:
            return {"error": f"unknown tool: {tool_id}"}, 404
        job_id = uuid.uuid4().hex[:12]
        registry.ensure(job_id)
        runner.submit(lambda: _run_job_blocking(core, registry, tool_id, target, job_id, extra_args))
        return {"job_id": job_id}, 202



    @app.post("/api/ai/run")
    @limiter.limit("10 per minute")
    def ai_run():
        data = request.get_json(silent=True) or {}
        goal = (data.get("goal") or "").strip()
        if not goal:
            return {"error": "goal required"}, 400
        target = (data.get("target") or "").strip() or None
        if target is None:
            try:
                from whaxon.core.targets import extract_target
                target = extract_target(goal)
            except Exception:
                target = None
        run_id = "ai-" + uuid.uuid4().hex[:12]
        core.store.create_ai_run(run_id, goal)
        _lock = target
        def _factory():
            from whaxon.core.ai_bridge import build_executor
            return build_executor(core, target_lock=_lock)
        runner.submit(lambda: _ai_run_blocking(core, _factory, run_id, goal, core.store))
        return {"run_id": run_id}, 202

    @app.get("/api/ai/runs")
    def ai_runs_list():
        limit = int(request.args.get("limit", "50"))
        return core.store.list_ai_runs(limit=limit)

    @app.get("/api/ai/pending")
    def ai_pending_list():
        owner = request.args.get("owner") or None
        return core.store.list_pending_runs(owner=owner)

    @app.post("/api/ai/runs/<run_id>/answer")
    def ai_run_answer(run_id: str):
        data = request.get_json(silent=True) or {}
        answer = (data.get("answer") or "").strip()
        if not answer:
            return {"error": "answer required"}, 400
        user = (data.get("user") or "local")
        note = (data.get("note") or "")
        run = core.store.get_ai_run(run_id)
        if run is None:
            return {"error": "run not found"}, 404
        if run.get("status") != "waiting":
            return {"error": "run is not waiting"}, 409
        next_seq = len(run.get("steps") or []) + 1
        core.store.add_approval(run_id, next_seq, user, answer, note)
        return {"ok": True, "run_id": run_id, "seq": next_seq}

    @app.get("/api/ai/runs/<run_id>")
    def ai_run_get(run_id: str):
        run = core.store.get_ai_run(run_id)
        if run is None:
            return {"error": "run not found"}, 404
        return run

    @app.get("/api/ai/runs/<run_id>/stream")
    def ai_run_stream(run_id: str):
        import json as _json
        import time as _t

        from flask import Response

        if core.store.get_ai_run(run_id) is None:
            return {"error": "run not found"}, 404

        def generate():
            last_seq = 0
            deadline = _t.monotonic() + 600.0
            while _t.monotonic() < deadline:
                run = core.store.get_ai_run(run_id)
                if run is None:
                    return
                for step in run.get("steps", []):
                    seq = step.get("seq", 0)
                    if seq <= last_seq:
                        continue
                    last_seq = seq
                    payload = {"type": "step", "seq": seq,
                               "action": step.get("action"),
                               "result": step.get("result")}
                    yield "data: %s\n\n" % _json.dumps(payload)
                if run.get("status") in ("done", "failed", "error"):
                    yield "data: %s\n\n" % _json.dumps(
                        {"type": "finished", "status": run.get("status"),
                         "error": run.get("error", "")})
                    return
                _t.sleep(1.0)
                yield ": ping\n\n"

        return Response(generate(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache",
                                 "X-Accel-Buffering": "no"})

    @app.get("/api/jobs/<job_id>/stream")
    def stream_job(job_id: str):
        import json as _json

        from flask import Response

        if registry.get(job_id) is None:
            return {"error": "unknown job"}, 404

        def generate():
            q = registry.subscribe(job_id)
            try:
                current = registry.get(job_id)
                if current:
                    yield f"data: {_json.dumps({'type': 'status', 'status': current['status']})}\n\n"
                    for line in current["lines"]:
                        yield f"data: {_json.dumps({'type': 'line', **line})}\n\n"
                    if current["status"] == "finished":
                        yield f"data: {_json.dumps({'type': 'finished', 'exit_code': current['exit_code']})}\n\n"
                        return
                    if current["status"] == "failed":
                        yield f"data: {_json.dumps({'type': 'failed', 'error': current['error']})}\n\n"
                        return
                while True:
                    try:
                        item = q.get(timeout=30)
                    except queue.Empty:
                        yield ": ping\n\n"
                        continue
                    if item is None:
                        return
                    yield f"data: {_json.dumps(item)}\n\n"
            finally:
                registry.unsubscribe(job_id, q)

        return Response(generate(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/api/history")
    def list_history():
        return jsonify(registry.history())

    @app.get("/api/jobs/<job_id>/evidence")
    def list_evidence(job_id: str):
        if not registry.core.store.get(job_id):
            return {"error": "job not found"}, 404
        items = registry.core.store.list_evidence(job_id)
        return jsonify(items)

    @app.post("/api/jobs/<job_id>/evidence")
    def add_evidence(job_id: str):
        if not registry.core.store.get(job_id):
            return {"error": "job not found"}, 404
        data = request.get_json(silent=True)
        if data and (data.get("note") or data.get("kind") == "note"):
            note = data.get("note", "")
            name = data.get("name", "note")
            if not isinstance(note, str) or len(note) > 10000:
                return {"error": "note must be a string of at most 10000 characters"}, 400
            if not isinstance(name, str) or len(name) > 200:
                return {"error": "name must be a string of at most 200 characters"}, 400
            seq = registry.core.store.add_evidence(
                job_id, "note", name, note=note)
            return {"seq": seq}, 201
        f = request.files.get("file")
        if f is None:
            return {"error": "provide file (multipart) or {note: ...} JSON"}, 400
        from werkzeug.utils import secure_filename
        safe_name = secure_filename(f.filename or "")
        if not safe_name:
            return {"error": "filename is empty or invalid"}, 400
        try:
            target_dir = _evidence_dir(registry.core, job_id)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        import uuid as _uuid
        disk_name = f"{_uuid.uuid4().hex[:12]}-{safe_name}"
        dest = target_dir / disk_name
        try:
            f.save(str(dest))
            relative_path = str(dest.resolve().relative_to(Path(registry.core.data_dir).resolve()))
            seq = registry.core.store.add_evidence(
                job_id, "file", safe_name,
                path=relative_path,
                note=request.form.get("note", "")[:10000])
        except Exception:
            try:
                dest.unlink(missing_ok=True)
            except OSError:
                app.logger.exception("Failed to clean up partial evidence upload")
            app.logger.exception("Evidence upload failed for job %s", job_id)
            return {"error": "evidence upload failed"}, 500
        return {"seq": seq, "name": safe_name}, 201

    @app.delete("/api/jobs/<job_id>/evidence/<int:seq>")
    def delete_evidence(job_id: str, seq: int):
        if not registry.core.store.get(job_id):
            return {"error": "job not found"}, 404
        items = registry.core.store.list_evidence(job_id)
        item = next((x for x in items if x["seq"] == seq), None)
        if item is None:
            return {"ok": False}, 404
        if item.get("path"):
            try:
                full = _resolve_evidence_path(registry.core, item["path"])
            except ValueError:
                app.logger.error("Refusing to delete evidence with unsafe path for job %s", job_id)
                return {"error": "unsafe evidence path"}, 403
            try:
                full.unlink(missing_ok=True)
            except OSError:
                app.logger.exception("Failed to remove evidence file for job %s", job_id)
                return {"error": "failed to remove evidence file"}, 500
        ok = registry.core.store.remove_evidence(job_id, seq)
        return {"ok": ok}, (200 if ok else 404)

    @app.get("/api/jobs/<job_id>/evidence/<int:seq>/download")
    def download_evidence(job_id: str, seq: int):
        from flask import send_file
        if not registry.core.store.get(job_id):
            return {"error": "job not found"}, 404
        items = registry.core.store.list_evidence(job_id)
        item = next((x for x in items if x["seq"] == seq), None)
        if not item or not item.get("path"):
            return {"error": "not a file"}, 404
        try:
            full = _resolve_evidence_path(registry.core, item["path"])
        except ValueError:
            app.logger.error("Refusing to download evidence with unsafe path for job %s", job_id)
            return {"error": "unsafe evidence path"}, 403
        if not full.is_file():
            return {"error": "file missing"}, 404
        return send_file(str(full), as_attachment=True, download_name=item["name"])

    def _msf_session_scope_error(session_id: str):
        """Require a live Metasploit session whose host is currently in scope."""
        client = registry.core.msf
        if not client.is_up():
            return {"error": "msf not reachable; session scope cannot be verified"}, 503
        try:
            live = client.sessions()
        except Exception:
            app.logger.exception("Could not read Metasploit sessions for scope check")
            return {"error": "could not verify session scope"}, 503
        info = live.get(str(session_id))
        if info is None:
            return {"error": "session not found"}, 404
        if not isinstance(info, dict):
            return {"error": "session details are invalid; refusing to act"}, 503
        host = info.get("target_host") or info.get("tunnel_peer")
        if not host:
            return {"error": "session host is unknown; refusing out-of-scope-capable action"}, 403
        try:
            match = registry.core.scope.check(str(host))
        except Exception:
            app.logger.exception("Scope evaluation failed for Metasploit session host")
            return {"error": "scope evaluation failed; action was not performed"}, 503
        if match is None or not getattr(match, "allowed", False):
            reason = getattr(match, "reason", "target could not be confirmed in scope")
            return {
                "error": f"session host out of scope: {reason}",
                "target": str(host),
                "matched_rule": getattr(match, "matched_rule", None),
            }, 403
        return None

    @app.get("/api/msf/status")
    def msf_status():
        client = registry.core.msf
        up = client.is_up()
        payload = {"up": up, "config": client.config.display()}
        if up:
            try:
                payload["version"] = client.version()
                payload["modules"] = client.module_counts()
            except Exception as e:
                payload["error"] = str(e)
        return jsonify(payload)

    @app.get("/api/msf/sessions")
    def msf_sessions():
        client = registry.core.msf
        stored = registry.core.store.list_sessions(include_closed=True)
        live = client.sessions() if client.is_up() else {}
        return jsonify({
            "stored": stored,
            "live": live,
            "live_count": len(live),
        })

    @app.post("/api/msf/run")
    def msf_run():
        import re as _re
        import uuid as _uuid
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "request body must be a JSON object"}, 400
        module_type = data.get("module_type", "exploit")
        module_path = data.get("module_path", "")
        options = data.get("options") or {}
        target_value = data.get("target") or ""
        if not isinstance(module_type, str) or not isinstance(module_path, str):
            return {"error": "module_type and module_path must be strings"}, 400
        if not isinstance(options, dict):
            return {"error": "options must be a JSON object"}, 400
        module_type = module_type.strip()
        module_path = module_path.strip()
        if not module_path:
            return {"error": "module_path required"}, 400
        if module_type not in ("exploit", "auxiliary", "post"):
            return {"error": f"bad module_type: {module_type}"}, 400
        if (
            module_path.startswith("/")
            or any(part in {"", ".", ".."} for part in module_path.split("/"))
            or not _re.fullmatch(r"[A-Za-z0-9_/-]+", module_path)
        ):
            return {"error": "invalid Metasploit module path"}, 400
        if not isinstance(target_value, str):
            return {"error": "target must be a string"}, 400
        for key, value in options.items():
            if not isinstance(key, str) or not _re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", key):
                return {"error": "invalid Metasploit option name"}, 400
            if value is None or isinstance(value, (dict, list, tuple)):
                return {"error": f"option {key} must be a scalar value"}, 400
            value_text = str(value)
            if len(value_text) > 2048 or any(ch in value_text for ch in ("\r", "\n", "\x00")):
                return {"error": f"option {key} contains invalid or oversized data"}, 400
        for key in ("RHOSTS", "RHOST"):
            if options.get(key) is not None and not isinstance(options[key], str):
                return {"error": f"{key} must be a string"}, 400

        target = target_value.strip() or str(options.get("RHOSTS") or options.get("RHOST") or "").strip()
        session_host = ""
        if module_type == "post":
            session_id = options.get("SESSION")
            if session_id is None or not str(session_id).strip():
                return {"error": "post modules require a SESSION option"}, 400
            session_error = _msf_session_scope_error(str(session_id).strip())
            if session_error:
                return session_error
            try:
                session_info = registry.core.msf.sessions().get(str(session_id).strip()) or {}
            except Exception:
                app.logger.exception("Could not read Metasploit session for post module")
                return {"error": "could not verify post-module session"}, 503
            session_host = str(session_info.get("target_host") or session_info.get("tunnel_peer") or "").strip()
            if not session_host:
                return {"error": "post-module session host is unknown"}, 403
            if not target:
                target = session_host

        # Scope enforcement is server-side and cannot be disabled by request data.
        candidates = []
        if target:
            candidates.extend(h.strip() for h in target.split(",") if h.strip())
        rhosts = options.get("RHOSTS") or options.get("RHOST") or ""
        if rhosts:
            for host in rhosts.split(","):
                host = host.strip()
                if host and host not in candidates:
                    candidates.append(host)
        if not candidates:
            return {"error": "an explicit in-scope target (RHOST/RHOSTS) is required"}, 400
        for cand in candidates:
            try:
                match = registry.core.scope.check(cand)
            except Exception:
                app.logger.exception("Scope evaluation failed for Metasploit target")
                return {"error": "scope evaluation failed; no job was started"}, 503
            if match is None or not getattr(match, "allowed", False):
                reason = getattr(match, "reason", "target could not be confirmed in scope")
                matched_rule = getattr(match, "matched_rule", None)
                return {"error": f"target out of scope: {reason}",
                        "matched_rule": matched_rule,
                        "target": cand}, 403

        # Build the extra args
        extra_parts = [f"{k}={v}" for k, v in options.items()]
        extra_args = " ".join(extra_parts)

        from whaxon.adapters import get_adapter
        adapter = get_adapter("msf")
        if adapter is None:
            return {"error": "msf adapter not registered"}, 500

        job_id = _uuid.uuid4().hex[:12]
        registry.core.store.create(job_id)
        registry.core.store.set_started(job_id, "msf", target or "?")

        # Run in a thread, publish findings like the runner does
        def _do_run():
            import traceback

            from whaxon.core.events import JobFailed, JobFinished
            try:
                tool_id = f"msf:{module_type}:{module_path}"
                registry.core.store.append_line(job_id, "stdout",
                    f"running {tool_id} with {extra_args}")
                findings = adapter.run_module(tool_id, extra_args, ctx={"target": target, "store": registry.core.store, "job_id": job_id})
                for f in findings:
                    if f.kind == "msf_module_started" or f.kind == "msf_session":
                        registry.core.store.append_line(job_id, "stdout", f.raw_line)
                    elif f.kind == "msf_error":
                        registry.core.store.append_line(job_id, "stderr", f.raw_line)
                if findings:
                    registry.core.store.set_finished(job_id, 0, 0.0)
                    registry.core.bus.publish(JobFindings(
                        job_id=job_id,
                        findings=tuple(f.to_dict() for f in findings),
                    ))
                else:
                    registry.core.store.set_finished(job_id, 0, 0.0)
                registry.core.bus.publish(JobFinished(
                    job_id=job_id, exit_code=0, duration_s=0.0,
                ))
            except Exception as e:
                traceback.print_exc()
                registry.core.store.set_failed(job_id, str(e))
                registry.core.bus.publish(JobFailed(job_id=job_id, error=str(e)))

        import threading as _t
        _t.Thread(target=_do_run, daemon=True).start()

        return {"job_id": job_id}, 202

    @app.post("/api/msf/sessions/<session_id>/exec")
    def msf_session_exec(session_id: str):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "request body must be a JSON object"}, 400
        command = data.get("command", "")
        if not isinstance(command, str) or not command.strip():
            return {"error": "command required"}, 400
        command = command.strip()
        if len(command) > 4096 or "\x00" in command:
            return {"error": "command must be at most 4096 characters and contain no NUL"}, 400
        session_error = _msf_session_scope_error(session_id)
        if session_error:
            return session_error

        client = registry.core.msf
        try:
            output = client.session_exec(session_id, command, timeout=15.0)
        except Exception as e:
            return {"error": str(e)}, 500

        return jsonify({
            "session_id": session_id,
            "command": command,
            "output": output,
        })

    @app.get("/api/msf/sessions/<session_id>")
    def msf_session_info(session_id: str):
        session_error = _msf_session_scope_error(session_id)
        if session_error:
            return session_error
        client = registry.core.msf
        try:
            live = client.sessions()
            info = live.get(str(session_id))
            if info is None:
                return {"error": "session not found"}, 404
            return jsonify({"id": session_id, "info": info})
        except Exception as e:
            return {"error": str(e)}, 500

    @app.get("/api/msf/modules/<module_type>")
    def msf_list_modules(module_type: str):
        client = registry.core.msf
        if not client.is_up():
            return {"error": "msf not reachable"}, 503
        try:
            c = client.connect()
            if module_type == "exploit":
                return jsonify(c.modules.exploits[:200])
            if module_type == "auxiliary":
                return jsonify(c.modules.auxiliary[:200])
            if module_type == "post":
                return jsonify(c.modules.post[:200])
            return {"error": f"bad type: {module_type}"}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    @app.get("/api/tree")
    def get_tree():
        limit = request.args.get("limit", type=int) or 50
        return jsonify({"targets": registry.core.store.findings_by_target(limit=limit)})

    @app.get("/api/scope")
    def get_scope():
        return jsonify(registry.core.scope.summary())

    @app.post("/api/scope")
    def save_scope():
        """Validate and persist an operator-edited scope definition."""
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "JSON object required"}, 400
        enabled = data.get("enabled", True)
        if type(enabled) is not bool:
            return {"error": "'enabled' must be a JSON boolean"}, 400
        current_scope = registry.core.scope.summary()
        # Confirmation is required only for the transition from enforced to
        # disabled. Once enforcement is already disabled, operators must still
        # be able to edit the scope rules without repeatedly confirming the same
        # state transition.
        if enabled is False and current_scope.get("enabled", True) is not False and data.get("confirm_disable") is not True:
            return {"error": "confirm_disable=true is required to disable scope enforcement"}, 400
        engagement = data.get("engagement", "")
        notes = data.get("notes", "")
        if not isinstance(engagement, str) or len(engagement) > 200:
            return {"error": "engagement must be a string of at most 200 characters"}, 400
        if not isinstance(notes, str) or len(notes) > 5000:
            return {"error": "notes must be a string of at most 5000 characters"}, 400
        from whaxon.core.scope import _validate_scope_rule
        rules = {}
        for key in ("in_scope", "out_of_scope"):
            value = data.get(key, [])
            if not isinstance(value, list) or len(value) > 500:
                return {"error": f"'{key}' must be a list with at most 500 rules"}, 400
            normalized = []
            for item in value:
                if not isinstance(item, str) or not item.strip() or len(item.strip()) > 253:
                    return {"error": f"invalid rule in '{key}'"}, 400
                rule = item.strip()
                if not _validate_scope_rule(rule):
                    return {"error": f"invalid scope rule: {rule}"}, 400
                if rule not in normalized:
                    normalized.append(rule)
            rules[key] = normalized
        try:
            registry.core.scope.save({
                "engagement": engagement.strip(),
                "enabled": enabled,
                "in_scope": rules["in_scope"],
                "out_of_scope": rules["out_of_scope"],
                "notes": notes.strip(),
            })
        except (OSError, RuntimeError, ValueError) as exc:
            return {"error": f"scope was not saved: {exc}"}, 400
        return jsonify(registry.core.scope.summary())

    @app.post("/api/scope/check")
    def check_scope():
        data = request.get_json(silent=True) or {}
        target = (data.get("target") or "").strip()
        if not target:
            return {"error": "target required"}, 400
        match = registry.core.scope.check(target)
        return jsonify(match.to_dict())

    @app.post("/api/scope/override")
    def log_override():
        data = request.get_json(silent=True) or {}
        target = (data.get("target") or "").strip()
        tool = (data.get("tool") or "").strip()
        if not target:
            return {"error": "target required"}, 400
        from whaxon.core.override_log import log_override
        log_override(registry.core.data_dir, tool, target)
        return {"logged": True}

    def _validation_scope_error(target_url: str | None):
        """Re-check current scope before any validator network replay."""
        if not target_url:
            return {"error": "finding has no target URL; replay was not attempted"}, 400
        try:
            match = registry.core.scope.check(target_url)
        except Exception:
            app.logger.exception("Scope evaluation failed before validation replay")
            return {"error": "scope evaluation failed; replay was not attempted"}, 503
        if match is None or not getattr(match, "allowed", False):
            reason = getattr(match, "reason", "target could not be confirmed in scope")
            return {
                "error": f"target out of scope: {reason}; replay was not attempted",
                "matched_rule": getattr(match, "matched_rule", None),
            }, 403
        return None

    @app.post("/api/validate/<job_id>/<int:seq>")
    def api_validate(job_id: str, seq: int):
        from whaxon.core.findings import Finding
        from whaxon.core.validator import Validator
        findings = registry.core.store.get_findings(job_id) or []
        target_f = next((f for f in findings if f["seq"] == seq), None)
        if not target_f:
            return {"error": "finding not found"}, 404
        job = registry.core.store.get(job_id) or {}
        raw_target = job.get("target", "")
        if raw_target.startswith(("http://", "https://")):
            target_url = raw_target
        elif raw_target:
            target_url = f"http://{raw_target}"
        else:
            target_url = None
        scope_error = _validation_scope_error(target_url)
        if scope_error:
            return scope_error
        f_obj = Finding(
            kind=target_f["kind"], severity=target_f["severity"],
            source=target_f["source"], data=target_f["data"],
            raw_line=target_f["raw_line"],
            request_context=target_f.get("request_context") or {},
        )
        pkg_payloads = Path(__file__).resolve().parent.parent / "data" / "payloads"
        v = Validator(pkg_payloads)
        status, reason = v.validate(f_obj, target_url=target_url)
        registry.core.store.update_verification(job_id, seq, status, by="engine", reason=reason)
        return {"status": status, "reason": reason}

    @app.post("/api/retest/<job_id>/<int:seq>")
    def api_retest(job_id: str, seq: int):
        from whaxon.core.findings import Finding
        from whaxon.core.validator import Validator
        findings = registry.core.store.get_findings(job_id) or []
        target_f = next((f for f in findings if f["seq"] == seq), None)
        if not target_f:
            return {"error": "finding not found"}, 404
        if target_f.get("verification_status") != "verified":
            return {
                "error": "not verified",
                "verification_status": target_f.get("verification_status"),
            }, 400
        job = registry.core.store.get(job_id) or {}
        raw_target = job.get("target", "")
        if raw_target.startswith(("http://", "https://")):
            target_url = raw_target
        elif raw_target:
            target_url = f"http://{raw_target}"
        else:
            target_url = None
        scope_error = _validation_scope_error(target_url)
        if scope_error:
            return scope_error
        f_obj = Finding(
            kind=target_f["kind"], severity=target_f["severity"],
            source=target_f["source"], data=target_f["data"],
            raw_line=target_f["raw_line"],
            request_context=target_f.get("request_context") or {},
        )
        pkg_payloads = Path(__file__).resolve().parent.parent / "data" / "payloads"
        v = Validator(pkg_payloads)
        status, reason = v.revalidate(f_obj, target_url=target_url)
        registry.core.store.update_verification(job_id, seq, status, by="engine", reason=reason)
        return {"status": status, "reason": reason}

    @app.get("/api/coverage/<job_id>")
    def api_coverage(job_id: str):
        rows = registry.core.store.list_coverage(job_id)
        return jsonify({"job_id": job_id, "gaps": rows, "count": len(rows)})

    @app.post("/api/approvals/<job_id>/<int:seq>/resolve")
    def api_approval_resolve(job_id: str, seq: int):
        data = request.get_json(silent=True) or {}
        status = data.get("status", "").strip().lower()
        if status not in ("verified", "refuted"):
            return {"error": "status must be verified or refuted"}, 400
        findings = registry.core.store.get_findings(job_id) or []
        target_f = next((f for f in findings if f["seq"] == seq), None)
        if not target_f:
            return {"error": "finding not found"}, 404
        user = data.get("user") or "human"
        registry.core.store.update_verification(job_id, seq, status, by=f"human:{user}", reason=f"human review by {user}")
        return {"ok": True, "status": status, "by": f"human:{user}"}

    @app.post("/api/import/burp")
    def import_burp():
        import uuid as _uuid
        f = request.files.get("file")
        if f is None:
            return {"error": "no file provided"}, 400
        if not f.filename.lower().endswith(".xml"):
            return {"error": "expects .xml"}, 400

        # Save to a temp file so the adapter can parse it
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            f.save(tmp.name)
            tmp_path = Path(tmp.name)

        try:
            from whaxon.adapters import get_adapter
            adapter = get_adapter("burp")
            if adapter is None:
                return {"error": "burp adapter not registered"}, 500
            findings = adapter.parse_file(tmp_path)
        finally:
            try: tmp_path.unlink()
            except Exception: pass

        if not findings:
            return {"error": "no findings parsed"}, 400

        job_id = _uuid.uuid4().hex[:12]
        registry.core.store.create(job_id)
        target = findings[0].data.get("host") or "imported"
        registry.core.store.set_started(job_id, "burp", target)
        registry.core.store.append_line(job_id, "stdout",
            f"Imported {len(findings)} finding(s) from {f.filename}")
        for x in findings:
            loc = x.data.get("location") or x.data.get("path") or ""
            registry.core.store.append_line(job_id, "stdout",
                f"  [{x.severity}] {x.data.get('name', '')} {loc}")
        for i, x in enumerate(findings):
            registry.core.store.append_finding(job_id, x.to_dict(), i)
        registry.core.store.set_finished(job_id, 0, 0.0)

        return {"job_id": job_id, "target": target, "count": len(findings)}, 201

    @app.get("/api/jobs/<job_id>/report")
    def get_report(job_id: str):
        from flask import Response

        from whaxon.core.report import render_html, render_markdown
        job = registry.get(job_id)
        if job is None:
            return {"error": "unknown job"}, 404
        findings = registry.get_findings(job_id) or []
        fmt = request.args.get("format") or request.args.get("fmt") or "md"
        if fmt == "html":
            return Response(render_html(job, findings), mimetype="text/html")
        if fmt == "pdf":
            from whaxon.core.report import render_pdf
            try:
                pdf = render_pdf(job, findings)
            except Exception as e:
                return {"error": f"pdf render failed: {e}"}, 500
            return Response(pdf, mimetype="application/pdf",
                            headers={"Content-Disposition": f"attachment; filename=job-{job_id}.pdf"})
        return Response(render_markdown(job, findings), mimetype="text/markdown")

    @app.get("/api/jobs/<job_id>/findings")
    def get_job_findings(job_id: str):
        findings = registry.get_findings(job_id)
        if findings is None:
            return {"error": "unknown job"}, 404
        return jsonify(findings)

    @app.get("/api/jobs/<job_id>/output.txt")
    def download_output_txt(job_id: str):
        from flask import Response
        job = registry.get(job_id)
        if job is None:
            return {"error": "unknown job"}, 404
        lines = job.get("lines") or []
        body = chr(10).join((l.get("text") or "") for l in lines)
        return Response(body, mimetype="text/plain",
            headers={"Content-Disposition": f"attachment; filename=job-{job_id}.txt"})

    @app.get("/api/jobs/<job_id>/findings.csv")
    def download_findings_csv(job_id: str):
        import csv
        import io

        from flask import Response
        findings = registry.get_findings(job_id)
        if findings is None:
            return {"error": "unknown job"}, 404
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["kind", "severity", "source", "cvss", "cwe", "raw_line"])
        for f in findings:
            w.writerow([f.get("kind",""), f.get("severity",""), f.get("source",""),
                        f.get("cvss") or "", f.get("cwe",""),
                        (f.get("raw_line") or "").replace(chr(10), " ")])
        return Response(buf.getvalue(), mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=job-{job_id}.csv"})

    @app.get("/api/jobs/<job_id>/findings.json")
    def download_findings_json(job_id: str):
        import json as _json

        from flask import Response
        findings = registry.get_findings(job_id)
        if findings is None:
            return {"error": "unknown job"}, 404
        body = _json.dumps(findings, indent=2)
        return Response(body, mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename=job-{job_id}.json"})

    @app.get("/api/status")
    def api_status():
        """Platform-wide safety + capability flags."""
        import os
        scope_enabled = False
        engagement = "default"
        try:
            scope = registry.core.scope
            scope_enabled = bool(scope.enabled)
            engagement = str(scope.engagement or "default")
        except Exception:
            pass
        default_creds = (
            os.environ.get("WHAXON_AUTH_USER", "whaxon") == "whaxon"
            and os.environ.get("WHAXON_AUTH_PASS", "whaxon") == "whaxon"
        )
        autochain = os.environ.get("WHAXON_MSF_AUTOCHAIN", "").strip() in ("1", "true", "yes")
        msf_up = False
        try:
            msf_up = registry.core.msf.is_up()
        except Exception:
            pass
        return jsonify({
            "scope_enabled": scope_enabled,
            "engagement": engagement,
            "default_creds": default_creds,
            "autochain": autochain,
            "msf_up": msf_up,
        })

    # ---------- port forwards ----------

    @app.get("/api/msf/sessions/<session_id>/portfwd")
    def pf_list(session_id: str):
        from whaxon.core import portfwd as _pf
        session_error = _msf_session_scope_error(session_id)
        if session_error:
            return session_error
        try:
            live = _pf.list_live(registry.core.msf, session_id)
        except Exception as e:
            return jsonify({"session_id": session_id, "error": str(e), "live": []})
        return jsonify({"session_id": session_id, "live": live})

    @app.post("/api/msf/sessions/<session_id>/portfwd")
    def pf_add(session_id: str):
        from whaxon.core import portfwd as _pf
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "request body must be a JSON object"}, 400
        lport = data.get("lport")
        rhost = data.get("rhost")
        rport = data.get("rport")
        label = data.get("label", "")
        if not isinstance(rhost, str) or not rhost.strip() or lport is None or rport is None:
            return {"error": "lport, rhost, rport required"}, 400
        if not isinstance(label, str) or len(label) > 200:
            return {"error": "label must be a string of at most 200 characters"}, 400
        try:
            if isinstance(lport, bool) or isinstance(rport, bool):
                raise ValueError
            local_port = int(lport)
            remote_port = int(rport)
            if not 1 <= local_port <= 65535 or not 1 <= remote_port <= 65535:
                raise ValueError
        except (TypeError, ValueError):
            return {"error": "lport and rport must be integers between 1 and 65535"}, 400
        rhost = rhost.strip()
        session_error = _msf_session_scope_error(session_id)
        if session_error:
            return session_error
        try:
            match = registry.core.scope.check(rhost)
        except Exception:
            app.logger.exception("Scope evaluation failed for port-forward destination")
            return {"error": "scope evaluation failed; port forward was not created"}, 503
        if match is None or not getattr(match, "allowed", False):
            reason = getattr(match, "reason", "target could not be confirmed in scope")
            return {"error": f"port-forward destination out of scope: {reason}",
                    "target": rhost, "matched_rule": getattr(match, "matched_rule", None)}, 403
        try:
            fwd = _pf.add_forward(registry.core.msf, session_id,
                                  local_port, rhost, remote_port, label.strip())
        except Exception as e:
            return {"error": str(e)}, 500
        try:
            from whaxon.core import pivot as _pivot
            conn = registry.core.store._conn()
            try:
                _pivot.add_edge(conn,
                                parent_kind="session", parent_id=str(session_id),
                                child_kind="forward", child_id=str(lport),
                                relation="tunnels_via",
                                evidence=f"{rhost}:{rport}")
                print(f"[pivot] wrote session={session_id} -> forward={lport} -> {rhost}:{rport}", flush=True)
            finally:
                try: conn.close()
                except Exception: pass
        except Exception as e:
            import traceback as _tb
            print(f"[pivot] WRITE FAILED: {type(e).__name__}: {e}", flush=True)
            _tb.print_exc()
        return jsonify(fwd.to_dict())

    @app.delete("/api/msf/sessions/<session_id>/portfwd")
    def pf_del(session_id: str):
        from whaxon.core import portfwd as _pf
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "request body must be a JSON object"}, 400
        lport = data.get("lport")
        if lport is None:
            return {"error": "lport required"}, 400
        try:
            if isinstance(lport, bool) or not isinstance(lport, (int, str)):
                raise ValueError
            if isinstance(lport, str) and not lport.strip().isdigit():
                raise ValueError
            local_port = int(lport)
            if not 1 <= local_port <= 65535:
                raise ValueError
        except (TypeError, ValueError):
            return {"error": "lport must be an integer between 1 and 65535"}, 400
        session_error = _msf_session_scope_error(session_id)
        if session_error:
            return session_error
        fwd = _pf.Forward(session_id=session_id, lport=local_port, rhost="", rport=0)
        return jsonify(_pf.remove_forward(registry.core.msf, fwd))

    @app.get("/api/settings")
    def api_settings_get():
        try:
            return jsonify(registry.core.settings.get())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.post("/api/settings")
    def api_settings_post():
        data = request.get_json(silent=True) or {}
        try:
            updated = registry.core.settings.save(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify(updated)

    @app.get("/api/pivot/graph")
    def api_pivot_graph():
        from whaxon.core import pivot as _pivot
        try:
            conn = registry.core.store._conn()
        except Exception:
            conn = None
        if conn is None:
            return jsonify({"edges": [], "count": 0})
        try:
            return jsonify(_pivot.graph(conn))
        finally:
            try: conn.close()
            except Exception: pass

    @app.get("/api/pivot/sessions/<session_id>/chain")
    def api_pivot_chain(session_id: str):
        from whaxon.core import pivot as _pivot
        conn = getattr(registry.core.store, "_conn", None)
        if conn is None:
            return jsonify({"session_id": session_id, "root_exploits": [], "descendants": []})
        return jsonify(_pivot.chain_for_session(conn, session_id))

    @app.get("/api/pivot/candidates")
    def api_pivot_candidates():
        """Ask each live session for its routing table; return subnets it can
        reach that the host probably cannot."""
        from whaxon.core import autopivot as _ap
        results = []
        try:
            sessions = registry.core.msf.sessions()
        except Exception:
            sessions = {}
        for sid in sessions:
            try:
                cands = _ap.detect(registry.core.msf, sid)
            except Exception as e:
                cands = [{"error": str(e)}]
            results.append({"session_id": str(sid), "candidates": cands})
        return jsonify({"sessions": results})

    @app.get("/api/report")
    def api_report():
        """Generate an engagement report.

        Query params:
          engagement=<name>   default: 'default'
          format=md|json      default: 'md'
        """
        from whaxon.core import report as _report
        eng = request.args.get("engagement") or "default"
        fmt = (request.args.get("format") or request.args.get("fmt") or "md").lower()
        jobs_filter = (request.args.get("jobs") or "").strip()
        data = _report._load(registry.core.store, eng)
        if jobs_filter:
            wanted = {j.strip() for j in jobs_filter.split(",") if j.strip()}
            if wanted:
                data["jobs"] = [e for e in data["jobs"] if e["job"]["id"] in wanted]
                from whaxon.core.report import _LOOT_KINDS, _SEV_ORDER
                sev = {sx: 0 for sx in _SEV_ORDER}
                loot = []
                for entry in data["jobs"]:
                    for f in entry["findings"]:
                        sx = (f.get("severity") or "info").lower()
                        if sx in sev:
                            sev[sx] += 1
                        if f.get("kind") in _LOOT_KINDS:
                            loot.append({**f, "_job_id": entry["job"]["id"]})
                data["severity_counts"] = sev
                data["finding_count"] = sum(sev.values())
                data["job_count"] = len(data["jobs"])
                data["loot"] = loot
        # attach pivot chains
        from whaxon.core import report as _report
        data["chains"] = _report.attach_chains(registry.core.store)
        if fmt == "json":
            resp = jsonify(data)
            resp.headers["Content-Disposition"] = "attachment; filename=whaxon-report.json"
            return resp
        if fmt in ("html", "htm"):
            resp = app.response_class(_report.to_html(data), mimetype="text/html")
            resp.headers["Content-Disposition"] = "attachment; filename=whaxon-report.html"
            return resp
        md = _report.to_markdown(data, chains=data.get("chains", []))
        if fmt == "pdf":
            try:
                pdf = _report.to_pdf_bytes(data)
            except Exception as e:
                return {"error": f"pdf render failed: {e}"}, 500
            return app.response_class(pdf, mimetype="application/pdf",
                headers={"Content-Disposition": "attachment; filename=whaxon-report.pdf"})
        if fmt == "whaxon":
            import datetime as _dt
            import hashlib as _hashlib
            import json as _json
            canonical = _json.dumps(data, default=str, sort_keys=True)
            digest = _hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            from whaxon import __version__ as _whaxon_version
            envelope = {
                "format": "whaxon",
                "version": 1,
                "generated": data.get("generated") or _dt.datetime.now().isoformat(timespec="seconds"),
                "tool": "whaxon/" + _whaxon_version,
                "engagement": eng,
                "integrity": "sha256:" + digest,
                "payload": data,
            }
            out = _json.dumps(envelope, default=str, indent=2)
            resp = app.response_class(out, mimetype="application/json")
            resp.headers["Content-Disposition"] = "attachment; filename=whaxon-report.whaxon"
            return resp
        resp = app.response_class(md, mimetype="text/markdown")
        resp.headers["Content-Disposition"] = "attachment; filename=whaxon-report.md"
        return resp

    @app.get("/api/loot")
    def api_loot():
        """Aggregate loot-kind findings across all jobs, deduped."""
        loot_kinds = {"env_var", "sysinfo", "platform", "ntlm_hash",
                      "service", "msf_session", "msf_loot", "msf_loot_file",
                      "sqlmap_database", "sqlmap_table", "sqlmap_row",
                      "nuclei_finding", "cve", "exploit_suggestion",
                      "network_iface", "system_section"}
        limit = int(request.args.get("limit", 500))
        seen = set()
        out = []
        for job in registry.history(limit=200):
            try:
                findings = registry.get_findings(job["id"]) or []
            except Exception:
                continue
            for f in findings:
                kind = f.get("kind")
                if kind not in loot_kinds:
                    continue
                # dedupe key: (kind, canonical payload)
                d = f.get("data") or {}
                key_parts = [kind]
                for k in ("name", "value", "user", "port", "proto",
                          "session_id", "path", "field", "platform"):
                    if k in d:
                        key_parts.append(str(d[k]))
                key = tuple(key_parts)
                if key in seen:
                    continue
                seen.add(key)
                out.append({**f, "_job_id": job["id"]})
                if len(out) >= limit:
                    break
            if len(out) >= limit:
                break
        return jsonify({"count": len(out), "loot": out})

    @app.get("/api/jobs/<job_id>")
    def get_job(job_id: str):
        job = registry.get(job_id)
        if job is None:
            return {"error": "unknown job"}, 404
        return jsonify(job)

    @app.get("/settings")
    def settings_page():
        from flask import render_template as _rt
        return _rt("settings.html")

    @app.get("/ui-v2/scope")
    def ui_v2_scope():
        """Canonical scope and targets page backed by the live ScopeManager."""
        return render_template("ui_v2_scope.html")

    @app.get("/ui-v2/reports")
    def ui_v2_reports():
        """Canonical report page backed by the live report API."""
        return render_template("ui_v2_reports.html")

    @app.get("/ui-v2/run")
    def ui_v2_run():
        """Canonical run and orchestration page backed by the live job API."""
        return render_template("ui_v2_run.html")

    @app.get("/ui-v2/findings")
    def ui_v2_findings():
        """Canonical findings design, wired to live report and validation APIs."""
        return render_template("ui_v2_findings.html")

    @app.get("/ui-v2/history")
    def ui_v2_history():
        """Canonical job history page backed by recorded WHAXON jobs."""
        return render_template("ui_v2_history.html")

    @app.get("/ui-v2/diagnostics")
    def ui_v2_diagnostics():
        """Canonical diagnostics page backed by live health and tool APIs."""
        return render_template("ui_v2_diagnostics.html")

    @app.get("/ui-v2/evidence")
    def ui_v2_evidence():
        """Canonical evidence inspector backed by recorded job evidence."""
        return render_template("ui_v2_evidence.html")

    @app.get("/ui-v2/ai")
    def ui_v2_ai():
        """Canonical AI strategy gate backed by live AI run and scope APIs."""
        return render_template("ui_v2_ai.html")

    @app.get("/ui-v2/retest")
    def ui_v2_retest():
        """Canonical remediation retest page backed by verified findings."""
        return render_template("ui_v2_retest.html")

    @app.get("/ui-v2/chains")
    def ui_v2_chains():
        """Canonical attack-chain page backed by stored pivot graph data."""
        return render_template("ui_v2_chains.html")

    @app.get("/ui-v2/adapters")
    def ui_v2_adapters():
        """Canonical adapter manager backed by the live tool catalog."""
        return render_template("ui_v2_adapters.html")

    @app.get("/ui-v2/settings")
    def ui_v2_settings():
        """Read-only settings and API explorer with secret redaction."""
        return render_template("ui_v2_settings.html")

    @app.get("/ui-v2/audit")
    def ui_v2_audit():
        """Show recorded execution metadata without inventing cryptographic claims."""
        return render_template("ui_v2_audit.html")

    @app.get("/ui-v2")
    def ui_v2_dashboard():
        """Canonical engagement dashboard with live core-page navigation."""
        return render_template("ui_v2_dashboard.html")

    @app.get("/ui")
    def ui():
        return render_template("index.html")

    @app.post("/api/jobs/<job_id>/cancel")
    def cancel_job(job_id: str):
        ok = _cancel_job_blocking(core, job_id)
        return {"ok": ok, "job_id": job_id}

    @app.get("/")
    def index():
        from flask import redirect
        return redirect("/ui")

    return app


def create_app_factory(host: str | None = None, port: int | None = None):
    """Gunicorn entry point. Reads env vars, with optional explicit host/port.

    When host or port is provided, WHAXON_HOST/WHAXON_PORT are also set in
    os.environ so create_app's exposed-on-network warning fires correctly.
    """
    if host is None:
        host = os.environ.get("WHAXON_HOST", "127.0.0.1")
    if port is None:
        port = int(os.environ.get("WHAXON_PORT", "5001"))

    # Never synthesize the known demo credentials for a network-facing
    # listener. Loopback development remains convenient; remote deployments
    # must explicitly configure a non-default username and password.
    import ipaddress
    try:
        loopback = ipaddress.ip_address(host.strip("[]")).is_loopback
    except ValueError:
        loopback = host.lower() == "localhost"
    configured_user = os.environ.get("WHAXON_AUTH_USER", "").strip()
    configured_pass = os.environ.get("WHAXON_AUTH_PASS", "")
    configured_hash = os.environ.get("WHAXON_AUTH_PASS_HASH", "").strip()
    if not loopback and not _remote_auth_ready(
        configured_user, configured_pass, configured_hash
    ):
        raise RuntimeError(
            "Refusing to expose WHAXON on a non-loopback host without "
            "explicit non-default authentication credentials."
        )

    os.environ["WHAXON_HOST"] = host
    os.environ["WHAXON_PORT"] = str(port)
    os.environ.setdefault("WHAXON_AUTH_USER", "whaxon")
    if not os.environ.get("WHAXON_AUTH_PASS_HASH", "").strip():
        os.environ["WHAXON_AUTH_PASS_HASH"] = _hash_pw(
            os.environ.get("WHAXON_AUTH_PASS", "whaxon")
        )
    data_dir = Path(os.environ.get("WHAXON_DATA", "data"))
    core = Core(data_dir=data_dir)
    registry = JobRegistry(core)
    runner = AsyncRunner(core)
    return create_app(core, registry, runner)


def main(args: list[str] | None = None) -> None:
    host = os.environ.get("WHAXON_HOST", "127.0.0.1")
    port = int(os.environ.get("WHAXON_PORT", "5001"))
    import ipaddress
    try:
        loopback = ipaddress.ip_address(host.strip("[]")).is_loopback
    except ValueError:
        loopback = host.lower() == "localhost"

    # Convenience defaults are permitted only for loopback development.
    # Validate remote credentials before creating a fallback hash; otherwise a
    # custom username with an omitted password could inherit the demo password.
    if not loopback:
        configured_user = os.environ.get("WHAXON_AUTH_USER", "").strip()
        configured_pass = os.environ.get("WHAXON_AUTH_PASS", "")
        configured_hash = os.environ.get("WHAXON_AUTH_PASS_HASH", "").strip()
        if not _remote_auth_ready(
            configured_user, configured_pass, configured_hash
        ):
            raise SystemExit(
                "Refusing network exposure without explicit non-default "
                "WHAXON_AUTH_USER and WHAXON_AUTH_PASS or WHAXON_AUTH_PASS_HASH."
            )
    else:
        os.environ.setdefault("WHAXON_AUTH_USER", "whaxon")

    # Hash the explicitly supplied password only after remote credentials have
    # passed validation. This keeps custom remote credentials usable without
    # ever manufacturing a known password for an exposed listener.
    if not os.environ.get("WHAXON_AUTH_PASS_HASH", "").strip():
        os.environ["WHAXON_AUTH_PASS_HASH"] = _hash_pw(
            os.environ.get("WHAXON_AUTH_PASS", "whaxon")
        )

    data_dir = Path(os.environ.get("WHAXON_DATA", "data"))

    core = Core(data_dir=data_dir)
    registry = JobRegistry(core)
    runner = AsyncRunner(core)

    app = create_app(core, registry, runner)
    auth_user = os.environ.get("WHAXON_AUTH_USER", "")
    auth_on = "enabled" if auth_user else "DISABLED"
    print()
    print("  WHAXON web interface")
    print(f"  → http://{host}:{port}/ui")
    print(f"  → data directory: {data_dir}")
    print(f"  → authentication: {auth_on}" + (f" (user: {auth_user})" if auth_user else ""))
    print()
    auth_pass_effective = os.environ.get("WHAXON_AUTH_PASS", "whaxon")
    is_default_creds = (auth_user == "whaxon" and auth_pass_effective == "whaxon")
    is_loopback = host in ("127.0.0.1", "::1")
    if is_default_creds and not is_loopback:
        print()
        print("  ERROR: default credentials (whaxon/whaxon) on non-loopback host " + host + ".")
        print("  Set WHAXON_AUTH_USER and WHAXON_AUTH_PASS before exposing on a network.")
        print("  Refusing to start.")
        raise SystemExit(1)
    if is_default_creds:
        print("  NOTE: default credentials (whaxon/whaxon) in use. Safe on loopback only.")
        print("  Change WHAXON_AUTH_USER / WHAXON_AUTH_PASS before exposing on a network.")
        print()
    # Dev server. whaxon serve uses waitress via serve.py instead.
    app.run(host=host, port=port, debug=False, use_reloader=False)
