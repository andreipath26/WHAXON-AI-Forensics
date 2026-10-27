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
    assert "PTES Coverage" not in visible_text
    assert page.locator("#run-job-id").text_content() == "No job started"
    assert "staging-api.corp.net" not in response.text()
    assert "api.internal.corp" not in response.text()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="scope-and-targets"]').is_hidden()


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


def test_arbitrary_terminal_commands_are_rejected_in_ui(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.locator("#cli-input").fill("whoami")
    page.locator("#cli-input").press("Enter")
    assert "Arbitrary shell commands are not supported" in page.locator("#run-ui-notice").text_content()
