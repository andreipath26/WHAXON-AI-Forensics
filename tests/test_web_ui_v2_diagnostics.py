"""Browser coverage for the canonical live diagnostics page."""
from __future__ import annotations


def test_diagnostics_page_uses_live_health_and_tool_apis(page, live_server):
    health = page.request.get(f"{live_server}/api/health")
    tools = page.request.get(f"{live_server}/api/tools")
    assert health.status in (200, 503)
    assert tools.status == 200
    assert isinstance(health.json(), dict)
    assert isinstance(tools.json(), list)

    response = page.goto(f"{live_server}/ui-v2/diagnostics")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#diagnostics-status')?.textContent.includes('Loading current')",
        timeout=5000,
    )
    assert page.locator("#whaxon-live-diagnostics").is_visible()
    assert page.locator("#diagnostics-checks > div").count() >= 3
    assert page.locator("#diagnostics-refresh").is_visible()


def test_dashboard_links_to_live_diagnostics(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    link = page.locator('a[data-path="system-diagnostics-and-health"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/diagnostics"
