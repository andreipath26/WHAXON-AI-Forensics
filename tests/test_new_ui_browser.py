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
    visible_text = page.locator("body").inner_text()
    assert "Target: api.internal.corp" not in visible_text
    assert "ENG-2026-X892" not in visible_text
    assert "6 curl-verified" not in visible_text
    assert "Sample Deterministic Proof: FINDING-SQLI-001" not in visible_text
    assert "7f83b165" not in visible_text
    preview_button.click()
    page.wait_for_function("document.querySelector('#previewModal')?.classList.contains('flex')")
    preview = page.locator("#previewModal pre")
    assert preview.is_visible()
    assert "seed-job-1" in preview.inner_text()
    assert "ENG-2026-X892" not in preview.inner_text()


def test_threat_intel_page_uses_live_metasploit_module_names(page, live_server):
    page.route("**/api/msf/status", lambda route: route.fulfill(
        status=200, content_type="application/json", body='{"up":true,"config":{}}'))
    page.route("**/api/msf/modules/exploit", lambda route: route.fulfill(
        status=200, content_type="application/json",
        body='["exploit/linux/ssh/test_module","exploit/multi/http/test_module"]'))
    page.goto(f"{live_server}/ui/threat-intel-and-exploit-arsenal", wait_until="domcontentloaded")
    page.wait_for_function("document.querySelectorAll('.cve-row-item').length === 2")
    visible_text = page.locator("body").inner_text()
    assert "exploit/linux/ssh/test_module" in visible_text
    assert "exploit/multi/http/test_module" in visible_text
    assert "CVE-2024-6387" not in visible_text
    assert "CVE-2024-38077" not in visible_text
    assert "CISA KEV" not in visible_text
    assert "194,821 CVEs" not in visible_text
    assert "ACTIVE (2h ago)" not in visible_text
    assert "IN SCOPE:" not in visible_text
    assert "Async Python PoC Ready" not in visible_text


def test_health_page_shows_real_health_payload_and_hides_fake_controls(page, live_server):
    page.goto(f"{live_server}/ui/system-diagnostics-and-health", wait_until="domcontentloaded")
    stream = page.locator("#diagnostic-stream")
    assert stream.is_visible()
    assert "readiness" in stream.inner_text()
    assert page.locator("#btn-restart-daemons").is_hidden()


def test_evidence_page_never_shows_static_sample_artifacts(page, live_server):
    page.goto(f"{live_server}/ui/evidence-file-inspector", wait_until="domcontentloaded")
    page.wait_for_timeout(250)
    assert "raw_nmap_syn_scan.xml" not in page.locator("body").inner_text()


def test_unavailable_workflow_hides_its_navigation_entry(page, live_server):
    page.goto(f"{live_server}/ui/bas-and-detection-validation", wait_until="domcontentloaded")
    page.wait_for_timeout(250)
    assert page.locator('[data-path="bas-and-detection-validation"]').is_hidden()
    assert page.locator("main").inner_text().strip() == ""


def test_unwired_approval_page_hides_demo_modal_outside_main(page, live_server):
    page.goto(f"{live_server}/ui/trust-layer-approvals-queue-modal", wait_until="domcontentloaded")
    assert page.locator("#approvals-modal").is_hidden()


def test_reports_page_hides_static_coverage_and_rule_claims(page, live_server):
    page.goto(f"{live_server}/ui/ptes-coverage-and-reports", wait_until="domcontentloaded")
    assert page.get_by_text("Coverage Gap Matrix", exact=True).is_hidden()
    assert page.get_by_text("Rule Recommendations", exact=True).is_hidden()


def test_retest_page_renders_real_findings_and_hides_batch_claims(page, live_server):
    page.goto(f"{live_server}/ui/remediation-retest-studio", wait_until="domcontentloaded")
    queue = page.locator("div.max-h-\\[820px\\]")
    assert queue.is_visible()
    assert queue.locator(":scope > div").count() >= 1
    assert page.get_by_role("button", name="Validate / Retest Selected").is_visible()
    assert page.get_by_role("button", name="BATCH REPLAY (3x BASELINE + 3x INJECTED)").is_hidden()


def test_ai_strategy_gate_does_not_show_demo_proposal_without_pending_run(page, live_server):
    page.goto(f"{live_server}/ui/ai-strategy-gate", wait_until="domcontentloaded")
    page.wait_for_timeout(200)
    assert page.locator("#btn-authorize").is_hidden()
    assert page.locator("#btn-reject").is_hidden()


def test_attack_chain_page_hides_static_chain_when_no_recorded_edges(page, live_server):
    page.goto(f"{live_server}/ui/correlated-attack-chains", wait_until="domcontentloaded")
    page.wait_for_timeout(200)
    assert "Postgres Remote Code Execution via dblink/COPY" not in page.locator("body").inner_text()


def test_attack_surface_renders_recorded_targets_not_cloud_demo(page, live_server):
    page.goto(f"{live_server}/ui/attack-surface-and-continuous-monitoring", wait_until="domcontentloaded")
    page.wait_for_timeout(300)
    ledger = page.locator("#asset-ledger-container")
    assert page.get_by_text("ATTACK SURFACE & CONTINUOUS MONITORING", exact=True).is_visible()
    assert ledger.is_visible()
    assert ledger.locator("article.asset-card").count() >= 1
    visible_text = page.locator("body").inner_text()
    assert "127.0.0.1" in visible_text
    assert "assets-backup-archive.s3.amazonaws.com" not in visible_text
    assert "142 of 142 Assets Active" not in visible_text
    assert "DAEMON: HOURLY SYNCHRONOUS SCAN ACTIVE" not in visible_text
    assert "14m ago" not in visible_text
    assert "46m" not in visible_text


def test_approval_modal_uses_selected_real_finding_and_hides_fake_signing(page, live_server):
    page.goto(f"{live_server}/ui/trust-layer-approvals-queue-modal", wait_until="domcontentloaded")
    send = page.get_by_role("button", name="Send to Approvals")
    assert send.is_visible()
    send.click()
    modal = page.locator("#approvals-modal")
    assert modal.is_visible()
    assert "CND-9402" not in modal.inner_text()
    assert page.get_by_role("button", name="Refute / False Positive").is_visible()
    assert page.get_by_role("button", name="Approve as Verified (Sign Proof)").is_hidden()
