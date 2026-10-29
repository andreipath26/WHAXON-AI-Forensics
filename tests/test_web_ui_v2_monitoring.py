"""Browser coverage for the canonical attack-surface monitoring page."""
from __future__ import annotations


def test_monitoring_page_loads_canonical_design_and_live_state(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/monitoring")
    assert response is not None and response.status == 200
    assert page.locator("#asset-ledger-container").count() == 1
    page.wait_for_function(
        """() => {
          const node = document.querySelector("#asset-ledger-container");
          return node && !node.textContent.includes("Loading recorded WHAXON jobs");
        }""",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    assert "api.internal.corp" not in visible
    assert "ENG-2026-X892" not in visible
    assert "CVE-2023-38606" not in visible
    assert "uid=0(root)" not in visible
    assert "184,209" not in visible
    assert "99.4%" not in visible
    assert "Rogue Port Exposed" not in visible
    assert "DAEMON: HOURLY SYNCHRONOUS SCAN ACTIVE" not in visible
    assert "PAGE 1 OF 6" not in visible
    assert page.locator("#asset-search-input").is_visible()
    assert page.locator("#asset-ledger-container .asset-card").count() == 0


def test_monitoring_page_uses_live_apis_and_hides_unsupported_controls(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/monitoring")
    assert response is not None and response.status == 200
    assert page.locator("#asset-search-input").count() == 1
    assert page.get_by_role("button", name="Emergency Halt Scan").count() == 0
    assert page.get_by_role("button", name="Trigger Delta Recon Now").count() == 0

def test_monitoring_summary_uses_live_jobs_history_and_scope_and_refreshes(page, live_server):
    calls = {"report": 0, "history": 0, "scope": 0}

    def report(route):
        calls["report"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job":{"id":"job-mon","target":"192.0.2.10","tool":"nmap","status":"finished"},'
                 '"findings":[{"seq":1},{"seq":2}]}]}',
        )

    def history(route):
        calls["history"] += 1
        route.fulfill(status=200, content_type="application/json", body='[{"id":"job-mon"}]')

    def scope(route):
        calls["scope"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"enabled":true,"in_scope":["192.0.2.0/24"],"out_of_scope":["192.0.2.99"]}',
        )

    page.route("**/api/report?format=json", report)
    page.route("**/api/history", history)
    page.route("**/api/scope", scope)
    page.goto(f"{live_server}/ui-v2/monitoring")
    page.wait_for_function(
        "() => document.querySelector('#monitoring-summary-status')?.textContent.includes('Recorded findings: 2')",
        timeout=8000,
    )
    summary = page.locator("#monitoring-summary-status").inner_text()
    assert "Report jobs: 1" in summary
    assert "History records: 1" in summary
    assert "Scope enforcement: enabled" in summary
    assert "1 in-scope / 1 excluded" in summary
    with page.expect_response("**/api/report?format=json"):
        page.get_by_role("button", name="Refresh data").click()
    page.wait_for_function("() => document.querySelector('#monitoring-summary-status')?.textContent.includes('Recorded findings: 2')")
    assert all(value >= 2 for value in calls.values())
