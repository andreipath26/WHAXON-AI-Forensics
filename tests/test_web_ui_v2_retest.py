"""Browser coverage for the canonical live remediation retest page."""
from __future__ import annotations


def test_retest_page_loads_current_findings(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/retest")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#retest-status')?.textContent.includes('Loading recorded')",
        timeout=5000,
    )
    assert page.locator("#whaxon-live-retest").is_visible()
    assert page.locator("#retest-list").is_visible()


def test_dashboard_links_to_retest_page(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="remediation-retest-studio"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/retest"

def test_retest_page_never_displays_static_fixture_evidence_or_commands(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/retest")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('finding record(s)') "
        "|| document.querySelector('#retest-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "staging-api.corp.net",
        "pg_sleep(5)",
        "K9#xL9!pQ_corp_secret",
        "AKIAIOSFODNN7EXAMPLE",
        "5,009ms",
        "COMMIT 3-WAY VERDICT TO AUDIT LEDGER",
        "RE-EXECUTE IMMEDIATE PROBE",
    ):
        assert marker not in visible, f"Fictional retest fixture must not be shown: {marker}"
    assert page.locator("#whaxon-live-retest").is_visible()

