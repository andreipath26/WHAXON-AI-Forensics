"""Browser coverage for the canonical findings UI (UI v2)."""
from __future__ import annotations


def test_canonical_findings_page_loads_live_report(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => { const el = document.querySelector('#whaxon-findings-count'); "
        "return el && !el.textContent.includes('Loading'); }",
        timeout=5000,
    )
    assert page.locator("#whaxon-findings-list button[data-finding-index]").count() == 3
    assert page.locator("#whaxon-findings-list").inner_text().find(
        "SQLi: Time-based Blind"
    ) == -1


def test_canonical_findings_page_inspects_real_finding(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list button[data-finding-index]').length > 0",
        timeout=5000,
    )
    page.locator("#whaxon-findings-list button[data-finding-index]").first.click()
    detail = page.locator("#whaxon-detail")
    assert detail.is_visible()
    assert detail.get_by_text("Selected finding").count() == 1
    assert detail.get_by_text("Job ID").count() == 1


def test_wired_navigation_is_visible_and_unfinished_navigation_is_hidden(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list button[data-finding-index]').length > 0",
        timeout=5000,
    )
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert not page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
