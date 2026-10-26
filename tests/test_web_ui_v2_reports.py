"""Browser tests for the canonical live reports and PTES coverage page."""
from __future__ import annotations


def _open_reports_v2(page, live_server):
    page.goto(f"{live_server}/ui-v2/reports")
    page.wait_for_function(
        "() => document.querySelector('#reports-kpi-jobs').textContent.trim() !== '—'",
        timeout=5000,
    )


def test_reports_v2_renders_live_jobs_and_findings(page, live_server):
    _open_reports_v2(page, live_server)
    assert int(page.locator("#reports-kpi-jobs").text_content()) >= 1
    assert page.locator("#reports-jobs tr").count() >= 1
    assert page.locator('a[href="/api/report?format=json"]').is_visible()
    assert page.locator('a[href="/api/report?format=pdf"]').is_visible()


def test_reports_v2_inspects_job_and_wires_job_exports(page, live_server):
    _open_reports_v2(page, live_server)
    page.locator("#reports-jobs button").first.click()
    assert page.locator("#reports-detail").is_visible()
    assert "/api/jobs/" in page.locator("#reports-job-md").get_attribute("href")
    assert "format=html" in page.locator("#reports-job-html").get_attribute("href")
    assert "format=pdf" in page.locator("#reports-job-pdf").get_attribute("href")
    assert "findings" in page.locator("#reports-detail-evidence").text_content()


def test_reports_v2_shows_all_wired_navigation(page, live_server):
    _open_reports_v2(page, live_server)
    for path in (
        "scope-and-targets",
        "run-and-orchestration",
        "trust-layer-and-findings",
        "ptes-coverage-and-reports",
    ):
        assert page.locator(f'a[data-path="{path}"]').is_visible()
