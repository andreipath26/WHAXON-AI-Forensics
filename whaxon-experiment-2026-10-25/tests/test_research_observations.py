"""Characterisation and ground-truth tests for the WHAXON forensics study.

Two kinds of test, deliberately separated:

* **ground-truth tests** assert what the *benchmark* and the *target* actually do,
  using raw HTTP clients that do not share code with WHAXON. They protect the
  labels the study scores against.
* **characterisation tests** pin behaviour of the current WHAXON release. They are
  not claims that the behaviour is desirable: several pin *defects* so that a
  future fix will make them fail loudly and force the study's numbers to be
  recomputed rather than silently invalidated.
"""
from __future__ import annotations

import json
import socket
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from experiments.benchmark.server import CASES, serve            # noqa: E402
from whaxon.adapters.ffuf import FfufAdapter                     # noqa: E402
from whaxon.core.findings import Finding                         # noqa: E402
from whaxon.core.scope import ScopeManager                       # noqa: E402
from whaxon.core.validator import Validator                      # noqa: E402

PAYLOADS = ROOT / "src" / "whaxon" / "data" / "payloads"


# --------------------------------------------------------------------- fixtures
@pytest.fixture(scope="module")
def benchmark():
    srv = serve(0)
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def http_get(url: str, timeout: float = 15) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


# ------------------------------------------------------- benchmark ground truth
@pytest.mark.parametrize("case,spec", list(CASES.items()))
def test_benchmark_ground_truth_matches_label(benchmark, case, spec):
    """The label must be earned by behaviour, not asserted by the case name.

    A positive label requires an attacker-observable capability. A negative label
    requires that the capability is absent.
    """
    param = spec["param"]
    if spec["method"] == "POST":
        import urllib.parse
        data = urllib.parse.urlencode({param: "POSTONLY"}).encode()
        req = urllib.request.Request(f"{benchmark}/{case}", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8", "replace")
    else:
        _, body = http_get(f"{benchmark}/{case}?{param}=probe")

    if case == "xss_low":
        _, reflected = http_get(f"{benchmark}/{case}?{param}=<script>x</script>")
        assert spec["vulnerable"] and "<script>x</script>" in reflected
    elif case == "xss_high":
        _, reflected = http_get(f"{benchmark}/{case}?{param}=<script>x</script>")
        assert not spec["vulnerable"] and "<script>x</script>" not in reflected
        assert "&lt;script&gt;" in reflected
    elif case == "xss_no_reflection":
        assert not spec["vulnerable"] and "probe" not in body
    elif case == "sqli_low":
        _, err = http_get(f"{benchmark}/{case}?{param}=1%27")
        assert spec["vulnerable"] and "SQL syntax" in err
    elif case == "sqli_medium":
        _, err = http_get(f"{benchmark}/{case}?{param}=1%27")
        assert not spec["vulnerable"] and "SQL syntax" not in err
    elif case == "sqli_union":
        _, rows = http_get(f"{benchmark}/{case}?{param}=1%20UNION%20SELECT%205")
        assert spec["vulnerable"] and "5 :: 5" in rows
    elif case == "cmdi_get":
        _, out = http_get(f"{benchmark}/{case}?{param}=x;echo%20whaxon_cmdi_$(printf%20deadbeef)")
        assert spec["vulnerable"] and "whaxon_cmdi_deadbeef" in out
    elif case == "cmdi_post":
        import urllib.parse
        data = urllib.parse.urlencode({param: "x;echo whaxon_cmdi_$(printf cafebabe)"}).encode()
        req = urllib.request.Request(f"{benchmark}/{case}", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            out = r.read().decode("utf-8", "replace")
        assert spec["vulnerable"] and "whaxon_cmdi_cafebabe" in out
        _, via_get = http_get(f"{benchmark}/{case}?{param}=x;echo%20whaxon_cmdi_$(printf%2000000000)")
        assert "whaxon_cmdi_00000000" not in via_get, "GET must not reach a POST-only sink"
    elif case == "cmdi_safe":
        _, out = http_get(f"{benchmark}/{case}?{param}=x;echo%20whaxon_cmdi_$(printf%2012345678)")
        assert not spec["vulnerable"] and "whaxon_cmdi_12345678" not in out
    elif case == "lfi_low":
        _, disclosed = http_get(f"{benchmark}/{case}?{param}=/etc/hostname")
        assert spec["vulnerable"] and "include failed" not in disclosed
        assert len(disclosed) > 0
    elif case == "timing_decoy":
        import time
        t0 = time.monotonic()
        _, body = http_get(f"{benchmark}/{case}?{param}=1")
        assert not spec["vulnerable"]
        assert time.monotonic() - t0 >= 3.0, "decoy must actually be slow, else it tests nothing"
        assert "SQL syntax" not in body
    elif case == "marker_decoy":
        _, body = http_get(f"{benchmark}/{case}?{param}=1")
        assert not spec["vulnerable"] and "postgresql" in body.lower()
        assert "SQL syntax" not in body


# ------------------------------------------------------- characterisation: ffuf
def test_ffuf_adapter_invents_status_200_when_input_has_none():
    """ffuf's silent mode emits bare paths; the adapter fills in status=200."""
    findings = FfufAdapter().parse([("stdout", "admin\n")])
    assert len(findings) == 1
    assert findings[0].data == {"path": "admin", "status": 200, "size": None}
    assert findings[0].severity == "low"


def test_ffuf_adapter_preserves_status_when_present():
    findings = FfufAdapter().parse([("stdout", "secret [Status: 403, Size: 289]\n")])
    assert findings[0].data["status"] == 403
    assert findings[0].data["size"] == 289


def test_shipped_proof_artefact_contains_cross_tool_status_contradiction():
    """The repository's own DVWA proof run disagrees with itself on the same paths."""
    data = json.loads((ROOT / "data" / "proof-dvwa" / "engagement.json").read_text())
    per_tool: dict[str, dict[str, int]] = {}
    for job in data.get("jobs", []):
        tool = job.get("job", {}).get("tool")
        for f in job.get("findings", []):
            if f.get("kind") == "found_path":
                per_tool.setdefault(tool, {})[f["data"]["path"]] = f["data"].get("status")
    ffuf, gob = per_tool.get("ffuf", {}), per_tool.get("gobuster", {})
    shared = set(ffuf) & set(gob)
    assert shared, "expected overlapping paths"
    disagreements = {p for p in shared if ffuf[p] != gob[p]}
    assert disagreements, "expected at least one status disagreement"
    # Every ffuf status in this artefact is the invented 200 default.
    assert set(ffuf.values()) == {200}


# --------------------------------------------------- characterisation: validator
def test_validator_verifies_when_only_a_database_word_differs(benchmark):
    """A page that merely prints 'postgresql' for non-baseline input is 'verified'."""
    v = Validator(PAYLOADS)
    f = Finding(kind="sqli", severity="info", source="t",
                data={"parameter": "id"}, raw_line="x")
    status, reason = v.validate(f, target_url=f"{benchmark}/marker_decoy")
    assert status == "verified", reason
    assert "postgresql" in reason


def test_validator_refutes_a_genuine_union_injection(benchmark):
    """A real UNION SQLi is labelled 'refuted' because the replayed payload is not one."""
    v = Validator(PAYLOADS)
    f = Finding(kind="sqli", severity="info", source="t",
                data={"parameter": "id"}, raw_line="x")
    status, reason = v.validate(f, target_url=f"{benchmark}/sqli_union")
    assert status == "refuted", reason


def test_validator_legacy_path_accepts_a_pure_timing_signal(benchmark):
    """Timing alone yields 'verified' on the legacy path (documented risk, measured here)."""
    v = Validator(PAYLOADS, timing_threshold=1.0)
    f = Finding(kind="sqli", severity="info", source="t",
                data={"parameter": "id"}, raw_line="x")
    status, reason = v.validate(f, target_url=f"{benchmark}/timing_decoy")
    assert status == "verified" and "timing delta" in reason


def test_validator_cannot_replay_post_only_findings(benchmark):
    v = Validator(PAYLOADS)
    f = Finding(kind="command_injection", severity="info", source="t",
                data={"parameter": "ip"}, raw_line="x")
    status, _ = v.validate(f, target_url=f"{benchmark}/cmdi_post")
    assert status in ("candidate", "refuted")
    ctx = {"method": "POST", "url": f"{benchmark}/cmdi_post", "parameter": "ip",
           "body": "ip=1"}
    f2 = Finding(kind="command_injection", severity="info", source="t",
                 data={"parameter": "ip", "_request_context": ctx}, raw_line="x")
    status2, reason2 = v.validate(f2, target_url=f"{benchmark}/cmdi_post")
    assert status2 == "candidate" and "POST" in reason2


# ------------------------------------------------------------ characterisation: scope
def test_scope_denies_alternative_ip_encodings(tmp_path):
    p = tmp_path / "scope.json"
    p.write_text(json.dumps({"enabled": True, "in_scope": ["127.0.0.1/32"]}))
    sm = ScopeManager(p)
    for target in ("http://2130706433/", "http://0x7f000001/", "http://[::ffff:127.0.0.1]/"):
        assert sm.check(target).allowed is False, target
    assert sm.check("http://127.0.0.1./").allowed is True      # trailing dot normalised


def test_scope_authorises_a_name_without_binding_its_address(tmp_path):
    """The decision is made on the name; the resolved address is never consulted."""
    p = tmp_path / "scope.json"
    p.write_text(json.dumps({"enabled": True, "in_scope": ["example.com"]}))
    sm = ScopeManager(p)
    ips = {ai[4][0] for ai in socket.getaddrinfo("example.com", None, socket.AF_INET)}
    assert sm.check("https://example.com/").allowed is True
    for ip in ips:
        # Every address the name resolves to is OUTSIDE the declared scope.
        assert sm.check(ip).allowed is False


def test_redirect_moves_a_permitted_tool_request_out_of_scope(tmp_path):
    """A permitted target that redirects causes an out-of-scope host to be contacted."""
    hits: list[str] = []

    class Redirect(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        location = ""

        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", Redirect.location)
            self.send_header("Content-Length", "0")
            self.end_headers()

    class Sink(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_GET(self):
            hits.append(self.path)
            body = b"hit"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    a = ThreadingHTTPServer(("127.0.0.1", 0), Redirect)
    b = ThreadingHTTPServer(("127.0.0.2", 0), Sink)
    for srv in (a, b):
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        Redirect.location = f"http://127.0.0.2:{b.server_address[1]}/escaped"
        p = tmp_path / "scope.json"
        p.write_text(json.dumps({"enabled": True, "in_scope": ["127.0.0.1/32"],
                                 "out_of_scope": ["127.0.0.2"]}))
        sm = ScopeManager(p)
        start = f"http://127.0.0.1:{a.server_address[1]}/start"
        assert sm.check(start).allowed is True
        assert sm.check(Redirect.location).allowed is False
        # An HTTP client that follows redirects (as most scanners do) reaches B.
        with urllib.request.urlopen(start, timeout=10) as r:
            assert r.status == 200
        assert hits == ["/escaped"], "the out-of-scope host must have been contacted"
    finally:
        a.shutdown()
        b.shutdown()


def test_validator_blocks_redirects():
    """Independent control: the same redirect is refused by the replay path."""
    class Redirect(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.2:9/escaped")
            self.send_header("Content-Length", "0")
            self.end_headers()

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Redirect)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        v = Validator(PAYLOADS)
        with pytest.raises(ValueError, match="redirect blocked"):
            v._fetch(f"http://127.0.0.1:{srv.server_address[1]}/start", "q", "v")
    finally:
        srv.shutdown()
