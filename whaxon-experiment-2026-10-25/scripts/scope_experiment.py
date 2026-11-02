"""E10/E11 — what does WHAXON's scope boundary actually bound?

Two separate questions, kept separate because their answers differ:

E10 (decision matrix) — given a scope file, which target *strings* are allowed,
    and does the decision depend on the address the name resolves to? A matrix
    of normalised forms is evaluated through WHAXON's own `ScopeManager`.

E11 (destination binding) — when the allowed target is a live host that answers
    with a redirect, does the request that follows stay inside scope? Tested with
    two loopback addresses: 127.0.0.1 is in scope, 127.0.0.2 is explicitly out
    of scope. Server A (in scope) redirects to server B (out of scope). Server B
    records whether it was contacted.

    Both WHAXON paths are exercised:
      * `Runner.run_tool` with a catalog entry that follows redirects (curl -L),
        which is how an operator-run tool behaves; and
      * `Validator._fetch`, the replay path.

Safety: entirely local. No traffic leaves the VM; both addresses are loopback.
"""
from __future__ import annotations

import asyncio
import json
import socket
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from whaxon.core.catalog import ToolCatalog                     # noqa: E402
from whaxon.core.events import EventBus                        # noqa: E402
from whaxon.core.findings import Finding                        # noqa: E402
from whaxon.core.runner import ToolRunner                           # noqa: E402
from whaxon.core.scope import ScopeManager                      # noqa: E402
from whaxon.core.validator import Validator                     # noqa: E402

OUT = ROOT / "evidence" / "scope"
B_HITS: list[dict] = []
A_HITS: list[dict] = []


class Redirector(BaseHTTPRequestHandler):
    """Server A — in scope. Answers every GET with a redirect to server B."""
    protocol_version = "HTTP/1.1"
    target = ""      # set at runtime

    def log_message(self, *a):
        pass

    def do_GET(self):
        A_HITS.append({"server": "A(127.0.0.1,in-scope)", "path": self.path,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        self.send_response(302)
        self.send_header("Location", Redirector.target)
        self.send_header("Content-Length", "0")
        self.end_headers()


class Sink(BaseHTTPRequestHandler):
    """Server B — explicitly out of scope. Records any contact."""
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_GET(self):
        B_HITS.append({"server": "B(127.0.0.2,OUT-of-scope)", "path": self.path,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        body = b"out-of-scope server was contacted\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(handler, host: str) -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer((host, 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def decision_matrix(tmp: Path) -> dict:
    scope_path = tmp / "scope.json"
    scope_path.write_text(json.dumps({
        "engagement": "E10 matrix",
        "enabled": True,
        "in_scope": ["127.0.0.1/32", "*.example.test", "example.com"],
        "out_of_scope": ["127.0.0.2"],
        "notes": "synthetic scope used only for this offline experiment",
    }))
    sm = ScopeManager(scope_path)
    targets = [
        "http://127.0.0.1:8098/",
        "http://127.0.0.2:8098/",
        "127.0.0.1",
        "127.0.0.1:8098",
        "http://127.0.0.1./",
        "http://2130706433/",                  # 127.0.0.1 in decimal
        "http://0x7f000001/",                  # 127.0.0.1 in hex
        "http://[::ffff:127.0.0.1]/",          # IPv4-mapped IPv6
        "http://127.0.0.1@evil.test/",         # userinfo confusion
        "http://evil.test#@127.0.0.1/",        # fragment confusion
        "https://api.example.test/x",
        "https://example.com/",
        "http://localhost:8098/",
        "http://127.0.0.2.nip.io/",            # public wildcard DNS -> 127.0.0.2
    ]
    rows = []
    for t in targets:
        m = sm.check(t)
        rows.append({"target": t, "allowed": m.allowed, "reason": m.reason,
                     "matched_rule": m.matched_rule})
    # Does the decision consult DNS at all? Resolve a name the matrix allows and
    # compare the address with the CIDR rules.
    name = "example.com"
    try:
        resolved = sorted({ai[4][0] for ai in socket.getaddrinfo(name, None, socket.AF_INET)})
    except OSError as exc:
        resolved = [f"resolution failed: {exc}"]
    addrs_in_scope = []
    for ip in resolved:
        addrs_in_scope.append({"ip": ip, "allowed_by_rule": sm.check(ip).allowed})
    return {"scope_file": json.loads(scope_path.read_text()), "matrix": rows,
            "dns_binding_probe": {"name": name, "resolved": resolved,
                                  "addresses_allowed_by_rules": addrs_in_scope,
                                  "name_allowed": sm.check(f"https://{name}/").allowed}}


async def redirect_escape(tmp: Path) -> dict:
    a = serve(Redirector, "127.0.0.1")
    b = serve(Sink, "127.0.0.2")
    port_a, port_b = a.server_address[1], b.server_address[1]
    Redirector.target = f"http://127.0.0.2:{port_b}/escaped"

    # Scope: A allowed, B explicitly denied.
    scope_path = tmp / "scope_escape.json"
    scope_path.write_text(json.dumps({
        "engagement": "E11 redirect escape", "enabled": True,
        "in_scope": ["127.0.0.1/32"], "out_of_scope": ["127.0.0.2"],
    }))
    sm = ScopeManager(scope_path)
    check_in = sm.check(f"http://127.0.0.1:{port_a}/start").to_dict()
    check_out = sm.check(f"http://127.0.0.2:{port_b}/escaped").to_dict()

    # Catalog entry: a tool that follows redirects (curl -L), the behaviour of
    # most HTTP-capable scanners.
    cat_path = tmp / "tools.json"
    cat_path.write_text(json.dumps({"tools": [{
        "id": "curl-follow", "name": "curl (redirect-following)", "category": "web",
        "binary": "curl", "description": "test tool", "args": "-s -L --max-time 10 {target}",
        "package": "curl",
    }]}))
    bus = EventBus()
    catalog = ToolCatalog(bus, cat_path)
    catalog.load()
    runner = ToolRunner(bus, catalog=catalog, scope=sm)

    result: dict = {"check_in_scope": check_in, "check_out_of_scope": check_out,
                    "port_a": port_a, "port_b": port_b}
    try:
        job = await runner.run_tool("curl-follow", f"http://127.0.0.1:{port_a}/start",
                                    timeout_s=30)
        await asyncio.sleep(0.3)
        lines = runner._lines_by_job.get(job, [])
        result["runner_job"] = job
        result["runner_output"] = [t for _s, t in lines][:10]
    except Exception as exc:
        result["runner_error"] = f"{type(exc).__name__}: {exc}"

    # Control: does the scope checker refuse B directly?
    try:
        await runner.run_tool("curl-follow", f"http://127.0.0.2:{port_b}/escaped", timeout_s=15)
        result["direct_out_of_scope_run"] = "NOT BLOCKED (unexpected)"
    except Exception as exc:
        result["direct_out_of_scope_run"] = f"blocked: {type(exc).__name__}: {exc}"

    # Validator replay path against the same redirector.
    v = Validator(ROOT / "src" / "whaxon" / "data" / "payloads")
    try:
        v._fetch(f"http://127.0.0.1:{port_a}/start", "q", "whaxon_baseline")
        result["validator_fetch"] = "followed redirect (unexpected)"
    except Exception as exc:
        result["validator_fetch"] = f"{type(exc).__name__}: {exc}"

    time.sleep(0.2)
    result["server_a_requests"] = A_HITS
    result["server_b_requests"] = B_HITS
    result["scope_escaped_via_runner"] = len(B_HITS) > 0
    a.shutdown(); b.shutdown()
    return result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="whaxon-scope-"))
    matrix = decision_matrix(tmp)
    escape = asyncio.run(redirect_escape(tmp))
    (OUT / "decision-matrix.json").write_text(json.dumps(matrix, indent=2))
    (OUT / "redirect-escape.json").write_text(json.dumps(escape, indent=2))

    print("== E10 decision matrix ==")
    for r in matrix["matrix"]:
        print(f"  {'ALLOW' if r['allowed'] else 'deny ':5s} {r['target']:34s} "
              f"{r['reason']}{('/' + r['matched_rule']) if r['matched_rule'] else ''}")
    print("  dns:", json.dumps(matrix["dns_binding_probe"]))
    print("\n== E11 redirect escape ==")
    print("  in-scope check :", escape["check_in_scope"])
    print("  out-scope check:", escape["check_out_of_scope"])
    print("  runner output  :", escape.get("runner_output"))
    print("  direct B run   :", escape.get("direct_out_of_scope_run"))
    print("  validator fetch:", escape["validator_fetch"])
    print("  A hits:", len(escape["server_a_requests"]),
          "| B hits:", len(escape["server_b_requests"]),
          "| escaped:", escape["scope_escaped_via_runner"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
