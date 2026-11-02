"""Labeled local benchmark server with DVWA-like response semantics.

Why this exists
---------------
The authorised target's DVWA database is not initialised (login redirects to
setup.php), so stateful modules such as `sqli` cannot be exercised there. To
measure WHAXON's replay validator against *known* ground truth we need
endpoints whose vulnerability status is defined by construction, not by a
scanner's opinion.

Each endpoint below implements a documented DVWA security-level behaviour:

    low        input concatenated with no filtering
    medium     `<script>` stripped (DVWA medium XSS), numeric-only filter (DVWA medium SQLi)
    high       htmlspecialchars / mysqli_real_escape_string equivalents

Ground truth per case is asserted by tests/test_benchmark_labels.py, which
checks the *actual* attacker capability (marker reflected raw, error string
produced, marker executed, file disclosed) rather than the server's own label.

Every request is appended to evidence/benchmark/access-log.jsonl so a reader can
confirm what the validator actually contacted.
"""
from __future__ import annotations

import html
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ACCESS_LOG = Path("evidence/benchmark/access-log.jsonl")
_LOCK = threading.Lock()

# ---------------------------------------------------------------- ground truth
CASES = {
    "xss_low": {
        "vulnerable": True, "kind": "xss", "method": "GET", "param": "name",
        "cwe": "CWE-79", "note": "raw reflection of the submitted value into <pre>",
    },
    "xss_high": {
        "vulnerable": False, "kind": "xss", "method": "GET", "param": "name",
        "cwe": "CWE-79", "note": "htmlspecialchars() encoding, as DVWA high",
    },
    "xss_no_reflection": {
        "vulnerable": False, "kind": "xss", "method": "GET", "param": "name",
        "cwe": "CWE-79", "note": "value never echoed; a stable page",
    },
    "sqli_low": {
        "vulnerable": True, "kind": "sqli", "method": "GET", "param": "id",
        "cwe": "CWE-89", "note": "concatenated query; MySQL syntax error on quote",
    },
    "sqli_medium": {
        "vulnerable": False, "kind": "sqli", "method": "GET", "param": "id",
        "cwe": "CWE-89", "note": "numeric-only filter, as DVWA medium",
    },
    "sqli_union": {
        "vulnerable": True, "kind": "sqli", "method": "GET", "param": "id",
        "cwe": "CWE-89", "note": "UNION injection returns rows with no error text",
    },
    "cmdi_get": {
        "vulnerable": True, "kind": "command_injection", "method": "GET", "param": "ip",
        "cwe": "CWE-78", "note": "shell concatenation; canary is actually executed",
    },
    "cmdi_post": {
        "vulnerable": True, "kind": "command_injection", "method": "POST", "param": "ip",
        "cwe": "CWE-78", "note": "shell concatenation, POST-only endpoint",
    },
    "cmdi_safe": {
        "vulnerable": False, "kind": "command_injection", "method": "GET", "param": "ip",
        "cwe": "CWE-78", "note": "escapeshellarg(); separator is inert",
    },
    "lfi_low": {
        "vulnerable": True, "kind": "lfi", "method": "GET", "param": "page",
        "cwe": "CWE-98", "note": "arbitrary file read via include()",
    },
    "timing_decoy": {
        "vulnerable": False, "kind": "sqli", "method": "GET", "param": "id",
        "cwe": "CWE-89", "note": "NOT injectable; sleeps 3.2 s on any non-baseline value",
    },
    "marker_decoy": {
        "vulnerable": False, "kind": "sqli", "method": "GET", "param": "id",
        "cwe": "CWE-89", "note": "NOT injectable; prints a DB-driver word only for non-baseline values",
    },
}

PAGE = "<html><body><h1>benchmark case {case}</h1>{body}</body></html>"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):          # silence default stderr logging
        pass

    def _record(self, method: str, path: str, query: dict, body: str, status: int) -> None:
        ACCESS_LOG.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "method": method, "path": path, "status": status,
               "query": {k: v[:300] for k, v in query.items()},
               "body": body[:300]}
        with _LOCK:
            with ACCESS_LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")

    def _send(self, status: int, body: str) -> None:
        raw = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(parsed.query, keep_blank_values=True).items()}
        self._handle("GET", parsed.path.strip("/"), q, "")

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        q = {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}
        q.update({k: v[0] for k, v in parse_qs(parsed.query, keep_blank_values=True).items()})
        self._handle("POST", parsed.path.strip("/"), q, raw)

    # ------------------------------------------------------------- endpoints
    def _handle(self, method: str, case: str, q: dict, raw_body: str) -> None:
        if case not in CASES:
            self._record(method, case, q, raw_body, 404)
            self._send(404, "not found")
            return
        spec = CASES[case]
        value = q.get(spec["param"], "")
        body = self._dispatch(case, method, value)
        status = 200
        self._record(method, case, q, raw_body, status)
        self._send(status, PAGE.format(case=case, body=body))

    def _dispatch(self, case: str, method: str, value: str) -> str:
        if case == "xss_low":
            return f"<pre>Hello {value}</pre>"
        if case == "xss_high":
            return f"<pre>Hello {html.escape(value, quote=True)}</pre>"
        if case == "xss_no_reflection":
            return "<p>Static content only.</p>"
        if case == "sqli_low":
            if "'" in value or '"' in value:
                return ("<br /><pre>Fatal error: Uncaught mysqli_sql_exception: "
                        "You have an error in your SQL syntax; check the manual that "
                        "corresponds to your MySQL server version</pre>")
            return f"<p>ID: {value} :: First name: admin</p>"
        if case == "sqli_medium":
            if not re.fullmatch(r"\d+", value or ""):
                return "<p>ID: 1 :: First name: admin</p>"      # silently coerced
            return f"<p>ID: {value} :: First name: admin</p>"
        if case == "sqli_union":
            if re.search(r"union\s+select", value or "", re.I):
                return "<p>ID: 1 :: First name: admin</p><p>5 :: 5</p>"
            return "<p>ID: 1 :: First name: admin</p>"
        if case in ("cmdi_get", "cmdi_post"):
            # cmdi_post only reads POST input, so a GET carrying the payload must
            # not execute anything; cmdi_get reads GET input only.
            restricted = (case == "cmdi_post" and method != "POST") or \
                         (case == "cmdi_get" and method == "POST")
            return self._shell(value, restricted=restricted)
        if case == "cmdi_safe":
            return f"<pre>ping -c 4 '{value}'</pre><p>64 bytes from 127.0.0.1</p>"
        if case == "lfi_low":
            if not value:
                return "<p>?page= required</p>"
            try:
                return "<pre>" + Path(value).read_text(errors="replace")[:2000] + "</pre>"
            except OSError:
                return "<p>include failed</p>"
        if case == "timing_decoy":
            if value and value != "whaxon_baseline":
                time.sleep(3.2)
            return "<p>ID: 1 :: First name: admin</p>"
        if case == "marker_decoy":
            if value and value != "whaxon_baseline":
                return "<p>Database driver error: postgresql backend unavailable</p>"
            return "<p>ID: 1 :: First name: admin</p>"
        return "<p>unknown case</p>"

    @staticmethod
    def _shell(value: str, restricted: bool = False) -> str:
        """Emulate `shell_exec("ping -c 4 " . value)` including real execution.

        Supports the two canary forms WHAXON generates:
            x;echo whaxon_cmdi_$(printf <hex>)
            x;echo whaxon_cmdi_abcd""efgh
        so that the canary only appears when the injection point is live.
        """
        out = ""
        if not restricted and ";" in value:
            cmd = value.split(";", 1)[1]
            m = re.search(r"echo\s+(whaxon_cmdi_(?:\$\(printf\s+([0-9a-fA-F]+)\)|([0-9a-f]{4})\"\"([0-9a-f]{4})))", cmd)
            if m:
                # `printf <hex>` prints the hex text literally; the second form
                # relies on shell quote removal joining two halves.
                token = m.group(2) if m.group(2) else m.group(3) + m.group(4)
                out += f"<pre>whaxon_cmdi_{token}</pre>"
        out += "<pre>PING 127.0.0.1 (127.0.0.1): 56 data bytes</pre>"
        if not restricted and value.startswith("127.0.0.1"):
            out += "<pre>64 bytes from 127.0.0.1</pre>"
        return out


def serve(port: int = 0) -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


if __name__ == "__main__":
    s = serve(8099)
    print(f"benchmark server on http://127.0.0.1:{s.server_address[1]}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        s.shutdown()
