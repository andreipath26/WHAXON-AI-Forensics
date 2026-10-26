"""Browser smoke tests for the canonical roadmap UI served at /ui."""
from __future__ import annotations

import pytest

UI_ROUTES = [
    "/ui",
    "/ui/scope-and-targets",
    "/ui/run-and-orchestration",
    "/ui/trust-layer-and-findings",
    "/ui/trust-layer-approvals-queue-modal",
    "/ui/ptes-coverage-and-reports",
    "/ui/bas-and-detection-validation",
    "/ui/compliance-and-framework-crosswalk",
    "/ui/threat-intel-and-exploit-arsenal",
    "/ui/ai-strategy-gate",
    "/ui/remediation-retest-studio",
    "/ui/attack-surface-and-continuous-monitoring",
    "/ui/correlated-attack-chains",
    "/ui/bug-bounty-and-live-browser-studio",
    "/ui/ptaas-client-portal",
    "/ui/job-execution-history",
    "/ui/evidence-file-inspector",
    "/ui/cryptographic-audit-log",
    "/ui/system-diagnostics-and-health",
    "/ui/adapter-and-plugin-manager",
    "/ui/settings-and-api-explorer",
]


@pytest.mark.parametrize("route", UI_ROUTES)
def test_canonical_ui_route_loads_without_uncaught_page_errors(page, live_server, route):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    response = page.goto(f"{live_server}{route}", wait_until="domcontentloaded")
    assert response is not None and response.status == 200, route
    assert "WHAXON" in page.locator("body").inner_text(), route
    page.wait_for_timeout(250)
    assert errors == [], f"{route} raised browser errors: {errors}"


def test_legacy_ui_is_still_reachable(page, live_server):
    response = page.goto(f"{live_server}/legacy-ui", wait_until="domcontentloaded")
    assert response is not None and response.status == 200
    assert page.locator(".sb-brand .label-text").inner_text() == "WHAXON"

def test_dashboard_renders_live_job_rows(page, live_server):
    page.goto(f"{live_server}/ui", wait_until="domcontentloaded")
    page.wait_for_timeout(500)
    assert page.locator("main").is_visible()
    assert page.locator("main table tbody tr").count() >= 1
    assert "seed-job-1" in page.locator("main").inner_text()


def test_scope_page_renders_real_scope_rules(page, live_server):
    page.goto(f"{live_server}/ui/scope-and-targets", wait_until="domcontentloaded")
    page.wait_for_timeout(300)
    body = page.locator("#targetTableBody")
    assert body.is_visible()
    assert body.locator("tr").count() >= 1
    assert "127.0.0.0/8" in body.inner_text()


def test_findings_page_renders_real_findings(page, live_server):
    page.goto(f"{live_server}/ui/trust-layer-and-findings", wait_until="domcontentloaded")
    page.wait_for_timeout(500)
    card = page.locator("#finding-card-1")
    assert card.is_visible()
    assert "web_issue" in card.inner_text()
    assert "127.0.0.1:80" in card.inner_text()


def test_run_page_exposes_live_tool_and_target_controls(page, live_server):
    page.goto(f"{live_server}/ui/run-and-orchestration", wait_until="domcontentloaded")
    page.wait_for_timeout(400)
    assert page.locator('input[placeholder*="Target host"]').is_visible()
    assert page.locator('select[aria-label="Tool to run"]').count() == 0
    assert page.locator('button').filter(has_text="Re-run").count() >= 1


def test_history_page_renders_live_job_rows(page, live_server):
    page.goto(f"{live_server}/ui/job-execution-history", wait_until="domcontentloaded")
    page.wait_for_timeout(400)
    assert "seed-job-1" in page.locator("body").inner_text()


def test_catalog_page_renders_live_tools(page, live_server):
    page.goto(f"{live_server}/ui/adapter-and-plugin-manager", wait_until="domcontentloaded")
    page.wait_for_timeout(400)
    matrix = page.locator("#adapter-matrix")
    assert matrix.is_visible()
    assert matrix.locator(".adapter-card").count() >= 1



def test_reports_page_wires_native_preview_to_live_report(page, live_server):
    page.goto(f"{live_server}/ui/ptes-coverage-and-reports", wait_until="domcontentloaded")
    preview_button = page.get_by_role("button", name="Preview Markdown")
    assert preview_button.is_visible()
    preview_button.click()
    page.wait_for_function("document.querySelector('#previewModal')?.classList.contains('flex')")
    preview = page.locator("#previewModal pre")
    assert preview.is_visible()
    assert "seed-job-1" in preview.inner_text()
    assert "ENG-2026-X892" not in preview.inner_text()


def test_health_page_shows_real_health_payload_and_hides_fake_controls(page, live_server):
    page.goto(f"{live_server}/ui/system-diagnostics-and-health", wait_until="domcontentloaded")
    stream = page.locator("#diagnostic-stream")
    assert stream.is_visible()
    assert "readiness" in stream.inner_text()
    assert page.locator("#btn-restart-daemons").is_hidden()
