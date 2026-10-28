"""Browser tests for live dashboard controls and operational actions."""
from __future__ import annotations

import json
import re


def test_dashboard_new_engagement_control_opens_scope(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status') !== null",
        timeout=8000,
    )
    page.get_by_role("button", name=re.compile(r"No active engagement")).click()
    assert page.url.endswith("/ui-v2/scope")


def test_dashboard_filter_narrows_live_job_history(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => [...document.querySelectorAll('table tbody tr')].some(row => row.textContent.includes('seed-job-1'))",
        timeout=8000,
    )
    filter_input = page.get_by_role("textbox", name="Filter recent job history")
    filter_input.fill("seed-job-1")
    visible_rows = page.locator("table tbody tr:visible")
    assert visible_rows.count() == 1
    assert "seed-job-1" in visible_rows.first.inner_text()


def test_dashboard_exports_live_history_as_json(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status') !== null",
        timeout=8000,
    )
    with page.expect_download() as download_info:
        page.get_by_role("button", name=re.compile(r"Export Archive")).click()
    download = download_info.value
    assert download.suggested_filename.startswith("whaxon-history-")
    assert download.suggested_filename.endswith(".json")
    path = download.path()
    assert path is not None
    with open(path, encoding="utf-8") as file:
        payload = json.load(file)
    assert isinstance(payload.get("jobs"), list)
    assert any(job.get("id") == "seed-job-1" or job.get("job_id") == "seed-job-1" for job in payload["jobs"])


def test_dashboard_emergency_halt_is_honest_when_no_jobs_are_active(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status') !== null",
        timeout=8000,
    )
    page.get_by_role("button", name=re.compile(r"Emergency Halt Scan")).click()
    assert "No running or queued jobs were found" in page.locator("#dashboard-action-status").inner_text()


def test_dashboard_cli_help_and_credentials_controls_explain_real_setup(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status') !== null",
        timeout=8000,
    )
    page.get_by_role("button", name=re.compile(r"CLI Help")).click()
    assert "whaxon --help" in page.locator("#dashboard-action-status").inner_text()
    page.get_by_role("button", name=re.compile(r"Update Credentials Now")).click()
    assert "WHAXON_AUTH_USER" in page.locator("#dashboard-action-status").inner_text()


def test_dashboard_does_not_claim_default_credentials_are_detected_without_checking(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    html = response.text()
    assert "Default Local Engine Credentials Detected" not in html
    assert "whaxon:whaxon" not in html
    assert "Credential Configuration Before Network Exposure" in html
