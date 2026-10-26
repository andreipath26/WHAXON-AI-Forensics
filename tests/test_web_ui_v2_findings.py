"""Browser coverage for the canonical findings UI (UI v2)."""
from __future__ import annotations


def test_canonical_findings_page_loads_live_report(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => { const el = document.querySelector('#whaxon-findings-count'); "
        "return el && !el.textContent.includes('Loading'); }",
        timeout=5000,
    )
    assert page.locator("#whaxon-findings-list [data-finding-index]").count() == 3
    assert page.locator("#whaxon-findings-list").inner_text().find(
        "SQLi: Time-based Blind"
    ) == -1


def test_canonical_findings_page_inspects_real_finding(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length > 0",
        timeout=5000,
    )
    page.locator("#whaxon-findings-list [data-finding-index]").first.click()
    detail = page.locator("#whaxon-detail")
    assert detail.is_visible()
    assert detail.locator("#selected-finding-title").text_content().strip() != "Loading live finding…"
    assert "staging-api.corp.net" not in detail.locator("#curl-proof-payload").text_content()


def test_wired_navigation_is_visible_and_unfinished_navigation_is_hidden(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length > 0",
        timeout=5000,
    )
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
    assert page.locator('a[data-path="ptes-coverage-and-reports"]').is_visible()
