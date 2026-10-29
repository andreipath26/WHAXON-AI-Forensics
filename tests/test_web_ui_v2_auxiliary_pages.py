"""Browser coverage for canonical auxiliary WHAXON v2 pages."""
from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("path", "live_id"),
    [
        ("/ui-v2/bas", "whaxon-live-bas"),
        ("/ui-v2/bug-bounty", "whaxon-live-bug-bounty"),
        ("/ui-v2/compliance", "whaxon-live-compliance"),
        ("/ui-v2/ptaas", "whaxon-live-ptaas"),
        ("/ui-v2/threat-intel", "whaxon-live-threat-intel"),
        ("/ui-v2/approvals", "whaxon-live-approvals"),
    ],
)
def test_auxiliary_canonical_pages_render_live_panels(page, live_server, path, live_id):
    response = page.goto(f"{live_server}{path}")
    assert response is not None and response.status == 200
    assert page.locator(f"#{live_id}").count() == 1
    page.wait_for_function(
        "(id) => { const el = document.getElementById(id); return el && !el.textContent.includes('Fetching current backend state.'); }",
        arg=live_id,
        timeout=20000,
    )


def test_bug_bounty_hides_unimplemented_browser_actions(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/bug-bounty")
    assert response is not None and response.status == 200
    assert page.locator("#whaxon-live-bug-bounty").count() == 1
    for label in ("CLEAR CACHE", "DUMP DOM SNAPSHOT", "SEND TO VALIDATOR", "DIFF ANALYSIS", "PING SEC-OPS"):
        assert page.locator("button:visible").filter(has_text=label).count() == 0
    visible = page.locator("body").inner_text()
    assert "24 Ev/s" not in visible
    assert "api.staging.internal" not in visible


def test_ptaas_hides_unimplemented_client_actions(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/ptaas")
    assert response is not None and response.status == 200
    assert page.locator("#whaxon-live-ptaas").count() == 1
    for label in ("PING SEC-OPS", "REQUEST RETEST", "VIEW RAW PACKET", "VIEW SCRIPT"):
        assert page.locator("button:visible").filter(has_text=label).count() == 0
    visible = page.locator("body").inner_text()
    assert "BOLA / IDOR in Merchant Transfer Settlement Route" not in visible
    assert "REPRODUCIBLE EXPLOIT ARTIFACT" not in visible

def test_bas_validation_only_offers_actions_for_real_sequence_ids(page, live_server):
    calls = []

    def findings(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job":{"id":"job-bas"},"findings":['
                 '{"seq":3,"kind":"recorded finding","severity":"low","verification_status":"candidate"},'
                 '{"seq":null,"kind":"missing sequence","severity":"high","verification_status":"candidate"}]}]}',
        )

    def validate(route):
        calls.append(route.request.url)
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"candidate","reason":"no deterministic replay signal"}',
        )

    page.route("**/api/ui-v2/findings", findings)
    page.route("**/api/validate/**", validate)
    page.goto(f"{live_server}/ui-v2/bas")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-bas-status')?.textContent.includes('2 persisted finding(s)') || document.body.innerText.includes('2 persisted finding(s)')",
        timeout=8000,
    )
    buttons = page.get_by_role("button", name="Validate recorded finding")
    assert buttons.count() == 1
    buttons.first.click()
    page.wait_for_function(
        "() => document.body.innerText.includes('Validation result: candidate')",
        timeout=8000,
    )
    assert calls == [f"{live_server}/api/validate/job-bas/3"]

def test_approval_queue_submits_answer_to_waiting_run(page, live_server):
    pending_calls = {"count": 0}
    answers = []

    def pending(route):
        pending_calls["count"] += 1
        body = (
            '[{"run_id":"run-123","goal":"Review the proposed in-scope plan","status":"waiting"}]'
            if pending_calls["count"] == 1 else "[]"
        )
        route.fulfill(status=200, content_type="application/json", body=body)

    def runs(route):
        route.fulfill(status=200, content_type="application/json", body="[]")

    def answer(route):
        answers.append(route.request.post_data_json)
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"ok":true,"run_id":"run-123","seq":1}',
        )

    page.route("**/api/ai/pending", pending)
    page.route("**/api/ai/runs", runs)
    page.route("**/api/ai/runs/run-123/answer", answer)
    page.goto(f"{live_server}/ui-v2/approvals")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-approvals')?.innerText.includes('1 pending item(s)')",
        timeout=8000,
    )
    page.get_by_label("Answer for run run-123").fill("Proceed only with the approved scope.")
    page.get_by_label("Approval note for run run-123").fill("Reviewed against the engagement scope.")
    with page.expect_response("**/api/ai/runs/run-123/answer"):
        page.get_by_role("button", name="Submit answer").click()
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-approvals')?.innerText.includes('Answer recorded for run run-123')",
        timeout=8000,
    )
    assert answers == [{
        "answer": "Proceed only with the approved scope.",
        "note": "Reviewed against the engagement scope.",
    }]

def test_bug_bounty_workspace_filters_live_jobs_and_refreshes(page, live_server):
    calls = {"report": 0, "history": 0}

    def report(route):
        calls["report"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":['
                 '{"job":{"id":"job-a","target":"192.0.2.10","tool":"nmap","status":"finished"},"findings":[]},'
                 '{"job":{"id":"job-b","target":"192.0.2.20","tool":"nikto","status":"failed"},"findings":[{"seq":1}]}'
                 ']}',
        )

    def history(route):
        calls["history"] += 1
        route.fulfill(status=200, content_type="application/json", body='[{"id":"job-a"},{"id":"job-b"}]')

    page.route("**/api/report?format=json", report)
    page.route("**/api/history", history)
    page.goto(f"{live_server}/ui-v2/bug-bounty")
    page.wait_for_function(
        "() => document.querySelector('#bounty-workspace-search') && document.body.innerText.includes('2 report job(s)')",
        timeout=8000,
    )
    page.get_by_label("Filter assessment jobs").fill("job-b")
    assert page.locator("#whaxon-live-bug-bounty article:visible").count() == 1
    assert "job-b" in page.locator("#whaxon-live-bug-bounty article:visible").inner_text()
    with page.expect_response("**/api/report?format=json"):
        page.get_by_role("button", name="Refresh workspace").click()
    assert calls["report"] >= 2
    assert calls["history"] >= 2

def test_compliance_crosswalk_filters_and_exports_only_recorded_mappings(page, live_server):
    page.route(
        "**/api/ui-v2/findings",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job":{"id":"job-c"},"findings":['
                 '{"seq":1,"title":"SQL injection","cwe":"CWE-89","owasp":"A03","verification_status":"verified"},'
                 '{"seq":2,"title":"Missing header","cwe":"CWE-693","verification_status":"candidate"}]}]}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/compliance")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-compliance')?.innerText.includes('2 of 2 recorded finding(s)')",
        timeout=8000,
    )
    assert page.locator("#whaxon-live-compliance article").count() == 2
    page.get_by_label("Filter framework crosswalk").fill("CWE-89")
    assert page.locator("#whaxon-live-compliance article:visible").count() == 1
    assert "SQL injection" in page.locator("#whaxon-live-compliance article:visible").inner_text()
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Export crosswalk JSON").click()
    download = download_info.value
    assert download.suggested_filename == "whaxon-framework-crosswalk.json"

def test_ptaas_portal_filters_recorded_reports_and_findings(page, live_server):
    page.route(
        "**/api/report?format=json",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":['
                 '{"job":{"id":"job-a","target":"192.0.2.10","tool":"nmap","status":"finished"},"findings":[]},'
                 '{"job":{"id":"job-b","target":"192.0.2.20","tool":"nikto","status":"finished"},"findings":[{"title":"Missing header","severity":"low","cwe":"CWE-693"}]}'
                 ']}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/ptaas")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-ptaas')?.innerText.includes('2 of 2 recorded job(s)')",
        timeout=8000,
    )
    page.get_by_label("Filter client reports").fill("CWE-693")
    assert page.locator("#whaxon-live-ptaas article:visible").count() == 1
    assert "job-b" in page.locator("#whaxon-live-ptaas article:visible").inner_text()

def test_threat_intel_filters_local_references_and_refreshes_catalog(page, live_server):
    calls = {"tools": 0, "report": 0}

    def tools(route):
        calls["tools"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"id":"nmap","name":"Nmap","adapter_available":true,"binary_available":true},'
                 '{"id":"nikto","name":"Nikto","adapter_available":false,"binary_available":false}]',
        )

    def report(route):
        calls["report"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job":{"id":"job-ti"},"findings":['
                 '{"title":"Known issue","cve":"CVE-2024-12345"}]}]}',
        )

    page.route("**/api/tools", tools)
    page.route("**/api/report?format=json", report)
    page.goto(f"{live_server}/ui-v2/threat-intel")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel')?.innerText.includes('CVE-2024-12345')",
        timeout=8000,
    )
    assert page.locator("#whaxon-live-threat-intel article").count() == 3
    page.get_by_label("Filter threat intelligence references").fill("CVE-2024-12345")
    assert page.locator("#whaxon-live-threat-intel article:visible").count() == 1
    with page.expect_response("**/api/tools"):
        page.get_by_role("button", name="Refresh catalog").click()
    assert calls["tools"] >= 2
    assert calls["report"] >= 2

def test_threat_intel_catalog_filters_only_recorded_local_references(page, live_server):
    calls = {"tools": 0, "report": 0}

    def tools(route):
        calls["tools"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"id":"nmap","name":"Nmap","adapter_available":true,"binary_available":true},'
                 '{"id":"nikto","name":"Nikto","adapter_available":false,"binary_available":false}]',
        )

    def report(route):
        calls["report"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job":{"id":"job-ti"},"findings":['
                 '{"title":"Recorded vulnerability","cve":"CVE-2025-12345"},'
                 '{"title":"Other finding","references":["CVE-2024-23456"]}]}]}',
        )

    page.route("**/api/tools", tools)
    page.route("**/api/report?format=json", report)
    page.goto(f"{live_server}/ui-v2/threat-intel")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel')?.innerText.includes('CVE-2025-12345')",
        timeout=8000,
    )
    assert "No connected external threat-intelligence feed" in page.locator("#whaxon-live-threat-intel").inner_text()
    page.get_by_label("Filter threat intelligence references").fill("CVE-2025-12345")
    visible = page.locator("#whaxon-live-threat-intel article:visible").all_inner_texts()
    assert visible
    assert any("CVE-2025-12345" in text for text in visible)
    assert all("CVE-2024-23456" not in text for text in visible)
    with page.expect_response("**/api/tools"):
        page.get_by_role("button", name="Refresh catalog").click()
    assert calls["tools"] >= 2 and calls["report"] >= 2

def test_canonical_auxiliary_page_shells_are_preserved(page, live_server):
    page.goto(f"{live_server}/ui-v2/bas")
    assert page.get_by_text("BAS & DETECTION VALIDATION", exact=True).is_visible()
    page.goto(f"{live_server}/ui-v2/bug-bounty")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-bug-bounty')?.innerText.includes('Browser automation is not connected to this page.')",
        timeout=8000,
    )
    bounty_panel = page.locator("#whaxon-live-bug-bounty")
    assert bounty_panel.is_visible()
    assert "Browser automation is not connected to this page." in bounty_panel.inner_text()
    assert page.get_by_role("button", name="Refresh workspace").is_visible()
    page.goto(f"{live_server}/ui-v2/ptaas")
    assert page.get_by_role("heading", name="Self-Service Scoping & Assessment Dispatcher").is_visible()

def test_threat_intel_preserves_layout_without_exposing_unwired_replay(page, live_server):
    page.goto(f"{live_server}/ui-v2/threat-intel")
    assert page.get_by_text("Threat Intelligence · Local References", exact=True).is_visible()
    for label in ("Inspect Exploit Code", "Execute Curl Replay Test", "View Nuclei Heuristics"):
        assert page.get_by_role("button", name=label).count() == 0
    assert page.get_by_role("button", name="Refresh catalog").is_visible()


def test_compliance_page_hides_unimplemented_signed_export(page, live_server):
    page.goto(f"{live_server}/ui-v2/compliance")
    assert page.locator("#whaxon-live-compliance").count() == 1
    assert page.locator("button:visible").filter(has_text="Compile Signed Matrix").count() == 0



def test_compliance_header_reflects_live_scope_and_global_navigation(page, live_server):
    page.goto(f"{live_server}/ui-v2/compliance")
    page.wait_for_function(
        "() => document.querySelector('#compliance-status')?.textContent.includes('recorded finding(s)')"
        " || document.querySelector('#compliance-status')?.textContent.includes('Live data request timed out')",
        timeout=8000,
    )
    page.wait_for_function(
        "() => !document.querySelector('header')?.innerText.includes('api.internal.corp')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(response => response.json())")
    target = scope["in_scope"][0] if scope.get("in_scope") else "No target configured"
    header = page.locator("header").inner_text()
    assert target in header
    assert "SCOPE CONFIGURATION LOADED" in header or "SCOPE ENFORCEMENT DISABLED" in header

    page.get_by_role("button", name="Configure Scope").click()
    page.wait_for_url("**/ui-v2/scope")
    assert page.url.endswith("/ui-v2/scope")

    page.goto(f"{live_server}/ui-v2/compliance")
    page.locator("header button").filter(has_text="Terminal Log").click()
    page.wait_for_url("**/ui-v2/run")
    assert page.url.endswith("/ui-v2/run")


def test_compliance_header_halt_button_uses_live_job_history(page, live_server):
    page.goto(f"{live_server}/ui-v2/compliance")
    page.wait_for_function(
        "() => document.querySelector('#compliance-status')?.textContent.includes('recorded finding(s)')"
        " || document.querySelector('#compliance-status')?.textContent.includes('Live data request timed out')",
        timeout=8000,
    )
    page.locator("header button").filter(has_text="Emergency Halt Scan").click()
    page.wait_for_function(
        "() => document.querySelector('#compliance-status')?.textContent.includes('No running or queued jobs were found')",
        timeout=5000,
    )


def test_compliance_disables_disconnected_reference_controls(page, live_server):
    page.goto(f"{live_server}/ui-v2/compliance")
    page.wait_for_function(
        "() => document.querySelector('#compliance-status')?.textContent.includes('recorded finding(s)')"
        " || document.querySelector('#compliance-status')?.textContent.includes('Live data request timed out')",
        timeout=8000,
    )
    for button in page.locator("main button:visible").all():
        inside_panel = button.evaluate("(el) => el.closest('#whaxon-live-compliance') !== null")
        if inside_panel or "Configure Scope" in button.inner_text():
            continue
        assert button.is_disabled(), f"Unwired compliance reference control is enabled: {button.inner_text()}"

def test_threat_intel_header_uses_live_scope_and_real_navigation(page, live_server):
    page.goto(f"{live_server}/ui-v2/threat-intel")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('external threat-intelligence feed')"
        " || document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('Live catalog unavailable')",
        timeout=8000,
    )
    page.wait_for_function(
        "() => !document.querySelector('header')?.innerText.includes('api.internal.corp')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(response => response.json())")
    target = scope["in_scope"][0] if scope.get("in_scope") else "No target configured"
    header = page.locator("header").inner_text()
    assert target in header
    assert "SCOPE CONFIGURATION LOADED" in header or "SCOPE ENFORCEMENT DISABLED" in header

    page.locator("header button").filter(has_text="New").click()
    page.wait_for_url("**/ui-v2/scope")
    assert page.url.endswith("/ui-v2/scope")

    page.goto(f"{live_server}/ui-v2/threat-intel")
    page.locator("header button").filter(has_text="Terminal Log").click()
    page.wait_for_url("**/ui-v2/run")
    assert page.url.endswith("/ui-v2/run")


def test_threat_intel_halt_uses_live_history_and_demo_controls_are_disabled(page, live_server):
    page.goto(f"{live_server}/ui-v2/threat-intel")
    status = page.locator("#whaxon-live-threat-intel [role=status]")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('external threat-intelligence feed')"
        " || document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('Live catalog unavailable')",
        timeout=8000,
    )
    page.locator("header button").filter(has_text="Emergency Halt Scan").click()
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('No running or queued jobs were found')"
        " || document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('Emergency halt failed:')",
        timeout=5000,
    )
    for button in page.locator("main button:visible").all():
        inside_live_panel = button.evaluate("(el) => el.closest('#whaxon-live-threat-intel') !== null")
        if inside_live_panel:
            assert not button.is_disabled(), f"Live catalog control unexpectedly disabled: {button.inner_text()}"
        else:
            assert button.is_disabled(), f"Disconnected threat-intel control is enabled: {button.inner_text()}"
    assert page.get_by_role("button", name="Refresh catalog").is_enabled()

