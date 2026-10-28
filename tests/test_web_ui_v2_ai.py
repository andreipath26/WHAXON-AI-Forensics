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
