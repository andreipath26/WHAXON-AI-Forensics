import json

import pytest

from whaxon.core.scope import OutOfScopeError, ScopeManager


@pytest.fixture
def scope_file(tmp_path):
    def _write(data):
        p = tmp_path / "scope.json"
        p.write_text(json.dumps(data))
        return p
    return _write


def test_missing_file_is_fail_closed(tmp_path):
    """Missing scope.json must NOT disable enforcement.

    The old behavior (enabled=False for a missing file) was a
    fail-open security hole; it was fixed on 2026-09-27. See
    tests/test_scope_failclosed.py for the exhaustive contract.
    """
    s = ScopeManager(tmp_path / "nonexistent.json")
    assert s.enabled is True
    assert s.check("10.0.0.5").allowed is True   # RFC1918 default
    assert s.check("evil.example.com").allowed is False

def test_disabled_scope_allows_everything(scope_file):
    s = ScopeManager(scope_file({"enabled": False, "in_scope": ["a.com"]}))
    assert s.check("b.com").allowed is True


def test_exact_host_in_scope(scope_file):
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["acme.com"]}))
    assert s.check("acme.com").allowed is True
    assert s.check("other.com").allowed is False


def test_wildcard_matches_subdomain(scope_file):
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["*.acme.com"]}))
    assert s.check("api.acme.com").allowed is True
    assert s.check("deep.api.acme.com").allowed is True
    assert s.check("acme.com").allowed is False


def test_out_of_scope_wins(scope_file):
    s = ScopeManager(scope_file({
        "enabled": True,
        "in_scope": ["*.acme.com"],
        "out_of_scope": ["prod.acme.com"],
    }))
    assert s.check("api.acme.com").allowed is True
    assert s.check("prod.acme.com").allowed is False
    assert s.check("prod.acme.com").matched_rule == "prod.acme.com"


def test_cidr_range(scope_file):
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["10.0.0.0/24"]}))
    assert s.check("10.0.0.5").allowed is True
    assert s.check("10.0.0.255").allowed is True
    assert s.check("10.0.1.1").allowed is False


def test_ip_out_of_range(scope_file):
    s = ScopeManager(scope_file({
        "enabled": True,
        "in_scope": ["10.0.0.0/24"],
        "out_of_scope": ["10.0.0.1"],
    }))
    assert s.check("10.0.0.5").allowed is True
    assert s.check("10.0.0.1").allowed is False


def test_url_normalized(scope_file):
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["acme.com"]}))
    assert s.check("https://acme.com/path").allowed is True
    assert s.check("http://api.acme.com").allowed is False


def test_host_with_port(scope_file):
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["acme.com"]}))
    assert s.check("acme.com:8080").allowed is True


def test_cidr_rule_matches_url_target(scope_file):
    """Regression: a URL whose host is an IP literal must match CIDR rules.

    scope --check allowed a bare `127.0.0.1` but denied
    `http://127.0.0.1:8099/ping`, because CIDR matching only ran for
    targets whose kind was "ip" and a URL was classified as "url".
    """
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["127.0.0.0/8"]}))
    assert s.check("http://127.0.0.1:8099/ping?ip=1").allowed is True
    assert s.check("http://127.0.0.1:8099/ping?ip=1").matched_rule == "127.0.0.0/8"
    assert s.check("https://10.1.2.3/admin").allowed is False


def test_cidr_out_of_scope_denies_url_target(scope_file):
    """The deny path matters as much as the allow path."""
    s = ScopeManager(scope_file({
        "enabled": True,
        "in_scope": ["10.0.0.0/8"],
        "out_of_scope": ["10.9.0.0/16"],
    }))
    assert s.check("http://10.1.1.1/x").allowed is True
    assert s.check("http://10.9.1.1/x").allowed is False
    assert s.check("http://10.9.1.1/x").matched_rule == "10.9.0.0/16"


def test_ipv6_url_matches_cidr_rule(scope_file):
    s = ScopeManager(scope_file({
        "enabled": True,
        "in_scope": ["::1", "fc00::/7"],
        "out_of_scope": ["2001:db8::/32"],
    }))
    assert s.check("http://[::1]:8080/x").allowed is True
    assert s.check("http://[fd00::1]/x").allowed is True
    assert s.check("http://[2001:db8::1]/x").allowed is False


def test_hostname_url_is_not_matched_by_cidr(scope_file):
    s = ScopeManager(scope_file({"enabled": True, "in_scope": ["10.0.0.0/8"]}))
    assert s.check("http://acme.com/").allowed is False


def test_default_scope_allows_loopback_and_rfc1918_urls(tmp_path):
    """The auto-written default scope is CIDR-only, so URLs must match it."""
    s = ScopeManager(tmp_path / "scope.json")
    assert s.check("http://127.0.0.1:8099/").allowed is True
    assert s.check("http://192.168.1.10:80/").allowed is True
    assert s.check("https://pentest-ground.com:4280/").allowed is False


def test_runner_refuses_out_of_scope(scope_file):
    """Integration: runner raises OutOfScopeError when scope forbids the target."""
    import asyncio

    from whaxon.core.events import EventBus
    from whaxon.core.runner import ToolRunner

    bus = EventBus()
    scope = ScopeManager(scope_file({"enabled": True, "in_scope": ["allowed.com"]}))
    runner = ToolRunner(bus, catalog=None, scope=scope)

    with pytest.raises(OutOfScopeError):
        asyncio.run(runner.run_tool("echo", "forbidden.com"))
