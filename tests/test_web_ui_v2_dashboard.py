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
    page.locator("#dashboard-engagement-selector").click()
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
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status')?.textContent.includes('No running or queued jobs were found')",
        timeout=5000,
    )


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

def test_dashboard_credential_notice_reflects_live_status_api(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    status = page.evaluate("() => fetch('/api/status').then(response => response.json())")
    page.wait_for_function(
        """(defaultCreds) => {
          const labels = [...document.querySelectorAll('span')].map(node => node.textContent.trim());
          return defaultCreds
            ? labels.includes('Default Credentials Detected')
            : labels.includes('Credential Configuration Status');
        }""",
        arg=status["default_creds"],
        timeout=8000,
    )

def test_dashboard_artifact_card_supports_drop_and_rejects_unwired_formats(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status') !== null",
        timeout=8000,
    )
    assert page.locator("h2").filter(has_text="Import Existing Assessment Profile").is_visible()
    page.evaluate(
        """() => {
          const heading = [...document.querySelectorAll('h2')].find(node =>
            node.textContent.trim() === 'Import Existing Assessment Profile'
          );
          const card = heading.closest('.group.relative.flex.flex-col');
          const transfer = new DataTransfer();
          transfer.items.add(new File(['not an importable artifact'], 'unsupported.txt', {type: 'text/plain'}));
          card.dispatchEvent(new DragEvent('drop', {bubbles: true, cancelable: true, dataTransfer: transfer}));
        }"""
    )
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status')?.textContent.includes('Nmap and scope-profile imports are not wired yet')",
        timeout=5000,
    )

def test_dashboard_imports_valid_burp_xml_and_opens_findings(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    page.wait_for_function(
        "() => document.querySelector('#dashboard-action-status') !== null",
        timeout=8000,
    )
    page.evaluate(
        """() => {
          const heading = [...document.querySelectorAll('h2')].find(node =>
            node.textContent.trim() === 'Import Existing Assessment Profile'
          );
          const card = heading.closest('.group.relative.flex.flex-col');
          const xml = '<?xml version="1.0"?><issues><issue><name>Dashboard import test</name><host>http://127.0.0.1</host><path>/dashboard-test</path><severity>High</severity><confidence>Certain</confidence></issue></issues>';
          const transfer = new DataTransfer();
          transfer.items.add(new File([xml], 'dashboard-import.xml', {type: 'application/xml'}));
          card.dispatchEvent(new DragEvent('drop', {bubbles: true, cancelable: true, dataTransfer: transfer}));
        }"""
    )
    page.wait_for_url("**/ui-v2/findings", timeout=10000)
    payload = page.evaluate("() => fetch('/api/ui-v2/findings').then(response => response.text())")
    assert "Dashboard import test" in payload
