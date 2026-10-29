"""Browser coverage for the read-only settings/API explorer."""
from __future__ import annotations

from whaxon.core import Core
from whaxon.interfaces.web.server import (
    AsyncRunner,
    JobRegistry,
    _redact_sensitive_settings,
    create_app,
)


def test_settings_explorer_loads_and_redacts_settings(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/settings")
    assert response is not None and response.status == 200
    page.wait_for_function("() => !document.querySelector('#settings-status')?.textContent.includes('Loading settings')")
    assert page.locator("#whaxon-live-settings").is_visible()
    assert page.locator("#settings-json").is_visible()
    refresh = page.get_by_role("button", name="Refresh settings")
    assert refresh.is_visible()
    refresh.click()
    page.wait_for_function("() => !document.querySelector('#settings-status')?.textContent.includes('Loading settings')")
    assert page.locator("#settings-status").get_attribute("aria-live") == "polite"
    visible = page.locator("body").inner_text()
    assert "svc_whaxon_probe" not in visible


def test_dashboard_links_to_settings_explorer(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="settings-and-api-explorer"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/settings"


def test_settings_redaction_recurses_through_nested_values():
    raw = {
        "api_key": "never-return-this",
        "service": {
            "client_secret": "also-private",
            "passphrase": "private-passphrase",
            "timeout_seconds": 10,
            "headers": [{"Authorization": "Bearer very-private", "Cookie": "session=private", "Accept": "application/json"}],
        },
        "items": [{"password": "hidden"}],
    }
    assert _redact_sensitive_settings(raw) == {
        "api_key": "[REDACTED]",
        "service": {
            "client_secret": "[REDACTED]",
            "passphrase": "[REDACTED]",
            "timeout_seconds": 10,
            "headers": [{"Authorization": "[REDACTED]", "Cookie": "[REDACTED]", "Accept": "application/json"}],
        },
        "items": [{"password": "[REDACTED]"}],
    }


def test_settings_api_redacts_values_for_get_and_post(tmp_path, monkeypatch):
    core = Core(data_dir=tmp_path)
    registry = JobRegistry(core)
    runner = AsyncRunner(core)
    raw = {
        "api_key": "do-not-disclose",
        "service": {"password": "also-private", "timeout_seconds": 10},
    }
    monkeypatch.setattr(core.settings, "get", lambda: raw)
    monkeypatch.setattr(core.settings, "save", lambda _data: raw)
    app = create_app(core, registry, runner)
    app.config["TESTING"] = True
    client = app.test_client()

    get_response = client.get("/api/settings")
    post_response = client.post("/api/settings", json={"service": {"timeout_seconds": 10}}, headers={"Origin": "http://localhost"})
    assert get_response.status_code == 200
    assert post_response.status_code == 200
    expected = {
        "api_key": "[REDACTED]",
        "service": {"password": "[REDACTED]", "timeout_seconds": 10},
    }
    assert get_response.get_json() == expected
    assert post_response.get_json() == expected

def test_settings_reference_controls_are_not_mistaken_for_live_writes(page, live_server):
    page.goto(f"{live_server}/ui-v2/settings")
    page.wait_for_function("() => document.querySelector('#settings-status') && !document.querySelector('#settings-status').textContent.includes('Loading settings')")
    # Static design-reference controls remain visible for layout continuity but cannot submit writes.
    assert page.locator("main input, main select, main textarea").count() > 0
    assert page.locator("main input:disabled, main select:disabled, main textarea:disabled").count() == page.locator("main input, main select, main textarea").count()
    assert page.locator("main button:disabled").count() > 0
    assert "configuration writes are not connected" in page.locator("main").inner_text()
