"""Browser coverage for the canonical findings UI (UI v2)."""
from __future__ import annotations

import re


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
    assert page.locator('a[data-path="trust-layer-and-findings"]').is_visible()
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="scope-and-targets"]').get_attribute("href") == "/ui-v2/scope"
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').get_attribute("href") == "/ui-v2/run"
    # Reports are now part of the integrated UI, so navigation must lead to the real report route.
    reports = page.locator('a[data-path="ptes-coverage-and-reports"]')
    assert reports.is_visible()
    assert reports.get_attribute("href") == "/ui-v2/report"


def test_findings_page_has_no_hardcoded_demo_evidence(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/findings")
    assert response is not None
    html = response.text()
    assert "staging-api.corp.net" not in html
    assert "redacted_token_sess_089" not in html
    assert "5055ms" not in html
    assert "Baseline: 34ms" not in html


def test_replay_button_posts_to_live_validation_route(page, live_server):
    calls = []

    def respond(route):
        calls.append((route.request.method, route.request.url))
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"verified","reason":"browser test response"}',
        )

    page.route("**/api/validate/**", respond)
    page.route("**/api/retest/**", respond)
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length > 0",
        timeout=5000,
    )
    page.locator("#whaxon-findings-list [data-finding-index]").first.click()
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and ("/api/validate/" in response.url or "/api/retest/" in response.url)
    ) as response_info:
        page.locator("#replay-btn").click()
    assert response_info.value.ok
    assert calls and calls[0][0] == "POST"
    assert "/api/validate/" in calls[0][1] or "/api/retest/" in calls[0][1]


def test_finding_filter_chips_toggle_off_and_heading_tracks_visible_count(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length > 0",
        timeout=8000,
    )
    total = page.locator("#whaxon-findings-list [data-finding-index]:visible").count()
    heading = page.locator("#whaxon-findings-heading")
    assert "shown of" in heading.inner_text().lower()
    assert "4 in buffer" not in heading.inner_text().lower()

    verified_filter = page.get_by_role("button", name=re.compile(r"VERIFIED"))
    verified_filter.click()
    verified_filter.click()
    page.wait_for_function(
        "(total) => Array.from(document.querySelectorAll('#whaxon-findings-list [data-finding-index]')).filter(el => getComputedStyle(el).display !== 'none').length === total",
        arg=total,
        timeout=5000,
    )
    assert heading.inner_text().lower() == f"attack surface findings ({total} shown of {total})"

    search = page.locator("#whaxon-finding-filter")
    search.fill("no-such-finding-token-90210")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list #whaxon-findings-empty').length === 1",
        timeout=5000,
    )
    assert page.locator("#whaxon-findings-list [data-finding-index]:visible").count() == 0
    search.fill("")
    page.wait_for_function(
        "(total) => Array.from(document.querySelectorAll('#whaxon-findings-list [data-finding-index]')).filter(el => getComputedStyle(el).display !== 'none').length === total",
        arg=total,
        timeout=5000,
    )
    assert page.locator("#whaxon-findings-list #whaxon-findings-empty").count() == 0

def test_findings_search_includes_structured_data_and_evidence_falls_back_to_raw_line(page, live_server):
    page.goto(f"{live_server}/ui-v2/findings")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length > 0",
        timeout=8000,
    )

    # "protocol" exists in the structured finding data, not the scanner raw line.
    search = page.locator("#whaxon-finding-filter")
    search.fill("protocol")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length === 2",
        timeout=5000,
    )
    assert page.locator("#whaxon-findings-list [data-finding-index]").count() == 2

    search.fill("")
    page.wait_for_function(
        "() => document.querySelectorAll('#whaxon-findings-list [data-finding-index]').length === 3",
        timeout=5000,
    )
    ssh_finding = page.locator("#whaxon-findings-list [data-finding-index]").filter(has_text="22/tcp open ssh").first
    ssh_finding.click()
    proof = page.locator("#curl-proof-payload")
    assert "22/tcp open ssh OpenSSH 9.6" in proof.inner_text()
    assert "Retest Outcomes" in page.locator("main").inner_text()
    assert "Refuted" in page.locator("#whaxon-kpi-fixed").evaluate("(el) => el.parentElement.innerText")
