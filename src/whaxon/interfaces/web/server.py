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
        from whaxon.adapters import get_adapter

        result = []
        for tool in core.catalog.list():
            try:
                adapter_available = get_adapter(tool.id) is not None
            except Exception:
                app.logger.exception("Adapter lookup failed for catalog tool %s", tool.id)
                adapter_available = False
            result.append({
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

    # The source-of-truth designs live in the repository's existing
    # "web ui files and rendering" directory. Serve those files directly so
    # their layout and visual design are preserved; keep the prior UI available
    # unchanged at /legacy-ui.
    _NEW_UI_PAGES = {
        "dashboard-zero-state": "dashboard_engagement_hub_zero_state/code.html",
        "scope-and-targets": "scope_targets_forensics_hardened/code.html",
        "run-and-orchestration": "run_tool_orchestration_forensics_hardened/code.html",
        "trust-layer-and-findings": "trust_layer_verified_findings/code.html",
        "trust-layer-approvals-queue-modal": "trust_layer_approvals_queue_modal/code.html",
        "ptes-coverage-and-reports": "ptes_coverage_reports/code.html",
        "bas-and-detection-validation": "bas_detection_validation/code.html",
        "compliance-and-framework-crosswalk": "compliance_framework_crosswalk/code.html",
        "threat-intel-and-exploit-arsenal": "threat_intel_exploit_arsenal/code.html",
        "ai-strategy-gate": "ai_strategy_gate_human_in_the_loop/code.html",
        "remediation-retest-studio": "remediation_retest_studio_forensics_hardened/code.html",
        "attack-surface-and-continuous-monitoring": "attack_surface_continuous_monitoring/code.html",
        "correlated-attack-chains": "correlated_attack_chains/code.html",
        "bug-bounty-and-live-browser-studio": "bug_bounty_live_browser_studio/code.html",
        "ptaas-client-portal": "ptaas_client_portal/code.html",
        "job-execution-history": "job_execution_history/code.html",
        "evidence-file-inspector": "evidence_file_inspector/code.html",
        "cryptographic-audit-log": "cryptographic_audit_log/code.html",
        "system-diagnostics-and-health": "system_diagnostics_health/code.html",
        "adapter-and-plugin-manager": "adapter_plugin_manager/code.html",
        "settings-and-api-explorer": "settings_secrets_vault/code.html",
        "settings-and-secrets-vault": "settings_secrets_vault/code.html",
        "scope-targets": "scope_targets_forensics_hardened/code.html",
        "run-orchestration": "run_tool_orchestration_forensics_hardened/code.html",
        "trust-layer-findings": "trust_layer_verified_findings/code.html",
        "ptes-coverage-reports": "ptes_coverage_reports/code.html",
        "bug-bounty-live-browser": "bug_bounty_live_browser_studio/code.html",
        "system-diagnostics-health": "system_diagnostics_health/code.html",
        "adapter-plugin-manager": "adapter_plugin_manager/code.html",
        "settings-secrets-vault": "settings_secrets_vault/code.html",
    }

    def _new_ui_script(page: str) -> str:
        import json as _json
        page_json = _json.dumps(page)
        return r"""<script>
(function () {
  'use strict';
  const page = """ + page_json + r""";
  const pages = """ + _json.dumps(_NEW_UI_PAGES) + r""";
  document.querySelectorAll('[data-path]').forEach(function (link) {
    const slug = link.getAttribute('data-path');
    if (pages[slug]) link.setAttribute('href', '/ui/' + slug);
    else link.style.display = 'none';
  });
  async function requestJson(url, options) {
    const response = await fetch(url, options || {});
    let body = {};
    try { body = await response.json(); } catch (_) {}
    if (!response.ok) throw new Error(body.error || ('HTTP ' + response.status));
    return body;
  }
  function flattenFindings(report) {
    const result = [];
    (report.jobs || []).forEach(function (entry) {
      const job = entry.job || {};
      (entry.findings || []).forEach(function (finding) {
        result.push({job: job, finding: finding});
      });
    });
    return result;
  }
  function severity(value) {
    const v = String(value || 'info').toLowerCase();
    return ({critical:'CRITICAL',high:'HIGH',medium:'MEDIUM',low:'LOW',info:'INFO'})[v] || v.toUpperCase();
  }
  function status(value) {
    const v = String(value || 'candidate').toLowerCase();
    return v.replace(/_/g, ' ').toUpperCase();
  }
  function setHidden(element, hidden) {
    if (!element) return;
    element.hidden = !!hidden;
    if (hidden) {
      element.classList.add('hidden');
      element.style.display = 'none';
    } else {
      element.classList.remove('hidden');
      element.style.display = '';
    }
  }
  function hideButtonByText(needle) {
    const normalizedNeedle = String(needle || '').toLowerCase();
    document.querySelectorAll('button').forEach(function (button) {
      if ((button.textContent || '').toLowerCase().includes(normalizedNeedle)) {
        setHidden(button, true);
        button.setAttribute('aria-hidden', 'true');
      }
    });
  }
  // Remove hard-coded demo identity and global actions that have no backend route.
  document.querySelectorAll('span, button').forEach(function (element) {
    const label = (element.textContent || '').trim();
    if (label === 'OP//7749-ALPHA' || label === 'Lead Security Engineer' ||
        label === 'ENGINE STANDBY' || label.includes('ENG-2026-X892') ||
        label === 'Target: api.internal.corp') {
      setHidden(element, true);
      element.setAttribute('aria-hidden', 'true');
    }
  });
  hideButtonByText('add new');
  hideButtonByText('terminal log');
  hideButtonByText('emergency halt scan');
  async function wireFindings() {
    hideButtonByText('mark fixed');
    hideButtonByText('export proof to issue tracker');
    if (page !== 'trust-layer-approvals-queue-modal') hideButtonByText('send to approvals');
    const initialReplay = document.getElementById('replay-btn');
    if (initialReplay) initialReplay.disabled = true;
    const cards = Array.from({length:4}, function (_, i) {
      return document.getElementById('finding-card-' + (i + 1));
    }).filter(Boolean);
    const heading = Array.from(document.querySelectorAll('span')).find(function (el) {
      return /Attack Surface Findings/.test(el.textContent || '');
    });
    try {
      const report = await requestJson('/api/report?format=json');
      const rows = flattenFindings(report);
      const templateCard = cards[0];
      while (templateCard && cards.length < rows.length) {
        const clone = templateCard.cloneNode(true);
        clone.id = 'finding-card-' + (cards.length + 1);
        setHidden(clone, false);
        cards[cards.length - 1].after(clone);
        cards.push(clone);
      }
      if (heading) heading.textContent = 'Attack Surface Findings (' + rows.length + ')';
      cards.forEach(function (card, index) {
        const item = rows[index];
        if (!item) { setHidden(card, true); card.dataset.hasFinding = 'false'; return; }
        card.dataset.hasFinding = 'true';
        const f = item.finding, job = item.job;
        const line = card.querySelector('.flex.items-center.gap-space-sm');
        const labels = line ? line.querySelectorAll('span') : [];
        if (labels[0]) labels[0].textContent = severity(f.severity);
        const stripe = card.querySelector('.absolute.left-0');
        if (stripe) { stripe.classList.remove('bg-error','bg-tertiary','bg-secondary','bg-primary'); stripe.classList.add(({critical:'bg-error',high:'bg-error',medium:'bg-tertiary',low:'bg-secondary',info:'bg-primary'})[String(f.severity || 'info').toLowerCase()] || 'bg-primary'); }
        if (labels[1]) labels[1].textContent = f.title || f.kind || f.raw_line || 'Finding';
        if (labels[2]) labels[2].textContent = status(f.verification_status || f.status);
        const target = card.querySelector('p');
        if (target) target.textContent = f.target || job.target || f.url || f.endpoint || 'Target not recorded';
        const meta = card.querySelector('.flex.flex-col.items-end');
        if (meta) {
          const metaLabels = meta.querySelectorAll('span');
          if (metaLabels[0]) metaLabels[0].textContent = f.cvss != null ? 'CVSS ' + f.cvss : 'CVSS N/A';
          if (metaLabels[1]) metaLabels[1].textContent = f.source || job.tool || 'WHAXON';
        }
        card.dataset.severity = String(f.severity || 'info').toLowerCase();
        card.dataset.jobId = job.id || '';
        card.dataset.seq = String(f.seq == null ? '' : f.seq);
        card.dataset.status = String(f.verification_status || f.status || 'candidate').toLowerCase();
        card.dataset.rawLine = f.raw_line || '';
        card.dataset.description = (f.data && f.data.description) || f.description || '';
        card.dataset.remediation = (f.data && f.data.remediation) || f.remediation || '';
        card.onclick = function () {
          cards.forEach(function (other) {
            other.classList.remove('ring-1', 'ring-primary/40', 'bg-surface-container');
            other.classList.add('bg-surface-container-low');
          });
          card.classList.add('ring-1', 'ring-primary/40', 'bg-surface-container');
          card.classList.remove('bg-surface-container-low');
          window.__whaxonSelectedFinding = {jobId:card.dataset.jobId, seq:card.dataset.seq, status:card.dataset.status, finding:f, job:job};
          const proof = document.getElementById('curl-proof-payload');
          if (proof) {
            const raw = card.dataset.rawLine;
            proof.textContent = raw || 'No raw proof line was recorded for this finding.';
          }
          const detailColumn = document.querySelector('.lg\\:col-span-7');
          if (detailColumn) {
            const headerCard = detailColumn.firstElementChild;
            if (headerCard) {
              const title = headerCard.querySelector('.font-code-lg');
              if (title) title.textContent = f.title || f.kind || 'Finding';
              const severityBadge = headerCard.querySelector('.bg-error-container');
              if (severityBadge) severityBadge.textContent = severity(f.severity) + ' SEVERITY';
              const endpointLabel = Array.from(headerCard.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'TARGET ENDPOINT'; });
              const endpoint = endpointLabel && endpointLabel.parentElement.querySelectorAll('span')[1];
              if (endpoint) endpoint.textContent = f.url || f.endpoint || f.target || job.target || 'Target not recorded';
              const metadata = headerCard.querySelector('.font-code-sm.text-error.font-bold');
              const cvss = f.cvss != null ? f.cvss : (f.data && f.data.cvss);
              if (metadata) metadata.textContent = cvss != null ? String(cvss) : 'CVSS not provided';
              const engineLabel = Array.from(headerCard.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'DETECTION ENGINE'; });
              const engineValue = engineLabel && engineLabel.parentElement.querySelectorAll('span')[1];
              if (engineValue) engineValue.textContent = f.source || job.tool || 'Not recorded';
              const phaseLabel = Array.from(headerCard.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'PTES PHASE'; });
              const phaseValue = phaseLabel && phaseLabel.parentElement.querySelectorAll('span')[1];
              if (phaseValue) phaseValue.textContent = f.phase || (f.data && f.data.phase) || 'Not recorded';
              const oldDetails = headerCard.querySelectorAll('[data-whaxon-detail]');
              oldDetails.forEach(function (node) { node.remove(); });
              const description = (f.data && f.data.description) || f.description || '';
              const remediation = (f.data && f.data.remediation) || f.remediation || '';
              [description, remediation].forEach(function (value, index) {
                if (!value) return;
                const block = document.createElement('p'); block.dataset.whaxonDetail = 'true';
                block.className = 'font-body-sm text-body-sm text-on-surface-variant';
                block.textContent = (index ? 'Remediation: ' : 'Description: ') + value;
                headerCard.appendChild(block);
              });
            }
            const proofPanel = detailColumn.children[1];
            if (proofPanel) {
              Array.from(proofPanel.children).forEach(function (child) {
                const keep = child.contains(document.getElementById('curl-proof-payload')) || child.contains(document.getElementById('replay-btn'));
                setHidden(child, !keep);
              });
            }
          }
          if (proof) {
            const raw = card.dataset.rawLine;
            proof.textContent = raw || 'No raw proof line was recorded for this finding.';
            const proofSection = proof.closest('.flex.flex-col.gap-space-xs');
            if (proofSection) setHidden(proofSection, !raw);
          }
          const replay = document.getElementById('replay-btn');
          if (replay) {
            replay.disabled = !card.dataset.jobId || !card.dataset.seq || !['candidate','verified'].includes(card.dataset.status);
            const label = replay.querySelector('span:last-child');
            if (label) label.textContent = card.dataset.status === 'verified' ? 'Replay Test (Retest)' : 'Validate Finding';
          }
        };
      });
      const first = cards.find(function (card) { return !card.hidden; });
      if (first) first.click();
      const kpiLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'Active Scans'; });
      if (kpiLabel) {
        const kpiGrid = kpiLabel.closest('.grid');
        if (kpiGrid) setHidden(kpiGrid, true);
      }
      const replay = document.getElementById('replay-btn');
      if (replay) {
        replay.disabled = !first || !first.dataset.jobId || !first.dataset.seq || !['candidate','verified'].includes(first.dataset.status);
        const label = replay.querySelector('span:last-child');
        if (label && first) label.textContent = first.dataset.status === 'verified' ? 'Replay Test (Retest)' : 'Validate Finding';
      }
      const replayReady = Array.from(document.querySelectorAll('span')).find(function (el) { return /Replay Ready:/.test(el.textContent || ''); });
      if (replayReady) setHidden(replayReady, true);
      const fakeMarker = Array.from(document.querySelectorAll('span')).find(function (el) { return /Matched Pattern: DB_PASSWORD/.test(el.textContent || ''); });
      if (fakeMarker) { const box = fakeMarker.closest('.mt-space-md'); if (box) setHidden(box, true); }
      const methodology = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'Methodology Step:'; });
      if (methodology) { const box = methodology.closest('.mt-space-md'); if (box) setHidden(box, true); }
      const filterCounts = {
        'ALL': rows.length,
        'CRIT': rows.filter(function (item) { return String(item.finding.severity || '').toLowerCase() === 'critical'; }).length,
        'HIGH': rows.filter(function (item) { return String(item.finding.severity || '').toLowerCase() === 'high'; }).length,
        'MED': rows.filter(function (item) { return String(item.finding.severity || '').toLowerCase() === 'medium'; }).length,
        'LOW': rows.filter(function (item) { return ['low','info'].includes(String(item.finding.severity || '').toLowerCase()); }).length,
        'VERIFIED': rows.filter(function (item) { return /verified/i.test(String(item.finding.verification_status || item.finding.status || '')); }).length,
        'CANDIDATE': rows.filter(function (item) { return /candidate|pending/i.test(String(item.finding.verification_status || item.finding.status || '')); }).length
      };
      const searchInput = document.querySelector('input[placeholder*="Filter proof pattern"]');
      let activeFilter = 'ALL';
      function applyFindingFilters() {
        const query = searchInput ? searchInput.value.toLowerCase() : '';
        cards.forEach(function (card) {
          if (card.dataset.hasFinding !== 'true') { setHidden(card, true); return; }
          const sev = String(card.dataset.severity || '').toLowerCase();
          const state = String(card.dataset.status || '').toLowerCase();
          const text = [card.textContent, card.dataset.rawLine, card.dataset.description, card.dataset.remediation].join(' ').toLowerCase();
          const stateMatch = activeFilter === 'ALL' ? true :
            activeFilter === 'CRIT' ? sev === 'critical' :
            activeFilter === 'HIGH' ? sev === 'high' :
            activeFilter === 'MED' ? sev === 'medium' :
            activeFilter === 'LOW' ? ['low','info'].includes(sev) :
            activeFilter === 'VERIFIED' ? state === 'verified' :
            activeFilter === 'CANDIDATE' ? ['candidate','pending'].includes(state) :
            ['candidate','pending'].includes(state);
          setHidden(card, !stateMatch || !text.includes(query));
        });
        const selected = cards.find(function (card) { return !card.hidden; });
        if (selected) selected.click();
      }
      Array.from(document.querySelectorAll('button')).forEach(function (button) {
        const match = (button.textContent || '').trim().match(/^(ALL|CRIT|HIGH|MED|LOW|VERIFIED|CANDIDATE|REVIEW NEEDED)/i);
        if (!match) return;
        const key = match[1].toUpperCase();
        button.textContent = key === 'REVIEW NEEDED' ? key : key + ' (' + (filterCounts[key] || 0) + ')';
        button.onclick = function () { activeFilter = key; applyFindingFilters(); };
      });
      if (searchInput) searchInput.oninput = applyFindingFilters;    } catch (error) {
      wireUnavailablePage();
    }
    window.triggerReplayAction = async function () {
      const selected = window.__whaxonSelectedFinding;
      if (!selected || !['candidate','verified'].includes(selected.status)) return;
      const action = selected.status === 'verified' ? 'retest' : 'validate';
      const button = document.getElementById('replay-btn');
      if (button) button.disabled = true;
      try {
        const result = await requestJson('/api/' + action + '/' + encodeURIComponent(selected.jobId) + '/' + encodeURIComponent(selected.seq), {method:'POST'});
        window.alert(action + ': ' + (result.status || 'completed') + (result.reason ? '\\n' + result.reason : ''));
        window.location.reload();
      } catch (error) { window.alert('Retest failed: ' + error.message); }
      finally { if (button) button.disabled = false; }
    };
  }
  async function wireScope() {
    try {
      const data = await requestJson('/api/scope');
      const body = document.getElementById('targetTableBody');
      if (body) {
        body.replaceChildren();
        const rows = [
          ...(data.in_scope || []).map(function (target) { return {target:target, allowed:true}; }),
          ...(data.out_of_scope || []).map(function (target) { return {target:target, allowed:false}; })
        ];
        const table = body.closest('table');
        if (table) table.querySelectorAll('thead th').forEach(function (cell, index) {
          if (index > 0 && index < 6) setHidden(cell, true);
        });
        rows.forEach(function (item) {
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-surface-container/60 transition-colors';
          const target = document.createElement('td');
          target.className = 'py-2.5 px-space-md font-semibold';
          target.textContent = item.target;
          tr.appendChild(target);
          for (let i = 1; i < 6; i++) {
            const hiddenCell = document.createElement('td');
            setHidden(hiddenCell, true);
            tr.appendChild(hiddenCell);
          }
          const state = document.createElement('td');
          state.className = 'py-2.5 px-space-md text-right';
          state.textContent = item.allowed ? 'IN SCOPE' : 'EXCLUDED';
          state.classList.add(item.allowed ? 'text-primary' : 'text-error');
          tr.appendChild(state);
          body.appendChild(tr);
        });
        if (!rows.length) {
          const tr = document.createElement('tr'), td = document.createElement('td');
          td.colSpan = 7;
          td.className = 'p-space-lg text-outline';
          td.textContent = 'No scope rules configured.';
          tr.appendChild(td);
          body.appendChild(tr);
        }
        const filter = document.getElementById('targetFilterInput');
        if (filter) filter.oninput = function () {
          const q = filter.value.toLowerCase();
          body.querySelectorAll('tr').forEach(function (tr) {
            setHidden(tr, !tr.textContent.toLowerCase().includes(q));
          });
        };
      }
      ['quick import','add in-scope target','next','view certificate san chain',
       'mark out-of-scope exclusion','promote to scope','add boundary exclusion',
       'commit to scope','import & parse rules'].forEach(hideButtonByText);
      document.querySelectorAll('button').forEach(function (button) {
        const label = (button.textContent || '').toLowerCase();
        if (!/commit to scope|import & parse rules|add in-scope target|add boundary exclusion/.test(label)) return;
        const modal = button.closest('.fixed');
        if (modal) setHidden(modal, true);
      });
      const targetModal = document.getElementById('modalTargetInput');
      if (targetModal) {
        const modal = targetModal.closest('.fixed');
        if (modal) setHidden(modal, true);
      }
      const importText = document.querySelector('textarea[placeholder*="target"]');
      if (importText) {
        const modal = importText.closest('.fixed');
        if (modal) setHidden(modal, true);
      }
    } catch (error) {
      wireUnavailablePage();
    }
  }
  async function wireReports() {
    const previewButton = document.getElementById('previewBtn');
    const closeButton = document.getElementById('closePreviewBtn');
    const modal = document.getElementById('previewModal');
    const preview = modal && modal.querySelector('pre');
    const title = modal && modal.querySelector('h3 code');
    const buttons = Array.from(document.querySelectorAll('main button'));
    const exportJson = buttons.find(function (button) { return /Export Findings \(\.json\)/i.test(button.textContent || ''); });
    const exportPdf = buttons.find(function (button) { return /Download Full Report \(\.pdf\)/i.test(button.textContent || ''); });
    function setBusy(button, busy) { if (button) button.disabled = busy; }
    async function fetchMarkdown() {
      const response = await fetch('/api/report?format=md');
      if (!response.ok) throw new Error('Report request failed (HTTP ' + response.status + ')');
      return response.text();
    }
    if (previewButton) previewButton.onclick = async function () {
      setBusy(previewButton, true);
      try {
        const markdown = await fetchMarkdown();
        if (preview) preview.textContent = markdown || 'No report content is available yet.';
        if (title) title.textContent = 'whaxon-report.md';
        if (modal) { modal.classList.remove('hidden'); modal.classList.add('flex'); }
      } catch (error) {
        window.alert('Unable to load the report preview: ' + error.message);
      } finally { setBusy(previewButton, false); }
    };
    if (closeButton) closeButton.onclick = function () {
      if (modal) { modal.classList.add('hidden'); modal.classList.remove('flex'); }
    };
    if (exportJson) exportJson.onclick = function () { window.location.assign('/api/report?format=json'); };
    if (exportPdf) exportPdf.onclick = function () { window.location.assign('/api/report?format=pdf'); };
    // Never represent hard-coded sample engagement values or proof as live data.
    document.querySelectorAll('main span, main h2, main h3, main p').forEach(function (element) {
      const value = (element.textContent || '').trim();
      if (!/ENG-2026-X892|api\.internal\.corp|Sample Deterministic Proof|ENGAGEMENT HASH MANIFEST|41 automated vulnerability templates|6 vulnerabilities were deterministically verified/i.test(value)) return;
      const container = element.closest('.bg-surface-container-lowest, .bg-surface-container-low');
      if (container && !container.contains(previewButton) && !(modal && modal.contains(container))) setHidden(container, true);
      else if (!container) setHidden(element, true);
    });
    // The proof card wraps its sample title and explanatory claims outside the
    // code block. Hide the complete native card so no prototype proof is shown
    // beside a live report export.
    const sampleProofTitle = Array.from(document.querySelectorAll('main span')).find(function (element) {
      return /Sample Deterministic Proof: FINDING-SQLI-001/i.test(element.textContent || '');
    });
    if (sampleProofTitle) {
      const proofHeading = sampleProofTitle.closest('div.flex.items-center.justify-between.text-outline.pb-1');
      setHidden(proofHeading || sampleProofTitle, true);
    }
    document.querySelectorAll('main p, main span').forEach(function (element) {
      if (/Verified deterministically without LLM ambiguity|HTTP\/2 200 OK|PostgreSQL 15\.4/i.test((element.textContent || '').trim())) {
        setHidden(element, true);
      }
    });
    // Strip fixed report-page HUD figures from the supplied prototype.
    const prototypeMetrics = /^(?:6 curl-verified|84\.5%|41 Scans|17 Findings|6 Confirmed|3 Artifacts|TEMPLATE V4\.2|Target Phase 3|0x7F41\.\.\.B289 \[VALID\]|Evidence Integrity Guaranteed|PTES Certified Evidence Locker|SHA256 Manifest Lock)$/i;
    document.querySelectorAll('main span, main strong, main code, main p').forEach(function (element) {
      if (prototypeMetrics.test((element.textContent || '').trim())) setHidden(element, true);
    });
    // Keep the original report synthesis/export section; the phase tracker,
    // evidence locker, and gap-matrix sections are static mock engagement data.
    const previewSection = previewButton && previewButton.closest('section');
    document.querySelectorAll('main section').forEach(function (section) {
      if (!section.contains(previewButton)) setHidden(section, true);
    });
    document.querySelectorAll('main input[type="checkbox"]').forEach(function (input) {
      const label = input.closest('label') || input.parentElement;
      if (label && !label.contains(previewButton)) setHidden(label, true);
    });
    // The coverage matrix and SIEM rule recommendations in this design are
    // static examples; this backend does not produce those telemetry claims.
    document.querySelectorAll('main h2, main h3, main span').forEach(function (element) {
      const value = (element.textContent || '').trim();
      if (/Coverage Gap Matrix|Rule Recommendations|3 DOCUMENTED EXCLUSIONS|SEC-AZ-992|CROWDSTRIKE|SPLUNK & SENTINEL|FIN7 \/ APT29/i.test(value)) {
        const container = element.closest('.bg-surface-container-low.rounded-lg, .bg-surface-container-lowest.rounded-lg');
        if (container && !container.contains(previewButton)) setHidden(container, true);
        else setHidden(element, true);
      }
    });
    try { await requestJson('/api/report?format=json'); }
    catch (_) {
      [previewButton, exportJson, exportPdf].forEach(function (button) { if (button) button.disabled = true; });
    }
  }
  async function wireRun() {
    const targetInput = document.querySelector('input[placeholder*="Target host"]');
    const output = document.getElementById('terminal-stdout');
    let selectedJob = null, stream = null;
    if (targetInput) targetInput.value = '';
    if (output) output.textContent = 'Ready. Choose a registered tool and a target permitted by the configured scope.';
    let tools = [];
    try {
      const response = await requestJson('/api/tools');
      tools = Array.isArray(response) ? response : (response.tools || []);
    } catch (_) { wireUnavailablePage(); return; }
    const usable = tools.filter(function (tool) { return tool && tool.id && tool.available !== false; });
    const runButtons = Array.from(document.querySelectorAll('main button')).filter(function (button) {
      return (button.textContent || '').trim().toLowerCase() === 're-run';
    });
    function norm(value) { return String(value || '').toLowerCase().replace(/[^a-z0-9]/g, ''); }
    function findTool(card) {
      const title = card.querySelector('h2,h3,h4,[class*="font-semibold"]');
      const normalized = norm(title ? title.textContent : card.textContent);
      return usable.find(function (tool) {
        const id = norm(tool.id), name = norm(tool.name || tool.id);
        return normalized.includes(id) || normalized.includes(name) ||
          normalized.includes(id.replace(/\d+$/, '')) || normalized.includes(name.replace(/\d+$/, ''));
      }) || null;
    }
    let wiredCount = 0;
    runButtons.forEach(function (button) {
      const card = button.closest('.bg-surface-container-low.rounded-lg');
      if (!card) { setHidden(button, true); return; }
      const tool = findTool(card);
      if (!tool) { setHidden(card, true); return; }
      wiredCount += 1;
      const fakeStatus = Array.from(card.querySelectorAll('span')).find(function (span) {
        return /^(COMPLETED|RUNNING.*|QUEUED.*|READY)$/i.test((span.textContent || '').trim());
      });
      if (fakeStatus) fakeStatus.textContent = 'REGISTERED';
      card.querySelectorAll('.grid.grid-cols-3, .absolute.top-0').forEach(function (node) { setHidden(node, true); });
      card.querySelectorAll('span').forEach(function (span) {
        if (/PID:|services found|templates|req\/s|Candidates|Awaiting .* completion|Concurrency cap/i.test(span.textContent || '')) {
          const parent = span.closest('.grid, .bg-surface-container-lowest');
          if (parent) setHidden(parent, true); else setHidden(span, true);
        }
      });
      button.onclick = async function () {
        const target = targetInput && targetInput.value.trim();
        if (!target) { window.alert('Enter a target that is included in the configured scope.'); return; }
        button.disabled = true;
        if (output) output.textContent = 'Submitting ' + tool.id + ' against ' + target + '…';
        try {
          const result = await requestJson('/api/run', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({tool_id:tool.id, target:target})
          });
          selectedJob = result.job_id;
          const jobLabel = document.getElementById('job-id');
          if (jobLabel) jobLabel.textContent = selectedJob || '—';
          if (stream) stream.close();
          stream = new EventSource('/api/jobs/' + encodeURIComponent(selectedJob) + '/stream');
          stream.onmessage = function (event) {
            let message;
            try { message = JSON.parse(event.data); } catch (_) { return; }
            if (!output) return;
            if (message.type === 'line') {
              const line = document.createElement('div');
              line.className = 'whitespace-pre-wrap break-words';
              line.textContent = (message.stream ? '[' + message.stream + '] ' : '') + (message.text || message.line || '');
              output.appendChild(line);
              output.scrollTop = output.scrollHeight;
            } else if (message.type === 'status') {
              const line = document.createElement('div');
              line.textContent = 'Status: ' + (message.status || 'unknown');
              output.appendChild(line);
            } else if (message.type === 'finished' || message.type === 'failed') {
              const line = document.createElement('div');
              line.textContent = message.type === 'finished' ? 'Finished (exit ' + message.exit_code + ')' : 'Failed: ' + (message.error || 'unknown error');
              output.appendChild(line);
              stream.close(); stream = null; button.disabled = false;
            }
          };
          stream.onerror = function () { if (stream) { stream.close(); stream = null; } button.disabled = false; };
        } catch (error) {
          if (output) output.textContent = 'Run rejected: ' + error.message;
          button.disabled = false;
        }
      };
    });
    // Hide static tool cards and progress telemetry that are not backed by
    // an active WHAXON job. Only native per-tool Re-run cards with a matching
    // registered tool remain available.
    document.querySelectorAll('main section').forEach(function (section) {
      if (/Session Token/.test(section.textContent || '') && /SSE Socket/.test(section.textContent || '')) setHidden(section, true);
    });
    document.querySelectorAll('main .bg-surface-container-low.rounded-lg').forEach(function (card) {
      if (/Nuclei v|Nikto 2\.|sqlmap 1\.|Quick Trigger Utility Bar|whaxon:\/\/cli-pipeline/i.test(card.textContent || '')) {
        const hasNativeRun = Array.from(card.querySelectorAll('button')).some(function (button) {
          return (button.textContent || '').trim().toLowerCase() === 're-run';
        });
        if (!hasNativeRun) setHidden(card, true);
      }
    });
    // Use only controls that exist in the supplied design; do not inject a tool selector.
    ['run active pipeline','dispatch passive recon','inject payload','spawn sub-tool','emergency abort','engage replay','explore whatweb','gobuster','wpscan','execute','pause pipeline','pause','abort'].forEach(hideButtonByText);
    ['ai-planner-toggle','toggle-planner-gate'].forEach(function (id) {
      const control = document.getElementById(id);
      if (control) { const label = control.closest('label') || control.closest('div'); if (label) setHidden(label, true); else setHidden(control, true); }
    });
    const probeCheckbox = document.querySelector('input[type="checkbox"]:not(#ai-planner-toggle)');
    const probeGrid = probeCheckbox && probeCheckbox.closest('.grid');
    if (probeGrid) setHidden(probeGrid, true);
    if (!targetInput || wiredCount === 0) {
      runButtons.forEach(function (button) { setHidden(button, true); });
      if (output) output.textContent = 'No registered tool has a matching control in this design. No scan was started.';
    }
    document.querySelectorAll('button').forEach(function (button) {
      if (!(button.textContent || '').toLowerCase().includes('kill leader')) return;
      button.onclick = async function () {
        if (!selectedJob) { window.alert('There is no active WHAXON job to cancel.'); return; }
        try {
          const result = await requestJson('/api/jobs/' + encodeURIComponent(selectedJob) + '/cancel', {method:'POST'});
          if (output) output.appendChild(document.createTextNode('\\nCancellation requested: ' + String(result.ok)));
        } catch (error) { window.alert('Cancellation failed: ' + error.message); }
      };
    });
  }
  async function wireDashboard() {
    try {
      const values = await Promise.all([
        requestJson('/api/status'),
        requestJson('/api/history'),
        requestJson('/api/report?format=json'),
        requestJson('/api/tools'),
        requestJson('/api/msf/sessions').catch(function () { return {unavailable:true}; })
      ]);
      const statusData = values[0] || {};
      const history = Array.isArray(values[1]) ? values[1] : (values[1].jobs || values[1].history || []);
      const report = values[2] || {};
      const tools = Array.isArray(values[3]) ? values[3] : (values[3].tools || []);
      const sessions = values[4] || {};
      const findings = flattenFindings(report);
      const active = history.filter(function (job) { return /running|queued|active/i.test(String(job.status || '')); }).length;
      const verified = findings.filter(function (item) { return /verified/i.test(String(item.finding.verification_status || item.finding.status || '')); }).length;
      const candidate = findings.filter(function (item) { return /candidate|pending/i.test(String(item.finding.verification_status || item.finding.status || '')); }).length;
      const metrics = {
        'Active Scans':active,
        'Verified Findings':verified,
        'Candidate Findings':candidate,
        'Active Adapters':tools.filter(function (tool) { return !!tool.adapter_available; }).length
      };
      document.querySelectorAll('span').forEach(function (label) {
        const key = (label.textContent || '').trim();
        if (key === '0 Findings') label.textContent = findings.length + ' Findings';
        if (key === '0 Verified') label.textContent = verified + ' Verified';
        if (!(key in metrics)) return;
        const card = label.closest('.rounded-lg');
        const value = card && card.querySelector('.font-headline-lg');
        if (value) value.textContent = String(metrics[key]);
        if (key === 'PTES Coverage') { label.textContent = 'Coverage Gaps (10 Recent Jobs)'; label.title = unavailableCoverageCount + ' coverage lookup(s) unavailable'; }
      });
      const table = document.querySelector('table');
      const body = table && table.querySelector('tbody');
      if (body) {
        const headers = table.querySelectorAll('thead th');
        const labels = ['Job ID','Target','Operator','Timeline','Findings','Status','Actions'];
        headers.forEach(function (header, index) {
          if (labels[index]) header.textContent = labels[index];
          if (index === 2 || index === 6) setHidden(header, true);
        });
        body.replaceChildren();
        history.forEach(function (job) {
          const values = [
            job.id || job.job_id || '—',
            job.target || '—',
            '',
            [job.created_at || job.started_at || '', job.duration_s != null ? job.duration_s + 's' : ''].filter(Boolean).join(' · ') || '—',
            job.findings_count == null ? '—' : job.findings_count,
            job.status || '—',
            ''
          ];
          const tr = document.createElement('tr'); tr.className = 'border-b border-outline-variant/15 hover:bg-surface-container/50';
          for (let i = 0; i < headers.length; i++) {
            const td = document.createElement('td'); td.className = 'px-space-md py-space-sm font-code-sm';
            td.textContent = String(values[i] == null ? '—' : values[i]);
            if (i === 2 || i === 6) setHidden(td, true);
            tr.appendChild(td);
          }
          body.appendChild(tr);
        });
        if (!history.length) {
          const tr = document.createElement('tr'), td = document.createElement('td');
          td.colSpan = Math.max(1, headers.length); td.className = 'p-space-md text-outline'; td.textContent = 'No jobs recorded yet.';
          tr.appendChild(td); body.appendChild(tr);
        }
      }
      const remLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'Remediation Retest'; });
      if (remLabel) { const card = remLabel.closest('.rounded-lg'); if (card) setHidden(card, true); }
      const coverageLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'PTES Coverage'; });
      if (coverageLabel) { const card = coverageLabel.closest('.rounded-lg'); if (card) setHidden(card, true); }
      const sessionBufferLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'Active Session Buffer'; });
      if (sessionBufferLabel) { const bar = sessionBufferLabel.closest('.rounded-lg'); if (bar) setHidden(bar, true); }
      const falsePositiveLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return /FALSE POSITIVES/.test(el.textContent || ''); });
      if (falsePositiveLabel) {
        setHidden(falsePositiveLabel, true);
        const card = falsePositiveLabel.closest('.rounded-lg');
        const progress = card && card.querySelector('.mt-2.h-1');
        if (progress) setHidden(progress, true);
      }
      const roeLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'ROE SIGN-OFF'; });
      if (roeLabel) { const checklist = roeLabel.closest('.grid'); if (checklist) setHidden(checklist, true); }
      const activeScansLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'Active Scans'; });
      if (activeScansLabel) {
        const card = activeScansLabel.closest('.rounded-lg');
        const sublabel = card && Array.from(card.querySelectorAll('span')).find(function (el) { return /RUNNING/.test(el.textContent || ''); });
        if (sublabel) sublabel.textContent = active + ' RUNNING';
      }
      const adaptersLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'Active Adapters'; });
      if (adaptersLabel) {
        const card = adaptersLabel.closest('.rounded-lg');
        const sublabel = card && Array.from(card.querySelectorAll('span')).find(function (el) { return /PLUGINS READY/.test(el.textContent || ''); });
        if (sublabel) sublabel.textContent = 'ADAPTERS AVAILABLE';
      }
      const search = document.querySelector('input[placeholder*="Filter by ID"]');
      if (search && body) search.oninput = function () {
        const q = search.value.toLowerCase();
        body.querySelectorAll('tr').forEach(function (row) { setHidden(row, !row.textContent.toLowerCase().includes(q)); });
      };
      const sessionNote = Array.from(document.querySelectorAll('span,p')).find(function (el) { return /Awaiting Target Commit/.test(el.textContent || ''); });
      if (sessionNote) {
        if (sessions.unavailable) sessionNote.textContent = 'Session status unavailable';
        else sessionNote.textContent = sessions.live_count ? 'Live sessions reported by backend' : 'No active sessions reported';
      }
      const targetLabel = Array.from(document.querySelectorAll('span,p')).find(function (el) { return (el.textContent || '').trim() === 'Target: api.internal.corp'; });
      if (targetLabel) { setHidden(targetLabel, true); targetLabel.setAttribute('aria-hidden','true'); }
      const storageLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return /Storage:/.test(el.textContent || ''); });
      if (storageLabel) setHidden(storageLabel, true);
      document.querySelectorAll('span').forEach(function (el) { if (/CRYPTO LOG INTEGRITY|MERKLE_ROOT_VERIFIED/.test(el.textContent || '')) setHidden(el, true); });
      const historyFooter = Array.from(document.querySelectorAll('span')).find(function (el) { return /historical engagement logs/i.test(el.textContent || ''); });
      if (historyFooter) setHidden(historyFooter, true);
      hideButtonByText('deploy mock');
      hideButtonByText('configure filters');
      hideButtonByText('load workspace');
      hideButtonByText('audit pack');
      hideButtonByText('start new engagement');
      hideButtonByText('upload artifact');
      hideButtonByText('export archive');
      hideButtonByText('switch target session');
      hideButtonByText('update credentials');
      hideButtonByText('launch wizard');
      hideButtonByText('continue setup');
      hideButtonByText('inspect ledger');
      hideButtonByText('cli help');
      hideButtonByText('update credentials');
      hideButtonByText('launch wizard');
      hideButtonByText('continue setup');
      hideButtonByText('inspect ledger');
      hideButtonByText('cli help');
      // Report page wiring is dispatched only on its own route; do not alter the dashboard.
      const statusLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return (el.textContent || '').trim() === 'ENGINE STATUS'; });
      if (statusLabel && statusData.ok === false) statusLabel.textContent = 'ENGINE DEGRADED';
    } catch (error) {
      wireUnavailablePage();
    }
  }
  async function wireHistory() {
    try {
      const result = await requestJson('/api/history');
      const jobs = Array.isArray(result) ? result : (result.jobs || result.history || []);
      const table = document.querySelector('table');
      const body = table && table.querySelector('tbody');
      if (!body) return;
      const headers = table.querySelectorAll('thead th');
      if (headers.length >= 7) {
        ['Job ID / State','Tool','Target','Duration / Created'].forEach(function (label, index) { headers[index].textContent = label; });
        headers.forEach(function (header, index) { if (index >= 4) setHidden(header, true); });
      }
      body.replaceChildren();
      jobs.forEach(function (job) {
        const tr = document.createElement('tr'); tr.className = 'border-b border-outline-variant/15 hover:bg-surface-container/50';
        const id = job.id || job.job_id || '—';
        const tool = job.tool || job.tool_id || '—';
        const target = job.target || '—';
        const created = job.created_at || job.started_at || job.finished_at || '';
        const duration = job.duration_s != null ? job.duration_s + 's' : '';
        tr.dataset.id = String(id); tr.dataset.tool = String(tool).toLowerCase(); tr.dataset.target = String(target).toLowerCase();
        tr.dataset.status = String(job.status || '').toLowerCase(); tr.dataset.created = String(created);
        [String(id) + ' · ' + String(job.status || 'unknown'), tool, target, [duration, created].filter(Boolean).join(' · ') || '—'].forEach(function (value) {
          const td = document.createElement('td'); td.className = 'px-space-md py-space-sm font-code-sm text-code-sm'; td.textContent = String(value); tr.appendChild(td);
        });
        body.appendChild(tr);
      });
      if (!jobs.length) {
        const tr = document.createElement('tr'), td = document.createElement('td');
        td.colSpan = Math.max(1, headers.length); td.className = 'p-space-md text-outline'; td.textContent = 'No jobs recorded yet.';
        tr.appendChild(td); body.appendChild(tr);
      }
      const search = document.querySelector('input[placeholder*="Filter by job ID"]');
      const selects = Array.from(document.querySelectorAll('select'));
      const toolFilter = selects[0], timeFilter = selects[1], modeFilter = selects[2];
      if (toolFilter) {
        const tools = Array.from(new Set(jobs.map(function (job) { return job.tool || job.tool_id; }).filter(Boolean))).sort();
        toolFilter.replaceChildren();
        const all = document.createElement('option'); all.value = 'all'; all.textContent = 'All Tools'; toolFilter.appendChild(all);
        tools.forEach(function (tool) {
          const option = document.createElement('option'); option.value = tool; option.textContent = tool + ' (' + jobs.filter(function (job) { return (job.tool || job.tool_id) === tool; }).length + ')'; toolFilter.appendChild(option);
        });
      }
      if (modeFilter) { const wrapper = modeFilter.closest('div'); if (wrapper) setHidden(wrapper, true); else setHidden(modeFilter, true); }
      function applyFilters() {
        const q = search ? search.value.toLowerCase() : '';
        const selectedTool = toolFilter ? toolFilter.value : 'all';
        const range = timeFilter ? timeFilter.value : 'all';
        const age = range === '24h' ? 24*60*60*1000 : range === '7d' ? 7*24*60*60*1000 : range === '30d' ? 30*24*60*60*1000 : 0;
        body.querySelectorAll('tr').forEach(function (tr) {
          const raw = tr.dataset.created;
          let stamp = Date.parse(raw);
          if (raw && Number.isFinite(Number(raw))) { const numeric = Number(raw); stamp = numeric > 1e12 ? numeric : numeric * 1000; }
          const tooOld = age > 0 && Number.isFinite(stamp) && stamp > 0 && (Date.now() - stamp > age);
          setHidden(tr, !tr.textContent.toLowerCase().includes(q) ||
            (selectedTool !== 'all' && tr.dataset.tool !== selectedTool.toLowerCase()) || tooOld);
        });
      }
      if (search) search.oninput = applyFilters;
      if (toolFilter) toolFilter.onchange = applyFilters;
      if (timeFilter) timeFilter.onchange = applyFilters;
      applyFilters();
      hideButtonByText('verify integrity');
      hideButtonByText('export ledger');
      hideButtonByText('all (42)');
      hideButtonByText('success (38)');
      hideButtonByText('failed (3)');
      hideButtonByText('scope-blocked (1)');
      hideButtonByText('active / queued (0)');
      document.querySelectorAll('span').forEach(function (el) {
        if (/MERKLE_ROOT_VERIFIED|INTEGRITY VERIFIED|HASH MATCH|CRYPTO LOG INTEGRITY/i.test(el.textContent || '')) setHidden(el, true);
      });
      const summaryLabel = Array.from(document.querySelectorAll('span')).find(function (el) { return /historical engagement logs/i.test(el.textContent || ''); });
      if (summaryLabel) setHidden(summaryLabel, true);
    } catch (error) {
      wireUnavailablePage();
    }
  }
  async function wireCatalog() {
    try {
      const result = await requestJson('/api/tools');
      const tools = Array.isArray(result) ? result : (result.tools || []);
      const matrix = document.getElementById('adapter-matrix');
      if (matrix) {
        matrix.replaceChildren();
        tools.forEach(function (tool) {
          const card = document.createElement('div');
          card.className = 'adapter-card p-space-md bg-surface-container-low hover:bg-surface-container rounded shadow-sm transition-all flex flex-col gap-space-sm border border-outline-variant/20';
          card.dataset.search = [tool.id, tool.name, tool.category, tool.binary, tool.description].filter(Boolean).join(' ').toLowerCase();
          card.dataset.status = tool.available === false || !tool.binary ? 'missing' : 'available';
          card.dataset.category = String(tool.category || '').toLowerCase();
          const header = document.createElement('div'); header.className = 'flex items-start justify-between gap-space-sm';
          const name = document.createElement('span'); name.className = 'font-code-sm text-on-surface font-semibold'; name.textContent = tool.name || tool.id;
          const unavailable = tool.available === false || !tool.binary;
          const state = document.createElement('span'); state.className = 'font-label-sm text-label-sm ' + (unavailable ? 'text-error' : 'text-primary'); state.textContent = unavailable ? 'UNAVAILABLE' : 'REGISTERED';
          header.append(name, state);
          const id = document.createElement('div'); id.className = 'font-code-sm text-secondary'; id.textContent = tool.id || '';
          const detail = document.createElement('p'); detail.className = 'font-body-sm text-body-sm text-on-surface-variant'; detail.textContent = tool.description || tool.category || 'No description provided by catalog.';
          const meta = document.createElement('div'); meta.className = 'flex flex-wrap gap-space-sm font-code-sm text-outline';
          const binary = document.createElement('span'); binary.textContent = 'Binary: ' + (tool.binary || 'not specified');
          const adapter = document.createElement('span'); adapter.textContent = 'Adapter: ' + (tool.adapter_available ? 'available' : 'not available');
          meta.append(binary, adapter); card.append(header, id, detail, meta); matrix.appendChild(card);
        });
        const search = document.getElementById('adapter-search');
        const filter = document.getElementById('status-select');
        if (filter) {
          const availableCount = tools.filter(function (tool) { return tool.available !== false && !!tool.binary; }).length;
          const missingCount = tools.length - availableCount;
          Array.from(filter.options).forEach(function (option) {
            if (option.value === 'binary_found') option.textContent = 'Available (' + availableCount + ')';
            if (option.value === 'missing') option.textContent = 'Unavailable (' + missingCount + ')';
            if (option.value === 'untrusted') setHidden(option, true);
          });
        }
        let selectedCategory = 'all';
        function categoryMatches(category, key) {
          if (key === 'all') return true;
          if (key === 'recon') return /recon|discovery|enumerat/i.test(category);
          if (key === 'vulnerability') return /vuln|scan|web/i.test(category);
          if (key === 'exploitation') return /exploit|attack|post/i.test(category);
          if (key === 'ingestion') return /ingest|import|parse|burp/i.test(category);
          return false;
        }
        const categoryButtons = Array.from(document.querySelectorAll('button')).map(function (button) {
          const match = (button.textContent || '').trim().match(/^(All|Recon|Vulnerability|Exploitation|Ingestion)\s*\(\d+\)/i);
          return match ? {button:button,key:match[1].toLowerCase()} : null;
        }).filter(Boolean);
        categoryButtons.forEach(function (entry) {
          const count = entry.key === 'all' ? tools.length : tools.filter(function (tool) { return categoryMatches(String(tool.category || '').toLowerCase(), entry.key); }).length;
          entry.button.textContent = entry.key.charAt(0).toUpperCase() + entry.key.slice(1) + ' (' + count + ')';
          setHidden(entry.button, count === 0 && entry.key !== 'all');
          entry.button.onclick = function () { selectedCategory = entry.key; applyFilter(); };
        });
        function applyFilter() {
          const query = search ? search.value.toLowerCase() : '';
          const state = filter ? filter.value : 'all';
          matrix.querySelectorAll('.adapter-card').forEach(function (card) {
            setHidden(card, !card.dataset.search.includes(query) ||
              (state === 'missing' && card.dataset.status !== 'missing') ||
              (state === 'binary_found' && card.dataset.status !== 'available') ||
              !categoryMatches(card.dataset.category, selectedCategory));
          });
        }
        if (search) search.oninput = applyFilter;
        if (filter) filter.onchange = applyFilter;
        applyFilter();
      }
      hideButtonByText('sync upstream');
      hideButtonByText('reload catalog');
      hideButtonByText('register adapter');
      hideButtonByText('mock test');
      hideButtonByText('re-sign');
      hideButtonByText('save configuration');
      document.querySelectorAll('button').forEach(function (button) {
        if ((button.textContent || '').trim().toLowerCase().startsWith('configure')) setHidden(button, true);
      });
      ['btn-sync','btn-reload','btn-register','btn-mock-test','btn-resign','btn-save-conf'].forEach(function (id) {
        const button = document.getElementById(id);
        if (button) { setHidden(button, true); button.setAttribute('aria-hidden', 'true'); }
      });
    } catch (error) {
      wireUnavailablePage();
    }
  }
  async function wireRetest() {
    const search = document.querySelector('input[placeholder*="Filter Finding"]');
    const queue = Array.from(document.querySelectorAll('div')).find(function (element) {
      return element.classList.contains('max-h-[820px]') && element.classList.contains('overflow-y-auto');
    });
    if (!queue || !queue.firstElementChild) { wireUnavailablePage(); return; }
    const template = queue.firstElementChild.cloneNode(true);
    let rows = [], selected = null;
    try {
      const report = await requestJson('/api/report?format=json');
      rows = flattenFindings(report).filter(function (item) {
        return item.job && (item.job.id || item.job.job_id) && item.finding && item.finding.seq != null;
      });
    } catch (_) { wireUnavailablePage(); return; }
    if (!rows.length) { wireUnavailablePage(); return; }
    queue.replaceChildren();
    const entries = [];
    rows.forEach(function (item) {
      const job = item.job, finding = item.finding;
      const card = template.cloneNode(true);
      setHidden(card, false);
      card.dataset.jobId = String(job.id || job.job_id);
      card.dataset.seq = String(finding.seq);
      card.dataset.status = String(finding.verification_status || 'candidate').toLowerCase();
      const id = card.querySelector('.font-code-md');
      if (id) id.textContent = card.dataset.jobId + ':' + card.dataset.seq;
      Array.from(card.querySelectorAll('span')).forEach(function (span) {
        const value = (span.textContent || '').trim();
        if (/^PRIOR:/i.test(value)) span.textContent = 'PRIOR: ' + status(finding.verification_status);
        if (/^AUTHOR:/i.test(value)) span.textContent = 'SOURCE: ' + String(finding.source || 'unknown');
        if (/STILL_VULNERABLE|FIXED|INCONCLUSIVE/i.test(value)) span.textContent = status(finding.verification_status);
      });
      const title = card.querySelector('.font-body-md');
      if (title) title.textContent = String(finding.title || finding.kind || 'Finding');
      const target = card.querySelector('.font-code-sm.text-secondary');
      if (target) target.textContent = String(finding.url || finding.endpoint || finding.target || job.target || 'Target not recorded');
      const reasonBlock = card.querySelector('.mt-1.p-space-xs');
      if (reasonBlock) {
        const reasonLabels = reasonBlock.querySelectorAll('span');
        const reason = finding.verification_reason || finding.reason || 'No verification reason recorded';
        if (reasonLabels.length) reasonLabels[reasonLabels.length - 1].textContent = String(reason);
      }
      card.querySelectorAll('span, p').forEach(function (element) {
        if (/Median-of-3|pg_sleep\(5\)|Jitter Rejection|Audit C-01|HASH ATTESTED|5,042ms|Δ \+5,009ms/i.test(element.textContent || '')) setHidden(element, true);
      });
      card.addEventListener('click', function () {
        selected = item;
        entries.forEach(function (entry) {
          entry.card.classList.remove('border-primary','border-error/50','shadow-[0_0_14px_rgba(239,68,68,0.15)]');
        });
        card.classList.add('border-primary');
      });
      queue.appendChild(card);
      entries.push({card:card,item:item});
    });
    selected = rows[0];
    if (entries[0]) entries[0].card.click();
    if (search) search.oninput = function () {
      const q = search.value.toLowerCase();
      entries.forEach(function (entry) { setHidden(entry.card, !entry.card.textContent.toLowerCase().includes(q)); });
    };
    // This backend exposes single-finding validate/retest, not the design's
    // claimed 3x timing protocol or cryptographic three-way verdict ledger.
    ['BATCH REPLAY','RE-EXECUTE IMMEDIATE PROBE','COMMIT 3-WAY VERDICT TO AUDIT LEDGER','FILTER BY 3-WAY VERDICT'].forEach(hideButtonByText);
    const replayButton = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /Re-Execute Replay/i.test(button.textContent || '');
    });
    if (replayButton) {
      const label = replayButton.querySelector('span:last-child');
      if (label) label.textContent = 'Validate / Retest Selected';
      replayButton.onclick = async function () {
        if (!selected) { window.alert('Select a recorded finding first.'); return; }
        const jobId = selected.job.id || selected.job.job_id;
        const finding = selected.finding;
        const action = String(finding.verification_status || '').toLowerCase() === 'verified' ? 'retest' : 'validate';
        replayButton.disabled = true;
        try {
          const result = await requestJson('/api/' + action + '/' + encodeURIComponent(jobId) + '/' + encodeURIComponent(finding.seq), {method:'POST'});
          window.alert(action + ': ' + (result.status || 'completed') + (result.reason ? '\n' + result.reason : ''));
          window.location.reload();
        } catch (error) { window.alert(action + ' failed: ' + error.message); }
        finally { replayButton.disabled = false; }
      };
    }
    const exportButton = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /EXPORT PROOF AUDIT JSON/i.test(button.textContent || '');
    });
    if (exportButton) exportButton.onclick = function () {
      if (!selected) { window.alert('Select a recorded finding first.'); return; }
      window.location.assign('/api/jobs/' + encodeURIComponent(selected.job.id || selected.job.job_id) + '/findings.json');
    };
    document.querySelectorAll('main .bg-surface-container-low.rounded-xl').forEach(function (element) {
      if (/Status: FIXED|HASH ATTESTED|Status: STILL_VULNERABLE|ACTIVE TARGETS/i.test(element.textContent || '') &&
          !element.querySelector('button')) setHidden(element, true);
    });
    document.querySelectorAll('main span, main p').forEach(function (element) {
      if (/ENG-2026-X892|api\.internal\.corp|Median-of-3 pg_sleep|FINDING-SQLI-001|FINDING-XSS-004|FINDING-BOLA-009/i.test(element.textContent || '')) setHidden(element, true);
    });
  }
  async function wireAttackSurface() {
    let tree;
    try { tree = await requestJson('/api/tree?limit=50'); }
    catch (_) { wireUnavailablePage(); return; }
    const targets = Array.isArray(tree.targets) ? tree.targets : [];
    const container = document.getElementById('asset-ledger-container');
    const original = container && container.querySelector('article.asset-card');
    if (!container || !original || !targets.length) { wireUnavailablePage(); return; }

    const template = original.cloneNode(true);
    container.replaceChildren();
    const rank = {critical:5, high:4, medium:3, low:2, info:1};
    targets.forEach(function (record) {
      const card = template.cloneNode(true);
      setHidden(card, false);
      const findings = Array.isArray(record.findings) ? record.findings : [];
      const highest = findings.reduce(function (current, finding) {
        const value = String(finding.severity || 'info').toLowerCase();
        return (rank[value] || 0) > (rank[current] || 0) ? value : current;
      }, 'info');
      card.dataset.status = highest;
      card.dataset.provider = 'recorded';
      const title = card.querySelector('.font-code-lg.text-code-lg.font-bold');
      if (title) title.textContent = String(record.target || 'Target not recorded');
      const header = card.querySelector('.flex.items-center.gap-space-sm.flex-wrap');
      if (header) {
        const badge = Array.from(header.querySelectorAll('span')).find(function (span) {
          return /SEV:|CRITICAL EXPOSURE|SHADOW API DETECTED/i.test(span.textContent || '');
        });
        if (badge && findings.length) badge.textContent = 'SEVERITY: ' + highest.toUpperCase();
        else if (badge) setHidden(badge, true);
        Array.from(header.querySelectorAll('span')).forEach(function (span) {
          if (span === title || span === badge || span.classList.contains('material-symbols-outlined')) return;
          setHidden(span, true);
        });
      }
      const metadata = card.querySelector('.mt-space-xs.font-body-sm');
      if (metadata) metadata.textContent = String(record.job_count || (record.jobs || []).length || 0) +
        ' recorded jobs · ' + String(record.finding_count || findings.length || 0) + ' recorded findings';
      const actions = card.querySelectorAll('button');
      actions.forEach(function (button) { setHidden(button, true); });
      const drawer = card.querySelector('.bg-surface-container-lowest.p-space-sm.rounded');
      if (drawer) {
        drawer.textContent = 'Recorded target · ' + String(record.job_count || (record.jobs || []).length || 0) +
          ' jobs · ' + String(record.finding_count || findings.length || 0) + ' findings';
      }
      container.appendChild(card);
    });

    // This backend records targets seen in jobs; it does not run a continuous
    // asset monitor. Keep the original ledger, but suppress the demo telemetry
    // and actions that imply cloud discovery, drift detection, or remediation.
    document.querySelectorAll('main section').forEach(function (section) {
      if (!section.contains(container) && !/ATTACK SURFACE & CONTINUOUS MONITORING/i.test(section.textContent || '')) {
        setHidden(section, true);
      }
    });
    const daemonStatus = Array.from(document.querySelectorAll('main span')).find(function (element) {
      return /DAEMON: HOURLY SYNCHRONOUS SCAN ACTIVE/i.test(element.textContent || '');
    });
    if (daemonStatus) {
      const daemonPill = daemonStatus.closest('div.flex.items-center.gap-space-xs.bg-surface-container-high');
      setHidden(daemonPill || daemonStatus, true);
    }
    const timingStatus = Array.from(document.querySelectorAll('main div')).find(function (element) {
      return element.classList.contains('bg-surface-container-low') &&
        /LAST RUN:/.test(element.textContent || '') && /NEXT SYNC:/.test(element.textContent || '');
    });
    if (timingStatus) setHidden(timingStatus, true);
    document.querySelectorAll('main span, main p, main strong').forEach(function (element) {
      const value = (element.textContent || '').trim();
      if (/DAEMON: HOURLY SYNCHRONOUS SCAN ACTIVE|LAST RUN:|NEXT SYNC:|^14m ago$|^46m$|142 of 142 Assets Active|Critical Root Risk Path Active|SYN-ACK received|0 new hosts found|assets-backup-archive\.s3\.amazonaws\.com|api\.staging\.internal|54\.210\.42\.19/i.test(value)) {
        setHidden(element, true);
      }
    });
    ['configure cloud & dns probes','trigger delta recon now','enforce scope lock','launch nuclei probe',
     'auto-remediate acl','audit objects','trigger acme renew','harden ciphers','session shell',
     'expand canvas','stream full cryptographic audit logs','terminal log','emergency halt scan'].forEach(hideButtonByText);
    document.querySelectorAll('main .status-tab').forEach(function (button) {
      if (button.dataset.status !== 'all') setHidden(button, true);
      else button.textContent = 'ALL (' + targets.length + ')';
    });
    const search = document.getElementById('asset-search-input');
    if (search) search.oninput = function () {
      const query = search.value.toLowerCase().trim();
      container.querySelectorAll('article.asset-card').forEach(function (card) {
        setHidden(card, !card.textContent.toLowerCase().includes(query));
      });
    };
    const sort = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /SEVERITY DESC/i.test(button.textContent || '');
    });
    if (sort) setHidden(sort, true);
  }
  async function wireAiApprovals() {
    const modal = document.getElementById('approvals-modal');
    if (!modal) { wireUnavailablePage(); return; }
    setHidden(modal, true);
    await wireFindings();
    const main = document.querySelector('main');
    const firstCard = document.getElementById('finding-card-1');
    if (firstCard && !firstCard.hidden) firstCard.click();
    const sendButton = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /Send to Approvals/i.test(button.textContent || '');
    });
    const title = modal.querySelector('h3');
    const description = modal.querySelector('.border-b p');
    const body = modal.querySelector('.p-space-xl.overflow-y-auto');
    const refute = Array.from(modal.querySelectorAll('button')).find(function (button) {
      return /Refute \/ False Positive/i.test(button.textContent || '');
    });
    const hold = Array.from(modal.querySelectorAll('button')).find(function (button) {
      return /Hold for Retest/i.test(button.textContent || '');
    });
    const skip = Array.from(modal.querySelectorAll('button')).find(function (button) {
      return /Skip Item/i.test(button.textContent || '');
    });
    const approve = Array.from(modal.querySelectorAll('button')).find(function (button) {
      return /Approve as Verified/i.test(button.textContent || '');
    });
    const close = modal.querySelector('button[onclick*="approvals-modal"]');
    if (body) setHidden(body, true);
    [hold, skip, approve].forEach(function (button) { if (button) setHidden(button, true); });
    const remaining = Array.from(modal.querySelectorAll('span')).find(function (span) {
      return /Remaining in queue:/i.test(span.textContent || '');
    });
    if (remaining && remaining.parentElement) setHidden(remaining.parentElement, true);
    modal.querySelectorAll('span, p').forEach(function (element) {
      if (/CND-9402|11 CANDIDATES PENDING|QUEUE GATED: STRICT|OP\/\/7749-ALPHA|Awaiting Review for|Item 1 of 11/i.test(element.textContent || '')) setHidden(element, true);
    });
    if (sendButton) {
      setHidden(sendButton, false);
      sendButton.onclick = function () {
        const selected = window.__whaxonSelectedFinding;
        if (!selected || !selected.jobId || selected.seq == null) {
          window.alert('Select a recorded finding before opening review.'); return;
        }
        if (title) title.textContent = 'Manual Review — ' + String(selected.finding.title || selected.finding.kind || 'Finding');
        if (description) description.textContent = String(selected.finding.raw_line || selected.finding.reason || 'Review the recorded finding evidence before resolving it.');
        setHidden(modal, false);
      };
    }
    if (close) close.onclick = function () { setHidden(modal, true); };
    if (refute) refute.onclick = async function () {
      const selected = window.__whaxonSelectedFinding;
      if (!selected || !selected.jobId || selected.seq == null) {
        window.alert('Select a recorded finding first.'); return;
      }
      refute.disabled = true;
      try {
        await requestJson('/api/approvals/' + encodeURIComponent(selected.jobId) + '/' + encodeURIComponent(selected.seq) + '/resolve', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body:JSON.stringify({status:'refuted', user:'human'})
        });
        setHidden(modal, true);
        window.location.reload();
      } catch (error) {
        window.alert('Finding resolution failed: ' + error.message);
        refute.disabled = false;
      }
    };
  }
  async function wireAiStrategyGate() {
    let pending = [];
    try {
      const result = await requestJson('/api/ai/pending');
      pending = Array.isArray(result) ? result : (result.pending || result.runs || []);
    } catch (_) { wireUnavailablePage(); return; }
    if (!pending.length) { wireUnavailablePage(); return; }
    const current = pending[0];
    const runId = current.id || current.run_id;
    if (!runId) { wireUnavailablePage(); return; }
    const main = document.querySelector('main');
    const heading = main && main.querySelector('h1,h2,h3');
    let authorize = document.getElementById('btn-authorize');
    let reject = document.getElementById('btn-reject');
    if (!main || !heading || !authorize || !reject) { wireUnavailablePage(); return; }
    // Clone the native controls to remove the source file's demo listeners
    // (including its fake dispatch alert and timeout-based "EXECUTED" state).
    authorize = authorize.cloneNode(true); document.getElementById('btn-authorize').replaceWith(authorize);
    reject = reject.cloneNode(true); document.getElementById('btn-reject').replaceWith(reject);
    heading.textContent = String(current.goal || 'Pending AI action');
    const question = current.pending_question;
    const questionText = typeof question === 'string' ? question :
      (question && (question.question || question.prompt)) || '';
    const promptText = Array.from(main.querySelectorAll('p')).find(function (p) {
      return /Execution halted by Kernel Enforcement|sign-off required/i.test(p.textContent || '');
    });
    if (promptText) promptText.textContent = String(questionText || 'This AI run is waiting for an operator decision.');
    const authorizeLabel = authorize.querySelector('.font-label-md');
    const rejectLabel = reject.querySelector('.font-label-md');
    if (authorizeLabel) authorizeLabel.textContent = 'Approve Pending Step';
    if (rejectLabel) rejectLabel.textContent = 'Reject Pending Step';
    // Only the existing proposal header and decision controls remain visible;
    // static reasoning, target telemetry and session history are demo content.
    const activeSection = heading.closest('section');
    main.querySelectorAll('section').forEach(function (section) {
      if (section !== activeSection && !section.contains(heading) && !section.contains(authorize) && !section.contains(reject)) setHidden(section, true);
    });
    main.querySelectorAll('span, p, div').forEach(function (element) {
      const value = (element.textContent || '').trim();
      if (/ENG-2026-X892|api\.internal\.corp|OP\/\/7749-ALPHA|CVE-2023-38606|TARGET STABILITY|SCOPE DRIFT|PAYLOAD NOISE|85\.0% Exceeded|Confidence Score/i.test(value)) {
        const container = element.closest('.bg-surface-container-lowest, .bg-surface-container-low.rounded-xl');
        if (container && !container.contains(heading) && !container.contains(authorize) && !container.contains(reject)) setHidden(container, true);
        else if (!container) setHidden(element, true);
      }
    });
    async function answer(answer) {
      authorize.disabled = true; reject.disabled = true;
      try {
        await requestJson('/api/ai/runs/' + encodeURIComponent(runId) + '/answer', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body:JSON.stringify({answer:answer, note:'Decision submitted through WHAXON UI'})
        });
        window.location.reload();
      } catch (error) {
        window.alert('Could not submit the AI approval decision: ' + error.message);
        authorize.disabled = false; reject.disabled = false;
      }
    }
    authorize.onclick = function (event) { event.preventDefault(); answer('approve'); };
    reject.onclick = function (event) { event.preventDefault(); answer('reject'); };
    window.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') { event.preventDefault(); event.stopImmediatePropagation(); authorize.click(); }
      if (event.key === 'Escape') { event.preventDefault(); event.stopImmediatePropagation(); reject.click(); }
    }, true);
  }
  async function wireHealth() {
    const runButton = document.getElementById('btn-run-diag');
    const exportButton = document.getElementById('btn-export-json');
    const stream = document.getElementById('diagnostic-stream');
    const coreGrid = document.getElementById('cores-grid');
    if (coreGrid) setHidden(coreGrid, true);
    const restart = document.getElementById('btn-restart-daemons');
    if (restart) { setHidden(restart, true); restart.setAttribute('aria-hidden', 'true'); }
    ['Test MSF RPC Handshake','Benchmark SQLite Write Speed','Probe Ollama LLM Socket','Check eBPF Filter Integrity'].forEach(hideButtonByText);
    document.querySelectorAll('main button').forEach(function (button) {
      if (/^(PING|TEST|INSPECT|PROBE|CHECK)$/i.test((button.textContent || '').trim())) setHidden(button, true);
    });
    async function loadHealth() {
      const results = await Promise.all([
        requestJson('/api/health').catch(function (error) { return {error:error.message}; }),
        requestJson('/api/health/simple').catch(function (error) { return {error:error.message}; }),
        requestJson('/api/status').catch(function (error) { return {error:error.message}; })
      ]);
      const data = {readiness:results[0], capabilities:results[1], status:results[2]};
      if (stream) stream.textContent = JSON.stringify(data, null, 2);
      return data;
    }
    if (runButton) runButton.onclick = async function () {
      runButton.disabled = true;
      if (stream) stream.textContent = 'Running supported health checks…';
      try { await loadHealth(); }
      catch (error) { if (stream) stream.textContent = 'Health checks failed: ' + error.message; }
      finally { runButton.disabled = false; }
    };
    if (exportButton) exportButton.onclick = async function () {
      exportButton.disabled = true;
      try {
        const data = await loadHealth();
        const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url; link.download = 'whaxon-health.json';
        document.body.appendChild(link); link.click(); link.remove();
        URL.revokeObjectURL(url);
      } catch (error) {
        window.alert('Health report export failed: ' + error.message);
      } finally { exportButton.disabled = false; }
    };
    try { await loadHealth(); }
    catch (error) { if (stream) stream.textContent = 'Health checks failed: ' + error.message; }
  }
  async function wireEvidence() {
    let jobs = [];
    try {
      const history = await requestJson('/api/history');
      jobs = Array.isArray(history) ? history : (history.jobs || history.history || []);
    } catch (_) { wireUnavailablePage(); return; }
    let selectedJob = null, evidence = [];
    for (const job of jobs.slice(0, 20)) {
      const id = job && (job.id || job.job_id);
      if (!id) continue;
      try {
        const items = await requestJson('/api/jobs/' + encodeURIComponent(id) + '/evidence');
        if (Array.isArray(items) && items.length) { selectedJob = String(id); evidence = items; break; }
      } catch (_) {}
    }
    // The supplied evidence design contains sample artifacts and sample hashes.
    // If this installation has no real evidence, hide the page rather than
    // presenting those samples as recorded engagement data.
    if (!selectedJob || !evidence.length) { wireUnavailablePage(); return; }
    const tree = Array.from(document.querySelectorAll('div')).find(function (element) {
      return element.classList.contains('max-h-[460px]') && element.classList.contains('overflow-y-auto');
    });
    if (!tree) { wireUnavailablePage(); return; }
    const firstCategory = tree.firstElementChild;
    const headerTemplate = firstCategory && firstCategory.firstElementChild;
    const selectedTemplate = tree.querySelector('.bg-surface-container-high.shadow-xs');
    const rowTemplate = selectedTemplate || tree.querySelector('.group');
    if (!headerTemplate || !rowTemplate) { wireUnavailablePage(); return; }
    const header = headerTemplate.cloneNode(true);
    const headerLabels = header.querySelectorAll('span');
    Array.from(headerLabels).forEach(function (span) {
      if (/Reconnaissance|Evidence|Proof|Loot/i.test(span.textContent || '')) span.textContent = 'Recorded Evidence';
      else if (/^\d+$/.test((span.textContent || '').trim())) span.textContent = String(evidence.length);
    });
    tree.replaceChildren(header);
    const rows = [];
    let selected = evidence[0];
    function selectItem(item, row) {
      selected = item;
      rows.forEach(function (entry) {
        entry.row.classList.remove('bg-surface-container-high','shadow-xs');
        entry.row.classList.add('hover:bg-surface-container-high/60');
      });
      row.classList.add('bg-surface-container-high','shadow-xs');
      row.classList.remove('hover:bg-surface-container-high/60');
    }
    evidence.forEach(function (item) {
      const row = rowTemplate.cloneNode(true);
      row.className = 'flex items-center gap-1.5 px-2 py-1.5 rounded hover:bg-surface-container-high/60 cursor-pointer transition-colors group';
      const labels = Array.from(row.querySelectorAll('span'));
      const filename = String(item.name || item.path || ('evidence-' + item.seq));
      const nameLabel = labels.find(function (span) { return /raw_nmap_syn_scan\.xml|subfinder_enum\.json|amass_active_intel\.txt|sqlmap_session_dump\.sqlite|burp_traffic_proxy_stream\.pcap/i.test(span.textContent || ''); }) || labels.find(function (span) { return !(span.textContent || '').trim().match(/^(description|data_object|notes|SELECTED)$/i); });
      if (nameLabel) nameLabel.textContent = filename;
      labels.forEach(function (span) {
        if ((span.textContent || '').trim() === 'SELECTED') setHidden(span, true);
      });
      const meta = labels[labels.length - 1];
      if (meta) meta.textContent = [item.kind || 'evidence', item.added_at || ''].filter(Boolean).join(' • ');
      row.addEventListener('click', function () { selectItem(item, row); });
      tree.appendChild(row);
      rows.push({item:item,row:row});
    });
    selectItem(selected, rows[0].row);
    const search = document.querySelector('input[placeholder*="Search filename"]');
    if (search) search.oninput = function () {
      const q = search.value.toLowerCase();
      rows.forEach(function (entry) { setHidden(entry.row, !entry.row.textContent.toLowerCase().includes(q)); });
    };
    const download = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /Download Raw/i.test(button.textContent || '');
    });
    if (download) download.onclick = function () {
      if (!selected || selected.seq == null) { window.alert('Select a recorded evidence item first.'); return; }
      window.location.assign('/api/jobs/' + encodeURIComponent(selectedJob) + '/evidence/' + encodeURIComponent(selected.seq) + '/download');
    };
    ['Sync Merkle Tree','Export TAR.GZ','Verify SHA-256 Hash','Re-parse into Finding Model','Send to Issue Tracker','Trace Proof'].forEach(hideButtonByText);
    // Hide the sample inspector/KPI pane; this build exposes the real evidence
    // ledger and raw-download action only, not fabricated XML, port, or hash data.
    const layout = tree.parentElement && tree.parentElement.parentElement;
    if (layout && layout.children.length > 1) {
      Array.from(layout.children).forEach(function (child) { if (!child.contains(tree)) setHidden(child, true); });
    }
    document.querySelectorAll('main .grid').forEach(function (grid) {
      if (/Stored Artifacts|128\.4 MB|1,842,912|840 KB/i.test(grid.textContent || '')) setHidden(grid, true);
    });
  }
  async function wireChains() {
    let graph;
    try { graph = await requestJson('/api/pivot/graph'); }
    catch (_) { wireUnavailablePage(); return; }
    const edges = Array.isArray(graph.edges) ? graph.edges : [];
    if (!edges.length) { wireUnavailablePage(); return; }
    const cards = Array.from(document.querySelectorAll('main .bg-surface-container.rounded-xl.p-space-md.shadow-sm'));
    const template = cards.find(function (card) {
      return /SQL Injection|Postgres Remote Code Execution|Tenant IDOR/i.test(card.textContent || '');
    });
    if (!template || !template.parentElement) { wireUnavailablePage(); return; }
    const container = template.parentElement;
    const cardSelector = function (element) {
      return element.classList.contains('bg-surface-container') &&
        element.classList.contains('rounded-xl') && element.classList.contains('p-space-md') &&
        element.classList.contains('shadow-sm');
    };
    const directCards = Array.from(container.children).filter(cardSelector);
    const insertBefore = directCards[0] || null;
    directCards.forEach(function (card) { card.remove(); });
    function describe(node) { return String((node && node.kind) || 'node') + ':' + String((node && node.id) || 'unknown'); }
    edges.forEach(function (edge, index) {
      const card = template.cloneNode(true);
      setHidden(card, false);
      const badge = card.querySelector('.w-6.h-6');
      if (badge) badge.textContent = String(index + 1);
      const heading = Array.from(card.querySelectorAll('span')).find(function (span) {
        return span.classList.contains('font-code-md') && !/^\d+$/.test((span.textContent || '').trim());
      });
      if (heading) heading.textContent = describe(edge.parent) + ' → ' + describe(edge.child);
      const statusBadge = Array.from(card.querySelectorAll('span')).find(function (span) {
        return /LETHAL COMPROMISE|LATERAL MOVEMENT|INITIAL ACCESS|PRIVILEGE ESCALATION|PIVOT/i.test(span.textContent || '');
      });
      if (statusBadge) statusBadge.textContent = String(edge.relation || 'linked').replace(/_/g, ' ').toUpperCase();
      const paragraph = card.querySelector('p');
      if (paragraph) paragraph.textContent = edge.evidence ? String(edge.evidence) : 'No evidence note is recorded for this relationship.';
      const code = card.querySelector('.font-code-sm');
      if (code) code.textContent = describe(edge.parent) + ' → ' + describe(edge.child);
      const codeBlock = card.querySelector('.bg-surface-container-lowest.rounded.p-space-sm');
      if (codeBlock) codeBlock.textContent = 'Recorded relationship: ' + describe(edge.parent) + ' → ' + describe(edge.child);
      card.querySelectorAll('span, p').forEach(function (element) {
        if (/uid=0\(root\)|appuser:x:|AKIAIOS|9a4f21b7|CVE-2021-41773|staging-api\.corp\.net/i.test(element.textContent || '')) setHidden(element, true);
      });
      card.querySelectorAll('button').forEach(function (button) { setHidden(button, true); });
      if (insertBefore && insertBefore.parentElement === container) container.insertBefore(card, insertBefore);
      else container.appendChild(card);
    });
    // Other chain summaries on this page are hard-coded attack narratives.
    // Retain the original heading and the edge cards populated above only.
    const graphSection = container.closest('section') || container;
    document.querySelectorAll('main section').forEach(function (section) {
      if (section !== graphSection && !section.contains(document.getElementById('btn-recompute'))) setHidden(section, true);
    });
    document.querySelectorAll('main span, main p, main h2, main h3').forEach(function (element) {
      if (/3 Lethal Paths|CVSS Compound: 10\.0|CHAIN #AC-09|CHAIN #AC-04|CHAIN #AC-01|100% Deterministic Link|94% Telemetry Correlated|ACTIVE EXPLOIT DETECTED|uid=0\(root\)|api\.internal\.corp|db\.internal/i.test(element.textContent || '')) {
        const card = element.closest('.bg-surface-container-low.rounded-xl, .bg-surface-container.rounded-xl');
        if (card && !card.contains(container) && !card.contains(document.getElementById('btn-recompute'))) setHidden(card, true);
        else if (!card) setHidden(element, true);
      }
    });
    ['Add Custom Mitigation Rule','Generate Red Team Retest Script','Trace Proof'].forEach(hideButtonByText);
    const recompute = document.getElementById('btn-recompute');
    if (recompute) recompute.onclick = async function () {
      recompute.disabled = true;
      try {
        const updated = await requestJson('/api/pivot/graph');
        if (!Array.isArray(updated.edges) || !updated.edges.length) { wireUnavailablePage(); return; }
        window.location.reload();
      } catch (error) { window.alert('Could not refresh recorded attack relationships: ' + error.message); }
      finally { recompute.disabled = false; }
    };
    const exportButton = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /Export.*Graph.*JSON/i.test(button.textContent || '');
    });
    if (exportButton) exportButton.onclick = async function () {
      try {
        const data = await requestJson('/api/pivot/graph');
        const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a'); link.href = url; link.download = 'whaxon-pivot-graph.json';
        document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
      } catch (error) { window.alert('Graph export failed: ' + error.message); }
    };
  }
  async function wireSettings() {
    wireUnavailablePage();
  }
  async function wireCoverage() {
    const gapButton = Array.from(document.querySelectorAll('main button')).find(function (button) {
      return /^Gap Report$/i.test((button.textContent || '').trim());
    });
    const unsupportedButtons = [
      'Detonate Sequence', 'Query Blue Telemetry', 'Configure Vector Filters',
      'Push Rule to SIEM', 'Deploy to Sentinel', 'Deploy to Splunk',
      'Emergency Halt Scan', 'Export Validation Matrix'
    ];
    unsupportedButtons.forEach(hideButtonByText);

    // This backend records skipped/omitted checks per job. It does not execute
    // BAS simulations or query SIEM telemetry, so expose only those recorded
    // coverage gaps and suppress the static detection claims in the prototype.
    const main = document.querySelector('main');
    const workspace = main && Array.from(main.querySelectorAll('div')).find(function (element) {
      return element.classList.contains('p-margin') &&
        element.classList.contains('flex') &&
        element.classList.contains('flex-col') &&
        element.classList.contains('gap-gutter') &&
        Array.from(element.children).some(function (child) { return child.classList.contains('grid'); });
    });
    let jobs = [];
    try {
      const history = await requestJson('/api/history');
      jobs = Array.isArray(history) ? history : (history.jobs || history.history || []);
    } catch (error) {
      wireUnavailablePage();
      return;
    }
    const candidates = jobs.slice(0, 20).filter(function (job) {
      return job && (job.id || job.job_id);
    });
    let selectedJob = candidates[0] || null;
    let gaps = [];
    for (const job of candidates) {
      const id = String(job.id || job.job_id);
      try {
        const data = await requestJson('/api/coverage/' + encodeURIComponent(id));
        if (job === candidates[0]) { selectedJob = job; gaps = Array.isArray(data.gaps) ? data.gaps : []; }
        if (Array.isArray(data.gaps) && data.gaps.length) {
          selectedJob = job;
          gaps = data.gaps;
          break;
        }
      } catch (_) {
        // A missing coverage record for one job should not hide other recorded jobs.
      }
    }

    const kpiGrid = main && Array.from(main.querySelectorAll('.grid')).find(function (grid) {
      return /DETECTION VALIDATION RATIO/.test(grid.textContent || '') &&
        /CAUGHT/.test(grid.textContent || '');
    });
    if (kpiGrid) {
      const cards = Array.from(kpiGrid.children).filter(function (child) {
        return child.classList.contains('bg-surface-container-low') ||
          child.classList.contains('bg-surface-container');
      });
      cards.forEach(function (card, index) { if (index > 0) setHidden(card, true); });
      const card = cards[0];
      if (card) {
        const labels = Array.from(card.querySelectorAll('span'));
        const title = labels.find(function (span) { return /DETECTION VALIDATION RATIO/.test(span.textContent || ''); });
        if (title) title.textContent = 'RECORDED COVERAGE GAPS';
        const value = card.querySelector('.font-headline-xl');
        if (value) value.textContent = String(gaps.length);
        const caught = labels.find(function (span) { return (span.textContent || '').trim() === 'CAUGHT'; });
        if (caught) caught.textContent = 'RECORDED';
        const detail = card.querySelector('.mt-space-md');
        if (detail) {
          detail.replaceChildren();
          const line = document.createElement('span');
          line.className = 'font-code-sm text-code-sm text-on-surface-variant';
          line.textContent = selectedJob
            ? 'Job ' + String(selectedJob.id || selectedJob.job_id) + ' · ' + String(selectedJob.target || 'target not recorded')
            : 'No jobs recorded yet';
          detail.appendChild(line);
        }
        const progress = card.querySelector('.w-full.bg-surface-container-highest');
        if (progress) setHidden(progress, true);
      }
    }
    if (workspace) {
      Array.from(workspace.children).forEach(function (child) {
        if (child !== kpiGrid) setHidden(child, true);
      });
    }
    // Remove fixed demo figures and target labels outside the primary workspace.
    document.querySelectorAll('main span, main p, main strong, main h2, main h3').forEach(function (element) {
      if (/api\.internal\.corp|57\.2%|4 of 7 executed techniques|SEC-AZ-992|SIGMA-WIN-04769|BOLA State Manipulation|MITRE ATT&CK Coverage Heatmap|Automated rule generation available/i.test(element.textContent || '')) {
        const card = element.closest('.bg-surface-container-low.rounded-lg, .bg-surface-container.rounded-lg');
        if (card && !card.contains(kpiGrid)) setHidden(card, true);
        else if (!card) setHidden(element, true);
      }
    });
    if (gapButton) gapButton.onclick = function () {
      const jobLabel = selectedJob ? String(selectedJob.id || selectedJob.job_id) : 'none';
      const lines = gaps.map(function (gap) {
        return '[' + String(gap.kind || 'gap') + '] ' +
          String(gap.tool_id || 'unknown tool') + ' · ' +
          String(gap.target || 'target not recorded') + ' · ' +
          String(gap.detail || 'No detail recorded');
      });
      window.alert('Recorded coverage gaps for job ' + jobLabel + ' (' + gaps.length + '):\n' +
        (lines.length ? lines.join('\n') : 'No coverage gaps are recorded for the available job.'));
    };
  }
  async function wireThreatIntel() {
    let status, modules;
    try {
      status = await requestJson('/api/msf/status');
      if (!status.up) { wireUnavailablePage(); return; }
      modules = await requestJson('/api/msf/modules/exploit');
    } catch (_) { wireUnavailablePage(); return; }
    if (!Array.isArray(modules) || !modules.length) { wireUnavailablePage(); return; }

    const template = document.querySelector('.cve-row-item');
    if (!template || !template.parentElement) { wireUnavailablePage(); return; }
    const list = template.parentElement;
    const panel = template.closest('.lg\\:col-span-7');
    const workbench = panel && panel.parentElement;
    const workspace = (function () {
      let node = workbench;
      while (node && !(node.classList.contains('p-margin') && node.classList.contains('gap-space-2xl'))) node = node.parentElement;
      return node;
    })();
    const cardTemplate = template.cloneNode(true);
    list.replaceChildren();
    modules.slice(0, 50).forEach(function (moduleName) {
      if (typeof moduleName !== 'string' || !moduleName.trim()) return;
      const card = cardTemplate.cloneNode(true);
      card.removeAttribute('onclick');
      card.dataset.tags = 'msf';
      const moduleLabel = card.querySelector('.font-code-md.text-code-md.text-primary.font-bold');
      const moduleTitle = card.querySelector('.font-headline-sm.text-headline-sm.text-on-surface.font-semibold');
      if (moduleLabel) moduleLabel.textContent = 'MSF MODULE';
      if (moduleTitle) moduleTitle.textContent = moduleName;
      card.querySelectorAll('span').forEach(function (span) {
        if (/CVSS|EPSS|CISA KEV|SHADOW API|PUBLIC READ DRIFT|CRITICAL EXPOSURE|Async Python PoC Ready/i.test(span.textContent || '')) setHidden(span, true);
      });
      const description = card.querySelector('p');
      if (description) setHidden(description, true);
      const sampleDetails = Array.from(card.querySelectorAll('div')).find(function (element) {
        return element.classList.contains('flex-wrap') && element.classList.contains('justify-between') &&
          element.classList.contains('pt-space-xs') && /In Scope:/.test(element.textContent || '');
      });
      if (sampleDetails) setHidden(sampleDetails, true);
      card.querySelectorAll('button').forEach(function (button) { setHidden(button, true); });
      list.appendChild(card);
    });
    if (!list.children.length) { wireUnavailablePage(); return; }

    // Only the live Metasploit module catalog is supported on this page today.
    // Hide static CVE scores, threat-feed claims, and the unimplemented runner.
    if (workspace) Array.from(workspace.children).forEach(function (child) {
      if (!child.contains(workbench)) setHidden(child, true);
    });
    const kpiGrid = Array.from(document.querySelectorAll('main .grid')).find(function (grid) {
      return /Verified Modules/.test(grid.textContent || '') && /Shadow Advisories/.test(grid.textContent || '');
    });
    if (kpiGrid) setHidden(kpiGrid, true);
    document.querySelectorAll('main span').forEach(function (span) {
      if (/^(CISA KEV:|LOCAL DB:|EXPLOIT-DB:|EPSS MODEL:)$/i.test((span.textContent || '').trim())) {
        setHidden(span.parentElement || span, true);
      }
    });
    const sortSelect = document.querySelector('main select');
    if (sortSelect) {
      const sortBox = sortSelect.closest('div.flex.items-center.gap-1.shrink-0');
      setHidden(sortBox || sortSelect, true);
    }
    const inspector = document.getElementById('inspector-cve-id');
    if (inspector) {
      let column = inspector;
      while (column && !column.classList.contains('lg:col-span-5')) column = column.parentElement;
      setHidden(column, true);
    }
    ['sync upstream feeds','rebuild sqlite vector db','searchsploit terminal',
     'inspect exploit code','queue safe probe','simulate dry-run','metasploit harness',
     'inspect msf options','execute curl replay test','view nuclei heuristics',
     'arm & queue for hitl approval gate','terminal log','emergency halt scan'].forEach(hideButtonByText);
    const allButton = Array.from(panel.querySelectorAll('button')).find(function (button) {
      return /^All \(/i.test((button.textContent || '').trim());
    });
    if (allButton) allButton.textContent = 'All (' + list.children.length + ')';
    ['CISA KEV','Weaponized PoC','Remote Code Execution','PrivEsc'].forEach(hideButtonByText);
    const search = panel.querySelector('input[placeholder*="Filter by CVE-ID"]');
    if (search) search.oninput = function () {
      const query = search.value.toLowerCase().trim();
      list.querySelectorAll('.cve-row-item').forEach(function (card) {
        setHidden(card, !card.textContent.toLowerCase().includes(query));
      });
    };
  }
  function wireUnavailablePage() {
    // Remove navigation entry points for workflows whose required backend is
    // unavailable. Direct routes remain safe, but users should not be invited
    // into a page that has no working data source.
    const aliasGroups = [
      ['settings-and-api-explorer', 'settings-and-secrets-vault', 'settings-secrets-vault'],
      ['bug-bounty-and-live-browser-studio', 'bug-bounty-live-browser'],
      ['ptaas-client-portal'],
      ['cryptographic-audit-log'],
      ['bas-and-detection-validation'],
      ['compliance-and-framework-crosswalk'],
      ['threat-intel-and-exploit-arsenal'],
      ['attack-surface-and-continuous-monitoring'],
      ['correlated-attack-chains'],
      ['evidence-file-inspector'],
      ['system-diagnostics-and-health', 'system-diagnostics-health'],
      ['adapter-and-plugin-manager', 'adapter-plugin-manager'],
      ['scope-and-targets', 'scope-targets'],
      ['run-and-orchestration', 'run-orchestration'],
      ['trust-layer-and-findings', 'trust-layer-findings'],
      ['ptes-coverage-and-reports', 'ptes-coverage-reports'],
      ['remediation-retest-studio'],
      ['ai-strategy-gate'],
      ['job-execution-history'],
      ['dashboard-zero-state']
    ];
    const unavailableSlugs = new Set([page]);
    aliasGroups.forEach(function (group) {
      if (group.includes(page)) group.forEach(function (slug) { unavailableSlugs.add(slug); });
    });
    document.querySelectorAll('[data-path]').forEach(function (link) {
      if (unavailableSlugs.has(link.getAttribute('data-path'))) setHidden(link, true);
    });
    const main = document.querySelector('main');
    if (main) Array.from(main.children).forEach(function (child) { setHidden(child, true); });
    // Some supplied designs place demo modals outside <main>. Hide those too
    // whenever their native workflow has no real backend wiring.
    document.querySelectorAll('[id]').forEach(function (element) {
      if (/modal/i.test(element.id)) {
        setHidden(element, true);
        element.setAttribute('aria-hidden', 'true');
      }
    });
  }
  if (page === 'trust-layer-and-findings') wireFindings();
  if (page === 'trust-layer-findings') wireFindings();
  if (page === 'trust-layer-approvals-queue-modal') wireAiApprovals();
  if (page === 'scope-and-targets' || page === 'scope-targets') wireScope();
  if (page === 'run-and-orchestration' || page === 'run-orchestration') wireRun();
  if (page === 'dashboard-zero-state') wireDashboard();
  if (page === 'ptes-coverage-and-reports' || page === 'ptes-coverage-reports') wireReports();
  if (page === 'bas-and-detection-validation') wireCoverage();
  if (page === 'compliance-and-framework-crosswalk') wireUnavailablePage();
  if (page === 'threat-intel-and-exploit-arsenal') wireThreatIntel();
  if (page === 'job-execution-history') wireHistory();
  if (page === 'adapter-and-plugin-manager' || page === 'adapter-plugin-manager') wireCatalog();
  if (page === 'remediation-retest-studio') wireRetest();
  if (page === 'attack-surface-and-continuous-monitoring') wireAttackSurface();
  if (page === 'ai-strategy-gate') wireAiStrategyGate();
  if (page === 'system-diagnostics-and-health' || page === 'system-diagnostics-health') wireHealth();
  if (page === 'evidence-file-inspector') wireEvidence();
  if (page === 'correlated-attack-chains') wireChains();
  if (page === 'settings-and-api-explorer' || page === 'settings-and-secrets-vault' || page === 'settings-secrets-vault') wireSettings();
  if (page === 'bug-bounty-and-live-browser-studio' || page === 'bug-bounty-live-browser' || page === 'ptaas-client-portal' || page === 'cryptographic-audit-log') wireUnavailablePage();
})();
</script>"""

    def _serve_new_ui(page: str):
        from flask import abort
        source = _NEW_UI_PAGES.get(page)
        if source is None:
            return abort(404)
        # The source folder is deliberately outside the Python package. Resolve
        # only allowlisted design paths; never accept a user-supplied filesystem path.
        repo_root = Path(__file__).resolve().parents[4]
        design_root = (repo_root / "web ui files and rendering").resolve()
        if not design_root.is_dir():
            # Wheels include only the existing HTML design sources needed at runtime.
            design_root = (Path(__file__).resolve().parents[2] / "ui_source").resolve()
        design_path = (design_root / source).resolve()
        if not design_path.is_relative_to(design_root) or not design_path.is_file():
            return {"error": "source UI design files are unavailable in this checkout"}, 503
        html = design_path.read_text(encoding="utf-8")
        script = _new_ui_script(page)
        if "</body>" in html:
            html = html.replace("</body>", script + "</body>", 1)
        else:
            html += script
        return app.response_class(html, mimetype="text/html")

    @app.get("/legacy-ui")
    def legacy_ui():
        return render_template("index.html")

    @app.get("/ui")
    def ui():
        return _serve_new_ui("dashboard-zero-state")

    @app.get("/ui/<page>")
    def ui_page(page: str):
        return _serve_new_ui(page)

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
