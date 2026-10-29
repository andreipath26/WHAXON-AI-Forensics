"""Browser coverage for the live adapter manager."""
from __future__ import annotations


def test_adapter_manager_uses_live_tool_catalog(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/adapters")
    assert response is not None and response.status == 200
    page.wait_for_function("() => !document.querySelector('#adapter-status')?.textContent.includes('Loading live')")
    assert page.locator("#whaxon-live-adapters").is_visible()
    assert page.locator("#adapter-filter").is_visible()
    refresh = page.get_by_role("button", name="Refresh catalog")
    assert refresh.is_visible()
    await refresh.click()
    page.wait_for_function("() => !document.querySelector('#adapter-status')?.textContent.includes('Loading live')")
    assert page.locator("#adapter-status").get_attribute("aria-live") == "polite"


def test_dashboard_links_to_adapter_manager(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="adapter-and-plugin-manager"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/adapters"
