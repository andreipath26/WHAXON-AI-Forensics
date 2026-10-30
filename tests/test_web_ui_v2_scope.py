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
    table_footer = page.locator("#targetTableBody").locator("xpath=ancestor::div[contains(@class, 'overflow-x-auto')]/..").locator("div.p-space-md[class*='bg-surface-container-lowest']")
    assert "LIVE CONFIGURATION" in table_footer.inner_text()
    assert page.locator("#scopeTableStatus").get_attribute("aria-live") == "polite"
    assert page.locator("#scopeTableStatus").is_visible()
    assert "Pagination:" not in page.locator("body").inner_text()
    assert page.get_by_role("button", name="Next").count() == 0
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

def test_scope_header_does_not_claim_a_target_when_scope_is_empty(page, live_server):
    page.route(
        "**/api/scope",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"engagement":"empty-scope-test","enabled":true,"in_scope":[],"out_of_scope":[],"notes":""}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-header-boundary')?.textContent === 'NO TARGET RULE CONFIGURED'",
        timeout=8000,
    )
    assert page.locator("#scope-header-target").inner_text() == "Target: No target configured"
    assert page.locator("#scope-header-membership").inner_text() == "(NO TARGET RULE)"
    assert "(IN SCOPE)" not in page.locator("header").inner_text()
    assert "STRICT BOUNDARY ENFORCED" not in page.locator("header").inner_text()


def test_scope_header_reflects_disabled_enforcement(page, live_server):
    page.route(
        "**/api/scope",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"engagement":"disabled-scope-test","enabled":false,"in_scope":["example.test"],"out_of_scope":[],"notes":""}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-header-boundary')?.textContent === 'SCOPE ENFORCEMENT DISABLED'",
        timeout=8000,
    )
    assert page.locator("#scope-header-membership").inner_text() == "(ENFORCEMENT DISABLED)"
    assert "STRICT BOUNDARY ENFORCED" not in page.locator("header").inner_text()


def test_scope_runtime_header_uses_live_host_port_and_health(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-engine-state')?.textContent === 'API online'",
        timeout=8000,
    )
    location = page.evaluate("() => ({host: location.hostname, port: location.port || (location.protocol === 'https:' ? '443' : '80')})")
    assert page.locator("#scope-server-host").inner_text() == location["host"]
    assert page.locator("#scope-server-port").inner_text() == location["port"]
    assert page.locator("#scope-python-version").inner_text() == "Not reported"
    assert page.locator("#scope-sidebar-api-state").inner_text() == "API AVAILABLE"
    assert "OP//7749-ALPHA" not in page.locator("body").inner_text()
    assert "Lead Security Engineer" not in page.locator("body").inner_text()


def test_scope_runtime_header_reports_health_failure(page, live_server):
    page.route(
        "**/api/health/simple",
        lambda route: route.fulfill(
            status=503,
            content_type="application/json",
            body='{"ok":false}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-engine-state')?.textContent === 'API unavailable'",
        timeout=8000,
    )
    assert page.locator("#scope-sidebar-api-state").inner_text() == "API UNAVAILABLE"


def test_scope_demo_hosts_and_deny_rules_are_hidden_until_live_configuration(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    assert page.get_by_text("Discovered Hosts & SSL SAN Intake Queue").is_hidden()
    assert page.get_by_text("/auth/admin/*", exact=True).is_hidden()
    assert page.get_by_text("10.0.12.0/24 (Prod DBs)", exact=True).is_hidden()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    assert page.get_by_text("Discovered Hosts & SSL SAN Intake Queue").is_hidden()
    assert page.get_by_text("/auth/admin/*", exact=True).count() == 0
    assert page.get_by_text("10.0.12.0/24 (Prod DBs)", exact=True).count() == 0

def test_scope_registry_labels_do_not_overstate_assets_ports_or_authorization(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    body = page.locator("body").inner_text()
    assert "In-Scope Rules" in body
    assert "CIDR Rules" in body
    assert "Total In-Scope Assets" not in body
    assert "Discovery Mode" not in body
    assert "Allowed Ports" not in body
    assert "Authorization Record" in body
    assert "No evidence stored by scope API" in body
    assert "Explicit Exclusions" in body
    assert "Strict Deny Rules" not in body

def test_scope_registry_edits_and_persists_existing_rules(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.evaluate("""async () => {
      const scope = await fetch('/api/scope').then(r => r.json());
      scope.in_scope.push('scope-edit-before.example.com');
      await fetch('/api/scope', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(scope)});
    }""")
    page.reload()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.once("dialog", lambda dialog: dialog.accept("scope-edit-after.example.com"))
    page.get_by_role("button", name="Edit in scope rule scope-edit-before.example.com").click()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    assert "scope-edit-after.example.com" in scope["in_scope"]
    assert "scope-edit-before.example.com" not in scope["in_scope"]
    assert "scope-edit-after.example.com" in page.locator("#targetTableBody").inner_text()


def test_scope_registry_removes_rule_after_confirmation(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.evaluate("""async () => {
      const scope = await fetch('/api/scope').then(r => r.json());
      scope.in_scope.push('scope-remove-test.example.com');
      await fetch('/api/scope', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(scope)});
    }""")
    page.reload()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Remove in scope rule scope-remove-test.example.com").click()
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(r => r.json())")
    assert "scope-remove-test.example.com" not in scope["in_scope"]
    assert "scope-remove-test.example.com" not in page.locator("#targetTableBody").inner_text()


def test_scope_registry_shows_empty_state_and_filter_no_match(page, live_server):
    page.route(
        "**/api/scope",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"engagement":"empty-scope-test","enabled":true,"in_scope":[],"out_of_scope":[],"notes":""}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/scope")
    assert page.locator("#scope-empty-state").is_visible()
    assert "No scope rules configured" in page.locator("#scope-empty-state").inner_text()
    page.locator("#targetFilterInput").fill("missing")
    assert "No scope rules configured" in page.locator("#scope-empty-state").inner_text()


def test_scope_registry_filter_reports_no_matching_rules(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )
    page.locator("#targetFilterInput").fill("this-rule-does-not-exist")
    assert page.locator("#scope-empty-state").is_visible()
    assert "No scope rules match this filter" in page.locator("#scope-empty-state").inner_text()
    page.locator("#targetFilterInput").fill("")
    assert page.locator("#scope-empty-state").count() == 0
    assert page.locator("#targetTableBody tr").count() >= 1
