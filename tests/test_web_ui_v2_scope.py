"""Browser tests for the canonical scope page and live scope API wiring."""
from __future__ import annotations


def _open_scope_v2(page, live_server):
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-kpi-in').textContent.trim() !== '—'",
        timeout=5000,
    )


def test_scope_v2_renders_live_rules_and_counts(page, live_server):
    _open_scope_v2(page, live_server)
    assert page.locator("#scope-kpi-in").text_content().strip() == "7"
    assert page.locator("#scope-in-table tr").count() == 7
    assert "default" in page.locator("#scope-engagement-label").text_content()


def test_scope_v2_checks_allowed_target(page, live_server):
    _open_scope_v2(page, live_server)
    page.fill("#scope-check-target", "127.0.0.1")
    page.click("#scope-check-submit")
    page.wait_for_function(
        "() => document.querySelector('#scope-check-result').textContent.includes('ALLOWED')",
        timeout=5000,
    )
    assert "127.0.0.1" in page.locator("#scope-check-result").text_content()


def test_scope_v2_denies_out_of_scope_target(page, live_server):
    _open_scope_v2(page, live_server)
    page.fill("#scope-check-target", "google.com")
    page.click("#scope-check-submit")
    page.wait_for_function(
        "() => document.querySelector('#scope-check-result').textContent.includes('DENIED')",
        timeout=5000,
    )
    assert "google.com" in page.locator("#scope-check-result").text_content()


def test_scope_v2_shows_wired_navigation_and_hides_unfinished(page, live_server):
    _open_scope_v2(page, live_server)
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="ptes-coverage-and-reports"]').is_visible()
