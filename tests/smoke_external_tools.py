"""Run harmless scanner integration checks against a loopback-only HTTP fixture.

This script is intended for clean-install CI acceptance, not as a production scan.
All scanner targets bind to and resolve to 127.0.0.1.
"""
from __future__ import annotations

import json
import os
import re
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


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        with request_lock:
            requests.append(self.path)
        path = urlsplit(self.path).path
        if path in {"/admin", "/robots.txt"}:
            body = b"fixture response\n"
            status = 200
        elif path == "/search":
            # A deterministic, harmless boolean oracle for SQLmap. It models
            # a read-only product lookup and never connects to a database or
            # exposes data. Boolean conditions only change a fixed response.
            query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            value = unquote(query.get("id", [""])[0]).lower()
            false_match = re.search(r"\band\s+(\d+)\s*=\s*(\d+)\b", value)
            body = (
                b"No products found\n"
                if false_match and false_match.group(1) != false_match.group(2)
                else b"Product: fixture-item\n"
            )
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


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
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

            # Exercise the installed scanner through the actual Engine V2 plan,
            # policy, provider, scheduler and evidence-seal path. The target is
            # the same ephemeral loopback fixture; approval is exact-plan-bound.
            import asyncio

            from whaxon.core import Core
            from whaxon.core.workflow import WorkflowPlan, WorkflowTask

            async def run_v2_sqlmap() -> tuple[dict, dict]:
                core = Core(root / "v2-data")
                await core.initialize(drain=False)
                task = WorkflowTask(
                    id="sqlmap-loopback",
                    capability_id="tool.sqlmap",
                    target=f"{base_url}/search?id=2",
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
                return result, evidence

            with request_lock:
                before_v2 = len(requests)
            v2_result, v2_evidence = asyncio.run(run_v2_sqlmap())
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
            ), "Engine V2 SQLmap evidence did not retain the detected SQL injection finding"

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

            print(
                "Loopback scanner smoke passed: Nmap TCP discovery, Gobuster directory "
                "enumeration, ffuf content discovery, SQLmap boolean-injection detection "
                "directly and through Engine V2"
                + (", and Nuclei template matching." if shutil.which("nuclei") else ".")
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
