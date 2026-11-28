"""Rate-limit defaults stay production-safe while the isolated UI server can run full suites."""
from __future__ import annotations

from whaxon.core import Core
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, _default_rate_limits, create_app


def test_default_rate_limit_remains_200_per_minute():
    assert _default_rate_limits(
        host="127.0.0.1", auth_disabled=False, test_override=False,
    ) == ["200 per minute"]
    assert _default_rate_limits(
        host="127.0.0.1", auth_disabled=True, test_override=False,
    ) == ["200 per minute"]


def test_test_rate_limit_override_requires_loopback_and_auth_disabled():
    assert _default_rate_limits(
        host="127.0.0.1", auth_disabled=True, test_override=True,
    ) == ["10000 per minute"]
    assert _default_rate_limits(
        host="0.0.0.0", auth_disabled=True, test_override=True,
    ) == ["200 per minute"]
    assert _default_rate_limits(
        host="127.0.0.1", auth_disabled=False, test_override=True,
    ) == ["200 per minute"]


def test_test_global_override_preserves_endpoint_specific_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_HOST", "127.0.0.1")
    monkeypatch.setenv("WHAXON_AUTH_DISABLED", "1")
    monkeypatch.setenv("WHAXON_TEST_RATE_LIMITS", "1")

    core = Core(tmp_path)
    app = create_app(core, JobRegistry(core), AsyncRunner(core))
    assert app.config["WHAXON_DEFAULT_RATE_LIMITS"] == ("10000 per minute",)

    client = app.test_client()
    statuses = [
        client.post("/api/v2/ai/proposals", json={}).status_code
        for _ in range(11)
    ]
    assert statuses == [400] * 10 + [429]


def test_environment_flag_does_not_change_production_default(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_HOST", "127.0.0.1")
    monkeypatch.setenv("WHAXON_AUTH_DISABLED", "1")
    monkeypatch.delenv("WHAXON_TEST_RATE_LIMITS", raising=False)

    core = Core(tmp_path)
    app = create_app(core, JobRegistry(core), AsyncRunner(core))

    assert app.config["WHAXON_DEFAULT_RATE_LIMITS"] == ("200 per minute",)
