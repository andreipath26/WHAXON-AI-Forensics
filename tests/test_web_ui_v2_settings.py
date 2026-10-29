"""Browser coverage for the read-only settings/API explorer."""
from __future__ import annotations

from whaxon.interfaces.web.server import _redact_sensitive_settings


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
            "timeout_seconds": 10,
            "headers": [{"Authorization": "Bearer very-private", "Accept": "application/json"}],
        },
        "items": [{"password": "hidden"}],
    }
    assert _redact_sensitive_settings(raw) == {
        "api_key": "[REDACTED]",
        "service": {
            "client_secret": "[REDACTED]",
            "timeout_seconds": 10,
            "headers": [{"Authorization": "[REDACTED]", "Accept": "application/json"}],
        },
        "items": [{"password": "[REDACTED]"}],
    }
