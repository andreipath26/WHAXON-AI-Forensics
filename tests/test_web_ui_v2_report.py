"""Browser coverage for the canonical live report page (UI v2)."""
from __future__ import annotations


def test_report_page_loads_and_uses_live_report_counts(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/report")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => [...document.querySelectorAll('main div')].some(n => "
        "document.documentElement.dataset.reportReady === 'true' && n.textContent.includes('Live report data:') && n.textContent.includes('findings'))",
        timeout=5000,
    )
    assert page.locator("#previewBtn").is_visible()
    assert page.get_by_role("button", name="Export Findings (.json)").is_visible()
    assert page.get_by_role("button", name="Download Full Report (.pdf)").is_visible()


def test_report_page_hides_illustrative_proof_and_evidence_panels(page, live_server):
    page.goto(f"{live_server}/ui-v2/report")
    page.wait_for_function(
        "() => [...document.querySelectorAll('main div')].some(n => "
        "document.documentElement.dataset.reportReady === 'true' && n.textContent.includes('Live report data:'))",
        timeout=5000,
    )
    assert page.get_by_text("Sample Deterministic Proof: FINDING-SQLI-001 (auth-endpoint)").is_hidden()
    assert page.get_by_role("heading", name="PTES Phase Execution & Telemetry Tracker").is_hidden()
    assert page.get_by_role("heading", name="Coverage Gap Matrix").is_hidden()
    assert page.get_by_role("heading", name="Report Synthesis & Compliance Profiler").is_visible()
    assert page.get_by_role("heading", name="Evidence Summary").is_hidden()
    assert page.get_by_role("heading", name="Local Evidence Locker").is_hidden()
    assert page.get_by_text("Scope Compliance & Verification").is_hidden()
    assert page.get_by_text("6 curl-verified").is_hidden()
    assert page.get_by_text("STRICT_WHITELIST").is_hidden()
    assert page.get_by_text("Select Report Modules to Compile").is_hidden()
    assert page.get_by_text("Correlate Standards & Compliance Matrix").is_hidden()
    assert page.get_by_text("6 deterministic findings with reproducible curl replay proofs.").is_hidden()


def test_report_preview_fetches_live_markdown(page, live_server):
    page.goto(f"{live_server}/ui-v2/report")
    with page.expect_response(
        lambda response: response.request.method == "GET"
        and response.url.endswith("/api/report?format=md")
    ) as response_info:
        page.locator("#previewBtn").click()
    assert response_info.value.ok
    assert page.locator("#previewModal").is_visible()
