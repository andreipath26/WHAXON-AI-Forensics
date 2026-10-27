"""Browser coverage for the read-only settings/API explorer."""
from __future__ import annotations


def test_settings_explorer_loads_and_redacts_settings(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/settings")
    assert response is not None and response.status == 200
    page.wait_for_function("() => !document.querySelector('#settings-status')?.textContent.includes('Loading settings')")
    assert page.locator("#whaxon-live-settings").is_visible()
    assert page.locator("#settings-json").is_visible()


def test_dashboard_links_to_settings_explorer(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="settings-and-api-explorer"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/settings"
