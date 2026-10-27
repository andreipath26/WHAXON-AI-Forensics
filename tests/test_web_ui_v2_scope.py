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
    assert "staging-api.corp.net" not in response.text()
    assert "api.internal.corp" not in response.text()
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_hidden()


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
