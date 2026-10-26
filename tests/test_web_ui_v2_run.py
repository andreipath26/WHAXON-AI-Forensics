"""Browser tests for the canonical guarded run page."""
from __future__ import annotations


def _open_run_v2(page, live_server):
    page.goto(f"{live_server}/ui-v2/run")
    page.wait_for_function(
        "() => document.querySelectorAll('#run-tool-list [data-tool-id]').length > 0",
        timeout=5000,
    )


def test_run_v2_loads_live_catalog_and_history(page, live_server):
    _open_run_v2(page, live_server)
    assert int(page.locator("#run-kpi-tools").text_content()) > 0
    assert page.locator("#run-history").is_visible()
    assert page.locator('[data-tool-id="echo"]').count() == 1


def test_run_v2_executes_echo_through_backend(page, live_server):
    _open_run_v2(page, live_server)
    page.locator('[data-tool-id="echo"]').click()
    page.fill("#run-target", "127.0.0.1")
    page.click("#run-submit")
    page.wait_for_function(
        "() => document.querySelector('#run-job-label').textContent.includes('finished')",
        timeout=10000,
    )
    assert "127.0.0.1" in page.locator("#run-output").text_content()


def test_run_v2_rejects_out_of_scope_target_before_starting_job(page, live_server):
    _open_run_v2(page, live_server)
    page.locator('[data-tool-id="echo"]').click()
    page.fill("#run-target", "google.com")
    page.click("#run-submit")
    page.wait_for_function(
        "() => !document.querySelector('#run-message').classList.contains('hidden')",
        timeout=5000,
    )
    assert "not authorized" in page.locator("#run-message").text_content().lower() or "no matching" in page.locator("#run-message").text_content().lower()
    assert "No job running" in page.locator("#run-job-label").text_content()


def test_run_v2_shows_only_implemented_navigation(page, live_server):
    _open_run_v2(page, live_server)
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
    assert page.locator('a[data-path="ptes-coverage-and-reports"]').is_visible()
