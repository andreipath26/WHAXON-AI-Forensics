"""Regression tests for conservative HTTP validation replay safety."""

from pathlib import Path

import pytest

from whaxon.core.findings import Finding
from whaxon.core.validator import Validator


def test_context_replay_refuses_state_changing_methods(tmp_path: Path) -> None:
    validator = Validator(tmp_path)
    status, reason = validator._replay_ctx(
        {"method": "DELETE", "url": "https://example.test/item/1"},
        target_url="https://example.test",
        kind="sqli",
    )
    assert status == "candidate"
    assert "may change target state" in reason


def test_context_replay_refuses_post_until_explicit_safe_replay_exists(
    tmp_path: Path,
) -> None:
    validator = Validator(tmp_path)
    status, reason = validator._replay_ctx(
        {"method": "POST", "url": "https://example.test/search", "body": "q=test"},
        target_url="https://example.test",
        kind="sqli",
    )
    assert status == "candidate"
    assert "may change target state" in reason


def test_context_replay_rejects_non_http_urls(tmp_path: Path) -> None:
    validator = Validator(tmp_path)
    status, reason = validator._replay_ctx(
        {"method": "GET", "url": "file:///etc/passwd"},
        target_url="https://example.test",
        kind="sqli",
    )
    assert status == "candidate"
    assert "absolute HTTP(S)" in reason


def test_context_replay_rejects_credentials_embedded_in_url(tmp_path: Path) -> None:
    validator = Validator(tmp_path)
    status, reason = validator._replay_ctx(
        {"method": "GET", "url": "https://user:secret@example.test/search"},
        target_url="https://example.test",
        kind="sqli",
    )
    assert status == "candidate"
    assert "must not embed credentials" in reason


def test_context_replay_rejects_different_target_host(tmp_path: Path) -> None:
    validator = Validator(tmp_path)
    status, reason = validator._replay_ctx(
        {"method": "GET", "url": "https://other.example.test/search?q=test"},
        target_url="https://example.test",
        kind="sqli",
    )
    assert status == "candidate"
    assert "does not match the authorized target" in reason



def test_context_replay_requires_authorized_target_before_network(
    tmp_path: Path, monkeypatch,
) -> None:
    import urllib.request

    def unexpected_network(*args, **kwargs):
        pytest.fail("context replay must not make a request without an authorized target")

    monkeypatch.setattr(urllib.request, "build_opener", unexpected_network)
    validator = Validator(tmp_path)
    status, reason = validator._replay_ctx(
        {"method": "GET", "url": "http://127.0.0.1:9/"},
        target_url=None,
        kind="sqli",
    )
    assert status == "candidate"
    assert "authorized target URL required" in reason
    assert "no request sent" in reason

    finding = Finding(
        kind="sqli",
        severity="high",
        source="test",
        data={"parameter": "q", "_request_context": {
            "method": "GET", "url": "http://127.0.0.1:9/", "parameter": "q",
        }},
        raw_line="",
    )
    status, reason = validator.validate(finding, target_url=None)
    assert status == "candidate"
    assert "authorized target URL required" in reason
    assert "no request sent" in reason


def test_query_fetch_rejects_non_http_urls() -> None:
    with pytest.raises(ValueError, match="absolute HTTP"):
        Validator._fetch("file:///etc/passwd", "q", "test")


@pytest.mark.parametrize("fields", [
    {"method": 5}, {"method": None}, {"headers": []},
    {"headers": {"X-Test": 7}}, {"headers": {"Bad Header": "value"}},
    {"headers": {"X-Test": "first\r\nsecond"}},
    {"parameter": []}, {"body": {}},
    {"url": "http://127.0.0.1:bad/"}, {"url": "http://[invalid]/"},
    {"url": "http://127.0.0.1:0/"}, {"url": "http://127.0.0.1/#fragment"},
])
def test_malformed_context_rejected_before_network(tmp_path, monkeypatch, fields):
    import urllib.request

    def forbidden(*args, **kwargs):
        pytest.fail("invalid context must not open a transport")

    monkeypatch.setattr(urllib.request, "build_opener", forbidden)
    validator = Validator(tmp_path)
    validator.last_payload = "previous-proof"
    finding = Finding(
        kind="sqli", severity="high", source="fixture",
        data={"parameter": "id"},
        request_context={"url": "http://127.0.0.1/", "method": "GET", **fields},
    )
    status, _ = validator.validate(finding, target_url="http://127.0.0.1/")
    assert status == "candidate"
    assert validator.last_payload is None


@pytest.mark.parametrize("url", [
    "https://127.0.0.1:80/", "http://127.0.0.1:81/",
    "http://127.0.0.2/", "http://127.0.0.1:invalid/",
    "http://user@127.0.0.1/", 42,
])
def test_observation_origin_mismatch_rejected_before_network(tmp_path, monkeypatch, url):
    import urllib.request

    def forbidden(*args, **kwargs):
        pytest.fail("invalid observation origin must not open a transport")

    monkeypatch.setattr(urllib.request, "build_opener", forbidden)
    finding = Finding(
        kind="http_header_missing", severity="low", source="fixture",
        data={"header": "Content-Security-Policy", "url": url},
    )
    validator = Validator(tmp_path)
    assert validator.validate(finding, "http://127.0.0.1/")[0] == "candidate"
    assert validator.revalidate(finding, "http://127.0.0.1/")[0] == "inconclusive"


def test_replay_rejects_same_port_different_scheme(tmp_path, monkeypatch):
    import urllib.request

    def forbidden(*args, **kwargs):
        pytest.fail("cross-origin replay must not open a transport")

    monkeypatch.setattr(urllib.request, "build_opener", forbidden)
    status, _ = Validator(tmp_path)._replay_ctx(
        {"url": "https://127.0.0.1:80/", "method": "GET"},
        target_url="http://127.0.0.1/", kind="sqli",
    )
    assert status == "candidate"


def test_invalid_canonical_context_does_not_fall_back(tmp_path, monkeypatch):
    import urllib.request

    def forbidden(*args, **kwargs):
        pytest.fail("invalid canonical context must not fall back to a network request")

    monkeypatch.setattr(urllib.request, "build_opener", forbidden)
    finding = Finding(
        kind="sqli", severity="high", source="fixture",
        data={"parameter": "id", "_request_context": {"url": "http://127.0.0.1/"}},
        request_context={"method": "GET"},
    )
    assert Validator(tmp_path).validate(finding, "http://127.0.0.1/")[0] == "candidate"


def test_all_http_validation_paths_ignore_ambient_proxy(tmp_path, monkeypatch):
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Target(BaseHTTPRequestHandler):
        requests = 0

        def do_GET(self):
            type(self).requests += 1
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"fixture")

        def log_message(self, *_args):
            pass

    class Proxy(Target):
        requests = 0

    target = HTTPServer(("127.0.0.1", 0), Target)
    proxy = HTTPServer(("127.0.0.1", 0), Proxy)
    threads = [
        threading.Thread(target=server.serve_forever, daemon=True)
        for server in (target, proxy)
    ]
    for thread in threads:
        thread.start()
    try:
        url = f"http://127.0.0.1:{target.server_port}/"
        proxy_url = f"http://127.0.0.1:{proxy.server_port}"
        for name in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
            monkeypatch.setenv(name, proxy_url)
        for name in ("no_proxy", "NO_PROXY"):
            monkeypatch.setenv(name, "")
        validator = Validator(tmp_path)
        assert validator._fetch(url, "id", "fixture")[0] == "fixture"
        validator._replay_ctx({"url": url, "method": "GET", "parameter": "id"}, url, "sqli")
        finding = Finding(
            kind="http_header_missing", severity="low", source="fixture",
            data={"header": "Content-Security-Policy", "url": url},
        )
        assert validator.validate(finding, url)[0] == "verified"
        assert Target.requests == 8
        assert Proxy.requests == 0
    finally:
        for server in (target, proxy):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=5)
