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

def test_evidence_inspector_does_not_show_fixture_scan_output_as_live_evidence(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/evidence")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#evidence-status')?.textContent !== 'Evidence is loaded only from WHAXON records.'",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "staging-api.corp.net",
        "Apache Envoy 1.18.0",
        "SHA-256 CHECKSUM MATCHED",
        "LOCAL REPLAY CACHE INTACT",
        "Merkle Leaf #4",
        "0x8891...E25519",
        "Direct Finding Ingestion Preview",
    ):
        assert marker not in visible, f"Fictional evidence fixture must not be shown: {marker}"
    assert page.locator("#whaxon-live-evidence").is_visible()

