"""Browser coverage for the canonical WHAXON v2 dashboard."""
from __future__ import annotations


def test_dashboard_loads_and_routes_only_to_wired_core_pages(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    assert "Dashboard / Zero State" in response.text()
    assert page.locator('a[data-path="scope-and-targets"]').get_attribute("href") == "/ui-v2/scope"
    assert page.locator('a[data-path="run-and-orchestration"]').get_attribute("href") == "/ui-v2/run"
    visible = page.locator("body").inner_text()
    assert "staging-api.corp.net" not in visible
    assert "CVE-2023-38606" not in visible
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()
    assert page.locator('a[data-path="run-and-orchestration"]').is_visible()

def test_browser_navigation_headers_do_not_block_get_routes(page, live_server):
    response = page.request.get(
        f"{live_server}/ui-v2",
        headers={
            "Sec-Fetch-Site": "cross-site",
            "Origin": "https://untrusted.example",
        },
    )
    assert response.status == 200

def test_every_visible_dashboard_navigation_link_resolves_to_a_live_page(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200

    links = page.locator('a[data-path]:visible').evaluate_all(
        "(anchors) => anchors.map(a => ({label: a.innerText.trim(), href: a.getAttribute('href')}))"
    )
    assert links, "The dashboard should expose its wired navigation links."

    for link in links:
        href = link["href"]
        assert href and href != "#", f"Visible navigation item is not wired: {link['label']}"
        page_response = page.request.get(f"{live_server}{href}")
        assert page_response.status == 200, (
            f"Navigation item {link['label']!r} points to {href!r}, "
            f"which returned HTTP {page_response.status}"
        )

def test_dashboard_hides_inert_controls_and_illustrative_claims(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    for label in (
        "Deploy Mock",
        "Update Credentials Now",
        "Switch Target Session",
        "Upload Artifact",
        "Export Archive",
        "Inspect Ledger",
        "Audit Pack",
    ):
        assert page.get_by_role("button", name=label).count() == 0, (
            f"Inert dashboard control should not be visible: {label}"
        )
    assert page.locator("button:visible").count() == 0
    visible = page.locator("body").inner_text()
    assert "api.internal.corp" not in visible
    assert "ENG-2026-X892" not in visible
    assert "FINDING-SQLI-001" not in visible

