"""Browser and API coverage for the canonical scope UI (UI v2)."""
from __future__ import annotations


def test_scope_page_loads_live_configuration(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/scope")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=5000,
    )
    assert page.locator("#targetTableBody tr").count() >= 1
    assert page.get_by_text("Allowed Ports Range").is_hidden()
    assert page.get_by_text("Rate Limit Threshold").is_hidden()
    assert page.get_by_text("Written Authorization Reference / Contract ID").is_hidden()
    assert "10.0.12.0/24 (Prod DBs)" not in page.locator("main").inner_text()
    assert "staging-api.corp.net" not in response.text()
    assert "api.internal.corp" not in response.text()
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').get_attribute("href") == "/ui-v2/run"
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
    assert page.locator('a[data-path="trust-layer-and-findings"]').get_attribute("href") == "/ui-v2/findings"


def test_scope_api_rejects_malformed_rules_without_changing_config(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    before = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    result = page.evaluate(
        """async (scope) => {
          const response = await fetch('/api/scope', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({...scope, in_scope: ['https://evil.example/path']})
          });
          return {status: response.status, body: await response.json()};
        }""",
        before,
    )
    assert result["status"] == 400
    after = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    assert after["in_scope"] == before["in_scope"]


def test_scope_api_requires_explicit_confirmation_to_disable(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    before = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    result = page.evaluate(
        """async (scope) => {
          const response = await fetch('/api/scope', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({...scope, enabled: false})
          });
          return {status: response.status, body: await response.json()};
        }""",
        before,
    )
    assert result["status"] == 400
    assert "confirm_disable=true" in result["body"]["error"]


def test_scope_api_persists_valid_configuration(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    before = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    saved = page.evaluate(
        """async (scope) => {
          const response = await fetch('/api/scope', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(scope)
          });
          return {status: response.status, body: await response.json()};
        }""",
        before,
    )
    assert saved["status"] == 200
    assert saved["body"]["in_scope"] == before["in_scope"]
    assert saved["body"]["out_of_scope"] == before["out_of_scope"]

def test_scope_check_button_calls_live_scope_api(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=5000,
    )
    page.locator("#scopeCheckTarget").fill("127.0.0.1")
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith("/api/scope/check")
    ) as response_info:
        page.locator("#runScopeCheckBtn").click()
    assert response_info.value.ok
    page.wait_for_function(
        "() => document.querySelector('#scopeCheckResult')?.textContent.includes('ALLOWED')",
        timeout=5000,
    )

def test_scope_rules_remain_editable_after_enforcement_is_disabled(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    before = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    disabled = page.evaluate(
        """async (scope) => {
          const response = await fetch('/api/scope', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({...scope, enabled: false, confirm_disable: true})
          });
          return {status: response.status, body: await response.json()};
        }""",
        before,
    )
    assert disabled["status"] == 200
    saved = page.evaluate(
        """async (scope) => {
          const response = await fetch('/api/scope', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({...scope, in_scope: [...scope.in_scope, 'scope-edit.example.com']})
          });
          return {status: response.status, body: await response.json()};
        }""",
        disabled["body"],
    )
    assert saved["status"] == 200
    assert "scope-edit.example.com" in saved["body"]["in_scope"]
    assert saved["body"]["enabled"] is False
