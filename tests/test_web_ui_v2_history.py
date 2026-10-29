"""Browser coverage for the canonical live job-history page."""
from __future__ import annotations


def test_job_history_renders_only_records_from_live_history_api(page, live_server):
    api_response = page.request.get(f"{live_server}/api/history")
    assert api_response.status == 200
    jobs = api_response.json()
    assert isinstance(jobs, list)

    response = page.goto(f"{live_server}/ui-v2/history")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#history-live-summary')?.textContent.includes('Loading')",
        timeout=5000,
    )
    assert page.locator("#history-live-summary").is_visible()
    assert page.locator("table tbody tr").count() == len(jobs)
    visible = page.locator("body").inner_text()
    assert "Page 1 of 3" not in visible
    assert "Total 42 records" not in visible
    for marker in (
        "staging-api.corp.net",
        "api.internal.corp",
        "ENG-2026-X892",
        "JOB-8841",
        "JOB-8840",
        "7f99b1",
        "CVE-2023-38606",
    ):
        assert marker not in visible, f"Sample history data must not be shown as live: {marker}"


def test_job_history_exports_live_records_as_json(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/history")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#history-live-summary')?.textContent.includes('Loading')",
        timeout=5000,
    )
    with page.expect_download() as download:
        page.get_by_role("button", name="Export Ledger", exact=False).click()
    assert download.value.suggested_filename == "whaxon-job-history.json"


def test_dashboard_navigation_reaches_job_history(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    link = page.locator('a[data-path="job-execution-history"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/history"
    history_response = page.request.get(f"{live_server}/ui-v2/history")
    assert history_response.status == 200
