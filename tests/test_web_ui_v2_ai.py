"""Browser coverage for the canonical scope-gated AI strategy gate."""
from __future__ import annotations


def test_ai_strategy_gate_loads_live_run_state(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/ai")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#ai-run-status')?.textContent.includes('Loading live')",
        timeout=5000,
    )
    assert page.locator("#whaxon-ai-gate").is_visible()
    assert page.locator("#ai-target").is_visible()
    assert page.locator("#ai-goal").is_visible()


def test_ai_strategy_gate_blocks_target_when_scope_check_denies(page, live_server):
    calls = []
    page.route("**/api/scope/check", lambda route: route.fulfill(status=200, content_type="application/json", body='{"allowed":false,"reason":"blocked by test"}'))
    page.route("**/api/ai/run", lambda route: calls.append(route.request.url) or route.fulfill(status=202, content_type="application/json", body='{"run_id":"should-not-run"}'))
    page.goto(f"{live_server}/ui-v2/ai")
    page.locator("#ai-target").fill("https://out-of-scope.invalid")
    page.locator("#ai-goal").fill("Test target scope guard")
    page.locator("#ai-run-form button[type=submit]").click()
    page.wait_for_function("() => document.querySelector('#ai-run-status')?.textContent.includes('blocked by test')")
    assert not calls


def test_dashboard_links_to_ai_strategy_gate(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="ai-strategy-gate"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/ai"

def test_ai_strategy_gate_submits_to_server_even_if_client_scope_check_is_spoofed(page, live_server):
    page.route(
        "**/api/scope/check",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"allowed":true,"reason":"client says allowed"}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/ai")
    page.wait_for_function(
        "() => document.documentElement.dataset.aiGateReady === 'true'",
        timeout=8000,
    )
    page.locator("#ai-target").fill("https://example.com")
    page.locator("#ai-goal").fill("Assess this explicitly out-of-scope target")
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith("/api/ai/run")
    ) as response_info:
        page.locator("#ai-run-form button[type=submit]").click()
    assert response_info.value.status == 403
    page.wait_for_function(
        "() => document.querySelector('#ai-run-status')?.textContent.toLowerCase().includes('out of scope')",
        timeout=8000,
    )


def test_ai_strategy_gate_authorize_button_records_real_pending_answer(page, live_server):
    calls = []

    def pending(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"id":"ai-pending-ui-test","goal":"test authorized phase transition","phase":"recon","pending_question":{"rationale":"Confirm the next phase","target":"127.0.0.1","confidence":0.9,"proposed_phase":"enum"}}]',
        )

    def runs(route):
        route.fulfill(status=200, content_type="application/json", body="[]")

    def answer(route):
        calls.append({"method": route.request.method, "body": route.request.post_data_json})
        route.fulfill(status=200, content_type="application/json", body='{"ok":true,"run_id":"ai-pending-ui-test","seq":1}')

    page.route("**/api/ai/pending", pending)
    page.route("**/api/ai/runs", runs)
    page.route("**/api/ai/runs/ai-pending-ui-test/answer", answer)
    page.goto(f"{live_server}/ui-v2/ai")
    page.wait_for_function(
        "() => document.querySelector('#ai-pending-list')?.textContent.includes('Confirm the next phase')",
        timeout=8000,
    )
    assert page.locator("#btn-authorize").is_enabled()
    page.locator("#btn-authorize").click()
    page.wait_for_function(
        "() => document.querySelector('#ai-run-status')?.textContent.includes('Operator response recorded')",
        timeout=8000,
    )
    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["body"]["answer"] == "yes"
    assert calls[0]["body"]["user"] == "local"


def test_ai_strategy_gate_emergency_halt_cancels_active_job(page, live_server):
    calls = []

    def history(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"id":"job-to-cancel","status":"running"}]',
        )

    def cancel(route):
        calls.append(route.request.method)
        route.fulfill(status=200, content_type="application/json", body='{"ok":true}')

    page.route("**/api/history", history)
    page.route("**/api/jobs/job-to-cancel/cancel", cancel)
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto(f"{live_server}/ui-v2/ai")
    page.wait_for_function(
        "() => document.documentElement.dataset.aiGateReady === 'true'",
        timeout=8000,
    )
    page.get_by_role("button", name="Emergency Halt Scan").click()
    page.wait_for_function(
        "() => document.querySelector('#ai-run-status')?.textContent.includes('1 of 1 active job(s)')",
        timeout=8000,
    )
    assert calls == ["POST"]


def test_ai_strategy_gate_hides_fake_wire_preview_and_disables_actions_without_pending_run(page, live_server):
    page.route("**/api/ai/pending", lambda route: route.fulfill(status=200, content_type="application/json", body="[]"))
    page.route("**/api/ai/runs", lambda route: route.fulfill(status=200, content_type="application/json", body="[]"))
    page.goto(f"{live_server}/ui-v2/ai")
    page.wait_for_function(
        "() => document.documentElement.dataset.aiGateReady === 'true'",
        timeout=8000,
    )
    assert page.locator("#btn-authorize").is_disabled()
    assert page.locator("#btn-reject").is_disabled()
    assert page.get_by_text("HTTP Request Wire Preview").is_hidden()
    assert page.locator("#ai-pending-list").inner_text().find("No AI runs are currently waiting") >= 0
    visible_text = page.locator("body").inner_text()
    assert "CVE-2023-38606" not in visible_text
    assert "staging-api.corp.net" not in visible_text
    assert "Nmap 7.94 detected" not in visible_text
    assert "+204ms" not in visible_text
    assert "buffer boundary stress" not in visible_text
    assert "89.4%" not in visible_text
    assert "89% probability" not in visible_text
    assert "Kiln/Ollama (Mistral-Offensive-7B)" not in visible_text
    assert "LOW RISK" not in visible_text
    assert "Nuclei basic tech-detect" not in visible_text
    assert "PTES 4: Vulnerability Analysis" not in visible_text
    assert "Synaptic-Planner v2.4" not in visible_text
    assert "OP//7749-ALPHA" not in visible_text
    assert "4 / 12 REMAINING" not in visible_text
    assert "DETERMINISTIC OK" not in visible_text
    assert "WX-8492-491" not in visible_text
    assert "94.2%" not in visible_text
    assert "78.1%" not in visible_text
    assert "98.0%" not in visible_text
    assert "50 req/sec" not in visible_text
    assert "Chain-of-Thought" not in visible_text
    assert "Live AI strategy gate" in visible_text
    assert "No AI action is currently awaiting approval" in visible_text
    assert "AI Planner proposes spawning Nuclei" not in visible_text
    assert "LIVE PROPOSAL DETAILS" in visible_text
    assert "AI ACTION DETAILS UNAVAILABLE" in visible_text
    assert "RECORDED PROPOSAL DETAILS" not in visible_text
    assert "Recorded Proposal Details" not in visible_text
    assert "Target: No target selected" in page.locator("header span").filter(has_text="Target:").first.text_content()
