"""Browser coverage for the canonical WHAXON v2 dashboard."""
from __future__ import annotations


def test_dashboard_loads_and_routes_only_to_wired_core_pages(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    assert "Dashboard / Zero State" in response.text()
    assert page.locator('a[data-path="scope-and-targets"]').get_attribute("href") == "/ui-v2/scope"
    assert page.locator('a[data-path="run-and-orchestration"]').get_attribute("href") == "/ui-v2/run"
    visible = page.locator("body").inner_text()
    assert "staging-api.corp.net" not in visible
    assert "CVE-2023-38606" not in visible
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
