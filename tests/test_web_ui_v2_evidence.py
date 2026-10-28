"""Browser coverage for the canonical evidence inspector."""
from __future__ import annotations


def test_evidence_inspector_loads_recorded_jobs(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/evidence")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#evidence-job')?.textContent.includes('Loading recorded jobs')",
        timeout=5000,
    )
    assert page.locator("#whaxon-live-evidence").is_visible()
    assert page.locator("#evidence-refresh").is_visible()
    assert page.locator("#evidence-status").inner_text()


def test_dashboard_links_to_evidence_inspector(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    link = page.locator('a[data-path="evidence-file-inspector"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/evidence"
