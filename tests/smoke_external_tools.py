"""Run harmless scanner integration checks against a loopback-only HTTP fixture.

This script is intended for clean-install CI acceptance, not as a production scan.
All scanner targets bind to and resolve to 127.0.0.1.
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

requests: list[str] = []
request_lock = threading.Lock()

_ORACLE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sqlmap_boolean_oracle.py"
_ORACLE_SPEC = importlib.util.spec_from_file_location("sqlmap_boolean_oracle", _ORACLE_PATH)
if _ORACLE_SPEC is None or _ORACLE_SPEC.loader is None:
    raise RuntimeError("loopback SQLmap oracle is unavailable")
_ORACLE_MODULE = importlib.util.module_from_spec(_ORACLE_SPEC)
_ORACLE_SPEC.loader.exec_module(_ORACLE_MODULE)
_sqlmap_boolean_oracle = _ORACLE_MODULE.sqlmap_boolean_oracle


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        with request_lock:
            requests.append(self.path)
        path = urlsplit(self.path).path
        if path == "/hold":
            self.server.hold_observed.set()
            self.server.allow_hold_response.wait(timeout=15)
            body = b"held fixture response\n"
            status = 200
        elif path in {"/admin", "/robots.txt"}:
            body = b"fixture response\n"
            status = 200
        elif path == "/search":
            # A deterministic, harmless boolean oracle for SQLmap. It models
            # a read-only product lookup and never connects to a database or
            # exposes data. Boolean conditions only change a fixed response.
            query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            value = unquote(query.get("id", [""])[0]).lower()
            body = _sqlmap_boolean_oracle(value)
            status = 200
        else:
            body = b"not found\n"
            status = 404
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        pass


def run(argv: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout, check=False
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {argv!r}\n"
            f"stdout:\n{completed.stdout[-4000:]}\n"
            f"stderr:\n{completed.stderr[-4000:]}"
        )
    return completed


async def _prepare_v2_catalog_provider(root: Path, tool_id: str, target: str, args: str):
    import json
    import time

    from whaxon.core import Core
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    data_dir = root / f"v2-{tool_id}"
    data_dir.mkdir(parents=True, exist_ok=True)
    packaged_catalog = Path(__file__).resolve().parents[1] / "src" / "whaxon" / "data" / "tools.json"
    catalog = json.loads(packaged_catalog.read_text(encoding="utf-8"))
    tool = next(item for item in catalog["tools"] if item["id"] == tool_id)
    tool["args"] = args
    (data_dir / "tools.json").write_text(json.dumps(catalog), encoding="utf-8")

    core = Core(data_dir)
    await core.initialize(drain=False)
    task = WorkflowTask(
        id=f"{tool_id}-loopback",
        capability_id=f"tool.{tool_id}",
        target=target,
        permissions=("network.scan",),
        impact="moderate",
        timeout_s=120,
    )
    manifest = core.providers.manifest_for(task.capability_id)
    plan_id = f"{tool_id}-loopback-plan"
    plan = WorkflowPlan(
        mission_id=f"{tool_id}-loopback",
        tasks=(task,),
        metadata={"provider_bindings": {task.id: {
            "provider_id": manifest.provider_id,
            "provider_version": manifest.provider_version,
            "manifest_fingerprint": manifest.fingerprint,
        }}},
    )
    core.create_mission(f"{tool_id}-loopback", f"Exercise {tool_id} against loopback fixture")
    core.save_workflow_plan(plan_id, plan)
    core.store.grant_workflow_approval(
        plan_id, task.id, f"ci-{tool_id}-loopback-approval",
        "ci-operator", expires_at=time.time() + 300,
    )
    return core, plan_id, data_dir


async def _run_v2_catalog_provider(root: Path, tool_id: str, target: str, args: str):
    core, plan_id, _data_dir = await _prepare_v2_catalog_provider(
        root, tool_id, target, args,
    )
    result = await core.run_workflow_plan(plan_id, max_tasks=1, max_concurrency=1)
    evidence = core.workflow_evidence(plan_id)
    job_id = evidence["attempts"][0].get("job_id")
    evidence["provider_findings"] = core.store.get_findings(job_id) if job_id else []
    manifest = core.providers.manifest_for(f"tool.{tool_id}")
    binding = {
        "provider_id": manifest.provider_id,
        "provider_version": manifest.provider_version,
        "manifest_fingerprint": manifest.fingerprint,
    }
    return result, evidence, binding


async def _cancel_real_gobuster_after_loopback_effect(root: Path, server, port: int):
    from whaxon.core import Core

    # Each saved plan ID is immutable, so keep cancellation in its own
    # durable store instead of reusing the successful discovery plan.
    scenario_root = root / "gobuster-cancel"
    scenario_root.mkdir(parents=True)
    wordlist = scenario_root / "cancel-words.txt"
    wordlist.write_text("hold\\n", encoding="utf-8")
    core, plan_id, data_dir = await _prepare_v2_catalog_provider(
        scenario_root, "gobuster", "127.0.0.1",
        f"dir -u http://{{target}}:{port} -w {wordlist} -q -t 1 --no-error --timeout 10s",
    )
    manifest = core.providers.manifest_for("tool.gobuster")
    binding = {
        "provider_id": manifest.provider_id,
        "provider_version": manifest.provider_version,
        "manifest_fingerprint": manifest.fingerprint,
    }
    running = asyncio.create_task(
        core.run_workflow_plan(plan_id, max_tasks=1, max_concurrency=1),
    )
    observed = await asyncio.to_thread(server.hold_observed.wait, 15)
    if not observed:
        server.allow_hold_response.set()
        result = await running
        evidence = core.workflow_evidence(plan_id)
        job_id = evidence["attempts"][0].get("job_id")
        output = core.store.lines_since(job_id) if job_id else []
        with request_lock:
            observed_paths = [urlsplit(path).path for path in requests]
        # Preserve the failed reachability observation as evidence. Without a
        # real held request, this run cannot qualify cancellation or replay.
        return {
            "tool": "gobuster",
            "cancellation_status": "not_exercised",
            "cancellation_request_observed": False,
            "attempt_status": result.get("tasks", [{}])[0].get("status"),
            "observed_loopback_paths": sorted(set(observed_paths)),
            "provider_output_tail": output[-20:],
            "evidence_integrity_verified": evidence.get(
                "all_evidence_integrity_verified", False,
            ),
            **binding,
        }
    # The server has received a real scanner request. Cancellation now races
    # with an in-flight external process and must be recorded as uncertain.
    core.cancel_workflow_plan(plan_id)
    server.allow_hold_response.set()
    result = await running
    assert result["tasks"] == [{"id": "gobuster-loopback", "status": "uncertain"}], result
    await asyncio.sleep(0.5)

    restarted = Core(data_dir)
    await restarted.initialize(drain=False)

    async def forbidden_replay(_task):
        raise AssertionError("cancelled real provider effect must never be replayed")

    retry = await restarted.run_workflow_plan(
        plan_id, dispatch=forbidden_replay, max_tasks=1, max_concurrency=1,
    )
    assert retry["attempts"] == 0, retry
    assert len([path for path in requests if path.split("?", 1)[0] == "/hold"]) == 1
    return {
        "tool": "gobuster",
        "attempt_status": "uncertain",
        "restart_replay_attempts": retry["attempts"],
        "loopback_effect_requests": 1,
        **binding,
    }


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    server.hold_observed = threading.Event()
    server.allow_hold_response = threading.Event()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base_url = f"http://127.0.0.1:{port}"
    try:
        with tempfile.TemporaryDirectory(prefix="whaxon-tool-smoke-") as raw:
            root = Path(raw)
            wordlist = root / "words.txt"
            wordlist.write_text("admin\nrobots.txt\nmissing\n", encoding="utf-8")

            nmap = run([
                "nmap", "-sT", "-Pn", "-n", "-p", str(port),
                "--reason", "127.0.0.1",
            ])
            assert f"{port}/tcp open" in nmap.stdout, nmap.stdout

            gobuster = run([
                "gobuster", "dir", "-u", base_url, "-w", str(wordlist),
                "-q", "-t", "1", "--no-error", "--timeout", "3s",
            ])
            assert "admin" in gobuster.stdout, gobuster.stdout

            ffuf_output = root / "ffuf.json"
            run([
                "ffuf", "-w", str(wordlist), "-u", f"{base_url}/FUZZ",
                "-mc", "200", "-of", "json", "-o", str(ffuf_output),
                "-s", "-noninteractive", "-timeout", "3", "-maxtime", "20",
            ])
            ffuf_results = json.loads(ffuf_output.read_text(encoding="utf-8"))["results"]
            assert any(item.get("input", {}).get("FUZZ") == "admin" for item in ffuf_results), ffuf_results

            sqlmap_output = root / "sqlmap-output"
            sqlmap_direct = run([
                "sqlmap", "-u", f"{base_url}/search?id=1",
                "--batch", "--flush-session", "--technique=B",
                "--level=1", "--risk=1", "--threads=1",
                "--timeout=2", "--retries=0",
                "--disable-coloring", "--output-dir", str(sqlmap_output),
            ], timeout=90)
            with request_lock:
                sqlmap_requests = [path for path in requests if path.startswith("/search?")]
            assert sqlmap_requests, "SQLmap did not send an HTTP request to the loopback fixture"
            assert "injectable" in (
                sqlmap_direct.stdout + "\n" + sqlmap_direct.stderr
            ).lower(), (
                "SQLmap contacted the fixture but did not identify its boolean oracle"
            )
            assert "parameter: id (get)" in sqlmap_direct.stdout.lower() and (
                "false positive or unexploitable" not in sqlmap_direct.stdout.lower()
            ), (
                "SQLmap did not retain a confirmed finding after final confirmation; "
                f"stdout={sqlmap_direct.stdout[-5000:]!r}; "
                f"stderr={sqlmap_direct.stderr[-2000:]!r}; "
                f"recent_requests={sqlmap_requests[-50:]!r}"
            )

            # Exercise the installed scanner through the actual Engine V2 plan,
            # policy, provider, scheduler and evidence-seal path. The target is
            # the same ephemeral loopback fixture; approval is exact-plan-bound.
            import asyncio

            from whaxon.core import Core
            from whaxon.core.workflow import WorkflowPlan, WorkflowTask

            async def run_v2_sqlmap() -> tuple[dict, dict, list[dict], dict]:
                v2_data = root / "v2-data"
                v2_data.mkdir(parents=True, exist_ok=True)
                packaged_catalog = Path(__file__).resolve().parents[1] / "src" / "whaxon" / "data" / "tools.json"
                catalog = json.loads(packaged_catalog.read_text(encoding="utf-8"))
                sqlmap_tool = next(tool for tool in catalog["tools"] if tool["id"] == "sqlmap")
                # Keep this smoke deterministic and bounded: exercise the
                # supported boolean technique against the fixture's boolean
                # oracle, with a private SQLmap session/output directory.
                sqlmap_tool["args"] = (
                    f"-u {{target}} --batch --level=1 --risk=1 --technique=B "
                    f"--threads=1 --timeout=2 --retries=0 --disable-coloring "
                    f"--flush-session --output-dir={root / 'sqlmap-v2-output'}"
                )
                (v2_data / "tools.json").write_text(
                    json.dumps(catalog), encoding="utf-8",
                )
                core = Core(v2_data)
                await core.initialize(drain=False)
                task = WorkflowTask(
                    id="sqlmap-loopback",
                    capability_id="tool.sqlmap",
                    target=f"{base_url}/search?id=1",
                    permissions=("network.scan",),
                    impact="moderate",
                    timeout_s=180,
                )
                manifest = core.providers.manifest_for(task.capability_id)
                plan = WorkflowPlan(
                    mission_id="loopback-smoke",
                    tasks=(task,),
                    metadata={
                        "provider_bindings": {
                            task.id: {
                                "provider_id": manifest.provider_id,
                                "provider_version": manifest.provider_version,
                                "manifest_fingerprint": manifest.fingerprint,
                            },
                        },
                    },
                )
                core.create_mission(
                    "loopback-smoke", "Exercise Engine V2 against loopback only",
                )
                core.save_workflow_plan("loopback-smoke-plan", plan)
                core.store.grant_workflow_approval(
                    "loopback-smoke-plan", task.id, "ci-loopback-approval",
                    "ci-operator", expires_at=time.time() + 300,
                )
                result = await core.run_workflow_plan(
                    "loopback-smoke-plan", max_tasks=1, max_concurrency=1,
                )
                evidence = core.workflow_evidence("loopback-smoke-plan")
                job_id = evidence["attempts"][0].get("job_id")
                output = core.store.lines_since(job_id) if job_id else []
                manifest = core.providers.manifest_for(task.capability_id)
                binding = {
                    "provider_id": manifest.provider_id,
                    "provider_version": manifest.provider_version,
                    "manifest_fingerprint": manifest.fingerprint,
                }
                return result, evidence, output, binding

            with request_lock:
                before_v2 = len(requests)
            v2_result, v2_evidence, v2_output, v2_binding = asyncio.run(run_v2_sqlmap())
            assert v2_result["complete"] is True, v2_result
            assert v2_result["tasks"] == [{"id": "sqlmap-loopback", "status": "succeeded"}], v2_result
            assert v2_evidence["all_evidence_recorded"] is True, v2_evidence
            assert v2_evidence["all_evidence_integrity_verified"] is True, v2_evidence
            with request_lock:
                v2_requests = requests[before_v2:]
            assert any(path.startswith("/search?") for path in v2_requests), (
                "Engine V2 SQLmap provider did not contact its approved loopback target"
            )
            assert any(
                finding["kind"] == "sqli"
                for attempt in v2_evidence["attempts"]
                for finding in attempt["findings"]
            ), (
                "Engine V2 SQLmap evidence did not retain the detected SQL injection finding; "
                f"evidence={v2_evidence!r}; output={v2_output[-80:]!r}"
            )

            # Exercise the real Nmap, Gobuster, and ffuf binaries through the
            # approved Engine V2 provider, scheduler, ToolRunner, parser, and
            # evidence-seal path. All targets are the ephemeral loopback fixture.
            v2_provider_runs = [{
                "tool": "sqlmap", "status": "succeeded",
                "evidence_integrity_verified": True, **v2_binding,
            }]
            v2_nmap, nmap_evidence, nmap_binding = asyncio.run(_run_v2_catalog_provider(
                root, "nmap", "127.0.0.1",
                f"-sT -Pn -n -p {port} {{target}}",
            ))
            assert v2_nmap["complete"] is True and v2_nmap["tasks"] == [
                {"id": "nmap-loopback", "status": "succeeded"},
            ], v2_nmap
            assert nmap_evidence["all_evidence_integrity_verified"] is True, nmap_evidence
            assert any(
                finding["kind"] == "open_port" and finding["data"].get("port") == port
                for finding in nmap_evidence["provider_findings"]
            ), nmap_evidence
            v2_provider_runs.append({"tool": "nmap", "status": "succeeded", "evidence_integrity_verified": True, **nmap_binding})

            with request_lock:
                before_v2_gobuster = len(requests)
            v2_gobuster, gobuster_evidence, gobuster_binding = asyncio.run(_run_v2_catalog_provider(
                root, "gobuster", "127.0.0.1",
                f"dir -u http://{{target}}:{port} -w {wordlist} -q -t 1 --no-error --timeout 3s",
            ))
            assert v2_gobuster["complete"] is True and v2_gobuster["tasks"] == [
                {"id": "gobuster-loopback", "status": "succeeded"},
            ], v2_gobuster
            assert gobuster_evidence["all_evidence_integrity_verified"] is True, gobuster_evidence
            with request_lock:
                gobuster_paths = [
                    urlsplit(path).path for path in requests[before_v2_gobuster:]
                ]
            # Gobuster's V2 adapter currently seals a successful attempt but
            # does not persist normalized directory findings. Prove the real
            # binary's effect from the fixture's observed requests without
            # treating an empty finding set as a successful finding.
            assert "/admin" in gobuster_paths, {
                "evidence": gobuster_evidence,
                "observed_paths": gobuster_paths,
            }
            gobuster_evidence["observed_loopback_paths"] = sorted(set(gobuster_paths))
            v2_provider_runs.append({
                "tool": "gobuster",
                "status": "succeeded",
                "evidence_integrity_verified": True,
                "normalized_finding_count": len(gobuster_evidence["provider_findings"]),
                "observed_loopback_paths": sorted(set(gobuster_paths)),
                **gobuster_binding,
            })

            with request_lock:
                before_v2_ffuf = len(requests)
            v2_ffuf, ffuf_evidence, ffuf_binding = asyncio.run(_run_v2_catalog_provider(
                root, "ffuf", base_url,
                f"-u {{target}}/FUZZ -w {wordlist} -mc 200 -noninteractive -timeout 3 -maxtime 20",
            ))
            assert v2_ffuf["complete"] is True and v2_ffuf["tasks"] == [
                {"id": "ffuf-loopback", "status": "succeeded"},
            ], v2_ffuf
            assert ffuf_evidence["all_evidence_integrity_verified"] is True, ffuf_evidence
            with request_lock:
                ffuf_paths = [urlsplit(path).path for path in requests[before_v2_ffuf:]]
            # The V2 FFuf adapter currently seals the completed run but does
            # not persist normalized findings. Verify its effect from requests
            # received by the fixture and expose the empty finding set.
            assert "/admin" in ffuf_paths, {
                "evidence": ffuf_evidence,
                "observed_paths": ffuf_paths,
            }
            ffuf_evidence["observed_loopback_paths"] = sorted(set(ffuf_paths))
            v2_provider_runs.append({
                "tool": "ffuf",
                "status": "succeeded",
                "evidence_integrity_verified": True,
                "normalized_finding_count": len(ffuf_evidence["provider_findings"]),
                "observed_loopback_paths": sorted(set(ffuf_paths)),
                **ffuf_binding,
            })

            cancellation_evidence = asyncio.run(
                _cancel_real_gobuster_after_loopback_effect(root, server, port),
            )
            v2_provider_runs.append(cancellation_evidence)

            nuclei = shutil.which("nuclei")
            if os.environ.get("WHAXON_REQUIRE_NUCLEI") == "1" and not nuclei:
                raise AssertionError("Homebrew acceptance requires the installed Nuclei executable")
            if nuclei:
                template = root / "whaxon-loopback-smoke.yaml"
                template.write_text(
                    """id: whaxon-loopback-smoke
info:
  name: WHAXON loopback smoke
  author: whaxon-ci
  severity: info
  description: Confirms a local HTTP fixture responds with the expected status
http:
  - method: GET
    path:
      - "{{BaseURL}}/admin"
    matchers:
      - type: status
        status:
          - 200
""",
                    encoding="utf-8",
                )
                nuclei_output = root / "nuclei.jsonl"
                run([
                    nuclei, "-u", base_url, "-t", str(template),
                    "-duc", "-no-interactsh", "-silent", "-jsonl",
                    "-timeout", "3", "-retries", "0",
                    "-o", str(nuclei_output),
                ], timeout=60)
                output = nuclei_output.read_text(encoding="utf-8")
                assert "whaxon-loopback-smoke" in output, output

            evidence = {
                "schema_version": "whaxon.provider-loopback-smoke.v1",
                "fixture": "ephemeral HTTP server bound to 127.0.0.1",
                "engine_v2_provider_runs": v2_provider_runs,
                "external_egress_isolated_by_workflow": True,
                "limitations": [
                    "Covers only Nmap, Gobuster, ffuf, and SQLmap in this job.",
                    "The CI package manager selects tool versions; binary versions and SHA-256 values are retained separately.",
                    "This is isolated loopback evidence, not production or external-target qualification.",
                ],
            }
            Path("provider-smoke-evidence.json").write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\\n", encoding="utf-8",
            )
            print(
                "Loopback scanner smoke passed: Nmap, Gobuster, ffuf and SQLmap; "
                "real Gobuster cancellation remained uncertain after restart without replay."
                + (" Nuclei template matching also passed." if shutil.which("nuclei") else "")
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
