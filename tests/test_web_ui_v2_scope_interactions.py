"""Browser interaction tests for the canonical Scope & Targets page."""
from __future__ import annotations

import json


def _read_scope(page):
    return page.evaluate("() => fetch('/api/scope').then(response => response.json())")


def _save_scope(page, scope):
    return page.evaluate(
        """async (value) => {
          const response = await fetch('/api/scope', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(value)
          });
          return {status: response.status, body: await response.json()};
        }""",
        scope,
    )


def _wait_loaded(page):
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=8000,
    )


def test_scope_modal_requires_authorization_and_persists_target(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    before = _read_scope(page)
    target = "scope-modal-test.example.invalid"
    try:
        page.locator("#openTargetModalBtn").click()
        page.locator("#modalTargetInput").fill(target)
        page.locator("#saveTargetBtn").click()
        assert "Confirm that written authorization exists" in page.locator("#scope-ui-notice").inner_text()
        assert target not in _read_scope(page)["in_scope"]

        page.locator("#authConfirmCheckbox").check()
        page.locator("#saveTargetBtn").click()
        page.wait_for_function(
            "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
            timeout=5000,
        )
        assert target in _read_scope(page)["in_scope"]
        assert page.locator("#targetModal").is_hidden()
    finally:
        _save_scope(page, before)


def test_scope_target_filter_filters_live_rows(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    rows = page.locator("#targetTableBody tr")
    assert rows.count() >= 1
    target = rows.first.locator("td").first.inner_text().strip()
    filter_input = page.locator("#targetFilterInput")
    filter_input.fill(target)
    assert page.locator("#targetTableBody tr:visible").count() >= 1
    filter_input.fill("no-such-scope-rule-987654")
    assert page.locator("#targetTableBody tr:visible").count() == 1
    assert "No scope rules match this filter" in page.locator("#scope-empty-state").inner_text()


def test_scope_import_drawer_imports_scope_json_and_closes(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    before = _read_scope(page)
    imported = {
        **before,
        "engagement": "Scope import browser test",
        "in_scope": ["scope-import.example.invalid"],
        "out_of_scope": ["scope-excluded.example.invalid"],
        "notes": "browser test import",
    }
    try:
        page.locator("#openImportDrawerBtn").click()
        assert page.locator("#importDrawer").is_visible()
        assert page.locator("#importDrawer button", has_text="scope.json").is_disabled()
        assert page.locator("#importDrawer button", has_text="Burp XML/JSON").is_hidden()
        assert page.locator("#importDrawer button", has_text="CIDR List").is_hidden()
        page.locator("#importDrawer textarea").fill(json.dumps(imported))
        page.locator("#executeImportBtn").click()
        page.wait_for_function(
            "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
            timeout=5000,
        )
        after = _read_scope(page)
        assert after["in_scope"] == imported["in_scope"]
        assert after["out_of_scope"] == imported["out_of_scope"]
        assert page.locator("#importDrawer").is_hidden()
    finally:
        _save_scope(page, before)


def test_scope_add_boundary_exclusion_persists_and_can_be_restored(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    before = _read_scope(page)
    rule = "scope-deny-test.example.invalid"
    try:
        page.once("dialog", lambda dialog: dialog.accept(rule))
        page.locator("#addDenyRuleBtn").click()
        page.wait_for_function(
            "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
            timeout=5000,
        )
        assert rule in _read_scope(page)["out_of_scope"]
    finally:
        _save_scope(page, before)


def test_scope_remove_rule_requires_confirmation_and_persists(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    before = _read_scope(page)
    field = "in_scope" if before.get("in_scope") else "out_of_scope"
    assert before.get(field), "test fixture needs at least one scope rule"
    target = before[field][0]
    try:
        page.once("dialog", lambda dialog: dialog.accept())
        row = page.locator("#targetTableBody tr").filter(has_text=target).first
        row.get_by_role("button", name="Remove").click()
        page.wait_for_function(
            "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Scope saved')",
            timeout=5000,
        )
        assert target not in _read_scope(page)[field]
    finally:
        _save_scope(page, before)


def test_scope_header_reflects_disabled_enforcement(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    before = _read_scope(page)
    try:
        disabled = {**before, "enabled": False, "confirm_disable": True}
        result = _save_scope(page, disabled)
        assert result["status"] == 200
        page.reload()
        _wait_loaded(page)
        assert "SCOPE ENFORCEMENT DISABLED" in page.locator("header").inner_text()
    finally:
        _save_scope(page, before)

def test_scope_header_shows_the_actual_configured_target(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    scope = _read_scope(page)
    target = scope["in_scope"][0] if scope.get("in_scope") else "No target configured"
    assert target in page.locator("header").inner_text()


def test_scope_dialogs_support_escape_and_restore_focus(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    target_trigger = page.locator("#openTargetModalBtn")
    target_trigger.click()
    assert page.locator("#targetModal").get_attribute("role") == "dialog"
    assert page.locator("#targetModal").get_attribute("aria-modal") == "true"
    assert page.locator("#modalTargetInput").evaluate("(el) => el === document.activeElement")
    page.keyboard.press("Escape")
    assert page.locator("#targetModal").is_hidden()
    assert target_trigger.evaluate("(el) => el === document.activeElement")
    page.keyboard.press("Enter")
    page.keyboard.press("Shift+Tab")
    assert page.locator("#closeTargetModalBtn").evaluate("(el) => el === document.activeElement")
    page.keyboard.press("Shift+Tab")
    assert page.locator("#saveTargetBtn").evaluate("(el) => el === document.activeElement")
    page.keyboard.press("Escape")

    import_trigger = page.locator("#openImportDrawerBtn")
    import_trigger.click()
    assert page.locator("#importDrawer").get_attribute("aria-hidden") == "false"
    assert page.locator("#importDrawer textarea").evaluate("(el) => el === document.activeElement")
    page.keyboard.press("Escape")
    assert page.locator("#importDrawer").is_hidden()
    assert import_trigger.evaluate("(el) => el === document.activeElement")


def test_scope_text_inputs_have_accessible_names(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    _wait_loaded(page)
    assert page.get_by_role("textbox", name="Filter configured scope rules").is_visible()
    assert page.get_by_role("textbox", name="Check a target against the active scope").is_visible()
    page.locator("#openTargetModalBtn").click()
    assert page.get_by_role(
        "textbox", name="Authorized target hostname, IP address, or CIDR"
    ).is_visible()
    page.keyboard.press("Escape")
    page.locator("#openImportDrawerBtn").click()
    assert page.get_by_role("textbox", name="Paste scope JSON definition").is_visible()
