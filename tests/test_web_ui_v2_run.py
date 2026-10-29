"""Browser coverage for the canonical Run & Orchestration page (UI v2)."""
from __future__ import annotations


def test_run_page_loads_live_tool_catalog(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/run")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => [...document.querySelector('#run-tool-select').options].some(o => o.value === 'echo')",
        timeout=8000,
    )
    assert page.locator("#run-target-input").count() == 1
    assert page.locator("#run-target-input").is_visible()
    assert page.locator("#run-active-btn").is_visible()
    assert page.locator("#run-passive-btn").is_visible()
    assert page.get_by_role("button", name="Spawn Sub-tool").is_hidden()
    assert page.get_by_role("button", name="Inject Payload").is_hidden()
    assert page.get_by_role("button", name="Emergency Abort").is_hidden()
    assert page.get_by_role("button", name="Execute").is_hidden()
    visible_text = page.locator("main").inner_text()
    assert "CVE-2023-38606" not in visible_text
    assert "184,209" not in visible_text
    assert "Recon: 100%" not in visible_text
    assert page.locator("#run-job-id").text_content() == "No job started"
    assert page.locator("#btn-pause").is_disabled()
    assert page.locator("#btn-pause-text").text_content() == "No Active Job"
    assert "staging-api.corp.net" not in response.text()
    assert "api.internal.corp" not in response.text()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="scope-and-targets"]').get_attribute("href") == "/ui-v2/scope"
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
    assert page.locator('a[data-path="trust-layer-and-findings"]').get_attribute("href") == "/ui-v2/findings"


def test_run_page_echo_job_streams_real_output(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => [...document.querySelector('#run-tool-select').options].some(o => o.value === 'echo')",
        timeout=8000,
    )
    page.locator("#run-tool-select").select_option("echo")
    page.locator("#run-target-input").fill("127.0.0.1")
    page.locator("#run-active-btn").click()
    page.wait_for_function(
        "() => document.querySelector('#run-job-status')?.textContent.toLowerCase().includes('finished')",
        timeout=15000,
    )
    assert page.locator("#run-job-id").text_content().strip() != "No job started"
    output = page.locator("#terminal-stdout").text_content()
    assert "Job" in output or "echo" in output.lower()
    assert "finished" in output.lower()


def test_run_page_does_not_start_out_of_scope_target(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => [...document.querySelector('#run-tool-select').options].some(o => o.value === 'echo')",
        timeout=8000,
    )
    page.locator("#run-tool-select").select_option("echo")
    page.locator("#run-target-input").fill("https://example.com")
    page.locator("#run-active-btn").click()
    page.wait_for_function(
        "() => document.querySelector('#run-ui-notice')?.textContent.includes('blocked by scope')",
        timeout=8000,
    )
    assert page.locator("#run-job-id").text_content() == "No job started"
    assert "outside configured scope" in page.locator("#terminal-stdout").text_content().lower()


def test_arbitrary_shell_input_is_disabled_and_execute_is_hidden(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    command_input = page.locator("#cli-input")
    assert command_input.is_disabled()
    assert "Shell commands are disabled" in command_input.get_attribute("placeholder")
    assert page.get_by_role("button", name="Execute").is_hidden()


def test_run_page_passive_button_starts_guarded_job(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => [...document.querySelector('#run-tool-select').options].some(o => o.value === 'echo')",
        timeout=8000,
    )
    page.locator("#run-tool-select").select_option("echo")
    page.locator("#run-target-input").fill("127.0.0.1")
    page.locator("#run-passive-btn").click()
    page.wait_for_function(
        "() => document.querySelector('#run-job-status')?.textContent.toLowerCase().includes('finished')",
        timeout=15000,
    )
    assert page.locator("#run-job-id").text_content().strip() != "No job started"
    assert "finished" in page.locator("#terminal-stdout").text_content().lower()


def test_run_page_cancel_button_cancels_active_job(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => [...document.querySelector('#run-tool-select').options].some(o => o.value === 'echo')",
        timeout=8000,
    )
    calls = []

    def fake_run(route):
        calls.append((route.request.method, route.request.url))
        route.fulfill(status=202, content_type="application/json", body='{"job_id":"ui-cancel-test"}')

    def fake_stream(route):
        route.fulfill(
            status=200,
            headers={"content-type": "text/event-stream", "cache-control": "no-cache"},
            body='retry: 60000\ndata: {"type":"status","status":"running"}\n\n',
        )

    def fake_cancel(route):
        calls.append((route.request.method, route.request.url))
        route.fulfill(status=200, content_type="application/json", body='{"ok":true}')

    page.route("**/api/run", fake_run)
    page.route("**/api/jobs/ui-cancel-test/stream", fake_stream)
    page.route("**/api/jobs/ui-cancel-test/cancel", fake_cancel)
    page.locator("#run-tool-select").select_option("echo")
    page.locator("#run-target-input").fill("127.0.0.1")
    page.locator("#run-active-btn").click()
    page.wait_for_function(
        "() => document.querySelector('#run-job-status')?.textContent === 'RUNNING'",
        timeout=8000,
    )
    assert page.locator("#btn-pause").is_enabled()
    page.wait_for_function(
        "() => Number.parseInt(document.querySelector('#elapsed-timer')?.textContent || '0', 10) >= 1",
        timeout=3000,
    )
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#btn-pause").click()
    page.wait_for_function(
        "() => document.querySelector('#run-job-status')?.textContent === 'CANCELLING'",
        timeout=5000,
    )
    assert any(method == "POST" and url.endswith("/api/jobs/ui-cancel-test/cancel") for method, url in calls)


def test_run_page_clear_buffer_clears_terminal_output(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => document.querySelector('#terminal-stdout')?.textContent.includes('No job output yet')",
        timeout=8000,
    )
    page.locator("button[title='Clear buffer']").click()
    assert page.locator("#terminal-stdout").inner_text().strip() == ""



def test_run_page_disables_ai_planner_toggle_without_scope_enforcement(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => [...document.querySelector('#run-tool-select').options].some(o => o.value === 'echo')",
        timeout=8000,
    )
    toggle = page.locator("#ai-planner-toggle")
    assert toggle.is_disabled()
    assert not toggle.is_checked()
    assert "does not enforce the same scope boundary" in toggle.get_attribute("title").lower()
    planner_card = toggle.locator("xpath=ancestor::div[contains(@class, 'bg-surface-container-low')][1]")
    assert "AI planner execution is disabled" in planner_card.inner_text()
    assert "GATE: NOT VERIFIED" in planner_card.inner_text()
    assert "GATE: ENFORCED" not in planner_card.inner_text()
    assert page.locator("#toggle-planner-gate").is_hidden()
