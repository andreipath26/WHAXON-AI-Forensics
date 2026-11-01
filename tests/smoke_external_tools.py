"""Run harmless scanner integration checks against a loopback-only HTTP fixture.

This script is intended for clean-install CI acceptance, not as a production scan.
All scanner targets bind to and resolve to 127.0.0.1.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

requests: list[str] = []
request_lock = threading.Lock()


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        with request_lock:
            requests.append(self.path)
        path = urlsplit(self.path).path
        if path in {"/admin", "/robots.txt", "/search"}:
            body = b"fixture response\n"
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
            run([
                "sqlmap", "-u", f"{base_url}/search?id=1",
                "--batch", "--flush-session", "--technique=B",
                "--level=1", "--risk=1", "--threads=1",
                "--timeout=2", "--retries=0",
                "--disable-coloring", "--output-dir", str(sqlmap_output),
            ], timeout=90)
            with request_lock:
                sqlmap_requests = [path for path in requests if path.startswith("/search?")]
            assert sqlmap_requests, "SQLmap did not send an HTTP request to the loopback fixture"

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
            "enumeration, ffuf content discovery, SQLmap HTTP parameter testing"
            + (", and Nuclei template matching." if shutil.which("nuclei") else ".")
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
