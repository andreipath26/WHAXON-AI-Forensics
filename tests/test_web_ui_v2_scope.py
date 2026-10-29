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



def test_scope_target_modal_saves_only_after_authorization_confirmation(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.locator("#openTargetModalBtn").click()
    assert page.locator("#targetModal").is_visible()
    page.locator("#modalTargetInput").fill("scope-ui-add.example.com")
    page.locator("#saveTargetBtn").click()
    assert "Confirm that written authorization exists" in page.locator("#scope-ui-notice").inner_text()
    assert "scope-ui-add.example.com" not in page.locator("#targetTableBody").inner_text()
    page.locator("#authConfirmCheckbox").check()
    page.locator("#saveTargetBtn").click()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
        timeout=8000,
    )
    assert "scope-ui-add.example.com" in page.locator("#targetTableBody").inner_text()
    scope = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    assert "scope-ui-add.example.com" in scope["in_scope"]


def test_scope_deny_rule_prompt_persists_explicit_exclusion(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.once("dialog", lambda dialog: dialog.accept("blocked-ui.example.com"))
    page.locator("#addDenyRuleBtn").click()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    assert "blocked-ui.example.com" in scope["out_of_scope"]
    assert "blocked-ui.example.com" in page.locator("body").inner_text()


def test_scope_json_import_persists_supported_scope_shape(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.locator("#openImportDrawerBtn").click()
    assert page.locator("#importDrawer").is_visible()
    page.locator("#importDrawer textarea").fill(
        '{"engagement":"UI import verification","enabled":true,"in_scope":["127.0.0.1","scope-import.example.com"],"out_of_scope":["blocked-import.example.com"],"notes":"browser test"}'
    )
    page.locator("#executeImportBtn").click()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    assert scope["engagement"] == "UI import verification"
    assert "scope-import.example.com" in scope["in_scope"]
    assert "blocked-import.example.com" in scope["out_of_scope"]
    assert "browser test" in scope["notes"]
    assert not page.locator("#importDrawer").is_visible()

def test_scope_page_does_not_claim_strict_boundary_enforcement(page, live_server):
    page.route(
        "**/api/scope",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"engagement":"scope-label-test","enabled":true,"in_scope":["example.com"],"out_of_scope":[],"notes":""}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    header = page.locator("header").inner_text()
    assert "SCOPE ENFORCEMENT ENABLED" in header
    assert "STRICT BOUNDARY ENFORCED" not in header

