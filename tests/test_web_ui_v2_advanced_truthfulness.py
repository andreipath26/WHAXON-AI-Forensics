"""Acceptance tests for advanced workspaces with intentionally limited integrations."""
from __future__ import annotations


def test_bas_workspace_uses_persisted_findings_and_disables_provider_actions(page, live_server):
    page.goto(f"{live_server}/ui-v2/bas")
    panel = page.locator("#whaxon-live-bas")
    assert panel.is_visible()
    page.wait_for_function(
        "() => document.querySelector('#bas-status')?.textContent.includes('persisted finding')"
        " || document.querySelector('#bas-status')?.textContent.includes('Live data unavailable')",
        timeout=8000,
    )
    assert page.get_by_role("button", name="Detonate Sequence").is_disabled()
    assert page.get_by_role("button", name="Deploy to Sentinel").is_disabled()
    assert page.get_by_role("button", name="Deploy to Splunk").is_disabled()
    for button in page.locator("main button:visible").all():
        if not button.evaluate("(el) => el.closest('#whaxon-live-bas') !== null"):
            assert button.is_disabled(), f"Unconnected BAS control remains enabled: {button.inner_text()}"


def test_compliance_workspace_filters_and_exports_only_recorded_findings(page, live_server):
    page.goto(f"{live_server}/ui-v2/compliance")
    panel = page.locator("#whaxon-live-compliance")
    assert panel.is_visible()
    page.wait_for_function(
        "() => document.querySelector('#compliance-status')?.textContent.includes('recorded finding')"
        " || document.querySelector('#compliance-status')?.textContent.includes('Live data unavailable')",
        timeout=8000,
    )
    search = panel.get_by_role("searchbox", name="Filter framework crosswalk")
    assert search.is_visible()
    search.fill("no-such-record-should-match")
    assert any(message in panel.inner_text() for message in ("No findings match this filter", "No recorded findings are available"))
    export = panel.get_by_role("button", name="Export crosswalk JSON")
    assert export.is_enabled()
    with page.expect_download() as download_info:
        export.click()
    assert download_info.value.suggested_filename == "whaxon-framework-crosswalk.json"
    assert page.get_by_role("button", name="Auditor Crosswalk PDF").count() == 0


def test_threat_intel_workspace_is_local_catalog_not_a_fake_live_feed(page, live_server):
    page.goto(f"{live_server}/ui-v2/threat-intel")
    panel = page.locator("#whaxon-live-threat-intel")
    assert panel.is_visible()
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('No connected external threat-intelligence feed')"
        " || document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('Live catalog unavailable')",
        timeout=10000,
    )
    assert panel.get_by_role("searchbox", name="Filter threat intelligence references").is_visible()
    refresh = panel.get_by_role("button", name="Refresh catalog")
    assert refresh.is_enabled()
    refresh.click()
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('locally recorded')"
        " || document.querySelector('#whaxon-live-threat-intel [role=status]')?.textContent.includes('Live catalog unavailable')",
        timeout=10000,
    )
    assert page.get_by_role("button", name="Sync Upstream Feeds").is_disabled()
    assert page.get_by_role("button", name="Inspect Exploit Code").count() == 0


def test_approvals_workspace_loads_real_queue_and_disables_demo_decisions(page, live_server):
    page.goto(f"{live_server}/ui-v2/approvals")
    panel = page.locator("#whaxon-live-approvals")
    assert panel.is_visible()
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-approvals p')?.textContent.includes('pending item(s)')"
        " || document.querySelector('#whaxon-live-approvals p')?.textContent.includes('Live data unavailable')",
        timeout=10000,
    )
    refresh = panel.get_by_role("button", name="Refresh queue")
    assert refresh.is_enabled()
    refresh.click()
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-approvals p')?.textContent.includes('pending item(s)')"
        " || document.querySelector('#whaxon-live-approvals p')?.textContent.includes('Live data unavailable')",
        timeout=10000,
    )
    for button in page.locator("main button:visible").all():
        if not button.evaluate("(el) => el.closest('#whaxon-live-approvals') !== null"):
            assert button.is_disabled(), f"Unwired approval control remains enabled: {button.inner_text()}"


def test_approvals_workspace_submits_operator_answer_to_waiting_run(page, live_server):
    page.goto(f"{live_server}/ui-v2/approvals")
    panel = page.locator("#whaxon-live-approvals")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-approvals p')?.textContent.includes('pending item(s)')",
        timeout=10000,
    )
    answer = panel.get_by_role("textbox", name="Answer for run seed-ai-approval-ui")
    assert answer.is_visible()
    answer.fill("Proceed with the next permitted phase.")
    note = panel.get_by_role("textbox", name="Approval note for run seed-ai-approval-ui")
    note.fill("Browser acceptance test")
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith("/api/ai/runs/seed-ai-approval-ui/answer")
    ) as response_info:
        panel.get_by_role("button", name="Submit answer").click()
    response = response_info.value
    assert response.status == 200
    assert response.json()["ok"] is True
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-approvals p')?.textContent.includes('Answer recorded for run seed-ai-approval-ui.')",
        timeout=10000,
    )
    assert panel.get_by_role("textbox", name="Answer for run seed-ai-approval-ui").count() == 0
    assert panel.get_by_role("textbox", name="Answer for run seed-ai-approval-ui").count() == 0
    approvals = page.evaluate(
        "() => fetch('/api/ai/runs/seed-ai-approval-ui').then(response => response.json())"
    )
    assert approvals["status"] in ("waiting", "running", "finished")
