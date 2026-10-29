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

def test_diagnostics_page_does_not_report_simulated_checks_as_live(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/diagnostics")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Live values loaded') "
        "|| document.querySelector('#diagnostics-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "All Tests Passed",
        "ACK RECEIVED (0.9ms)",
        "PID 8891 killed",
        "out_of_scope_drops",
        "msf_version",
        "ALL SUBSYSTEMS HEALTHY",
        "whaxon_health_diagnostics_",
    ):
        assert marker not in visible, f"Simulated diagnostic output must not be shown: {marker}"
    assert page.locator("#whaxon-live-diagnostics").is_visible()

def test_diagnostics_layout_remains_available_and_mock_actions_are_disabled(page, live_server):
    page.goto(f"{live_server}/ui-v2/diagnostics")
    assert page.get_by_role("heading", name="System Diagnostics & Health Monitor").is_visible()
    assert page.locator("#diagnostics-refresh").is_visible()
    restart = page.get_by_role("button", name="Restart Engine Daemons")
    if restart.count():
        assert restart.is_disabled()
