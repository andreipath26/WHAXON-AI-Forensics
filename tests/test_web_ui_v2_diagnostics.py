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


def test_diagnostics_reference_buttons_cannot_run_simulated_operations(page, live_server):
    page.goto(f"{live_server}/ui-v2/diagnostics")
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Live values loaded') "
        "|| document.querySelector('#diagnostics-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    for label in (
        "Restart Engine Daemons",
        "Test MSF RPC Handshake",
        "Benchmark SQLite Write Speed",
        "Probe Ollama LLM Socket",
        "Check eBPF Filter Integrity",
    ):
        button = page.get_by_role("button", name=label)
        if button.count():
            assert button.is_disabled(), f"{label} must not run a simulated operation"
    assert page.locator("#btn-run-diag").is_enabled(), "Run Full Diagnostic must refresh live diagnostics"
    assert page.locator("#btn-export-json").is_enabled(), "Export Health Report must export live API data"
    for button in page.locator("main button:visible").all():
        if button.get_attribute("id") in ("diagnostics-refresh", "btn-run-diag", "btn-export-json"):
            assert button.is_enabled()
        else:
            assert button.is_disabled(), f"Unwired diagnostic control is enabled: {button.inner_text()}"

def test_diagnostics_terminal_log_button_navigates_to_run_workspace(page, live_server):
    page.goto(f"{live_server}/ui-v2/diagnostics")
    page.get_by_role("button", name="Terminal Log").click()
    page.wait_for_url("**/ui-v2/run")
    assert page.url.endswith("/ui-v2/run")


def test_diagnostics_emergency_halt_reports_when_no_jobs_are_active(page, live_server):
    page.goto(f"{live_server}/ui-v2/diagnostics")
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Live values loaded')"
        " || document.querySelector('#diagnostics-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    page.get_by_role("button", name="Emergency Halt Scan").click()
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('No running or queued jobs were found')",
        timeout=5000,
    )

def test_diagnostics_header_uses_live_scope_and_navigation(page, live_server):
    page.goto(f"{live_server}/ui-v2/diagnostics")
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Live values loaded')"
        " || document.querySelector('#diagnostics-status')?.textContent.includes('Diagnostics could not be loaded')",
        timeout=10000,
    )
    page.wait_for_function(
        "() => !document.querySelector('header')?.innerText.includes('api.internal.corp')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(response => response.json())")
    targets = scope.get("in_scope") or []
    target = targets[0] if targets else "No target configured"
    header = page.locator("header").inner_text()
    assert target in header
    assert "SCOPE CONFIGURATION LOADED" in header or "SCOPE ENFORCEMENT DISABLED" in header

    page.locator("header button").filter(has_text="New").click()
    page.wait_for_url("**/ui-v2/scope")
    assert page.url.endswith("/ui-v2/scope")


def test_diagnostics_run_and_export_use_live_api_data(page, live_server):
    page.goto(f"{live_server}/ui-v2/diagnostics")
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Live values loaded')"
        " || document.querySelector('#diagnostics-status')?.textContent.includes('Diagnostics could not be loaded')",
        timeout=10000,
    )
    run_button = page.locator("#btn-run-diag")
    assert run_button.is_enabled()
    run_button.click()
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Live values loaded')"
        " || document.querySelector('#diagnostics-status')?.textContent.includes('Diagnostics could not be loaded')",
        timeout=10000,
    )

    with page.expect_download() as download_info:
        page.locator("#btn-export-json").click()
    download = download_info.value
    assert download.suggested_filename == "whaxon-health-report.json"
    page.wait_for_function(
        "() => document.querySelector('#diagnostics-status')?.textContent.includes('Exported a JSON report')"
        " || document.querySelector('#diagnostics-status')?.textContent.includes('Health report export failed')",
        timeout=5000,
    )
    assert "reference/demo control" in page.locator("#btn-restart-daemons").get_attribute("title")
    assert page.locator("#btn-restart-daemons").is_disabled()
    assert page.locator("#btn-run-diag").is_enabled()
    assert page.locator("#btn-export-json").is_enabled()

