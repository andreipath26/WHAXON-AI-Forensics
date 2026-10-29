"""Browser coverage for the live attack-chain graph page."""
from __future__ import annotations


def test_attack_chain_page_uses_live_graph_api(page, live_server):
    graph = page.request.get(f"{live_server}/api/pivot/graph")
    assert graph.status == 200
    assert isinstance(graph.json(), dict)
    response = page.goto(f"{live_server}/ui-v2/chains")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#chains-status')?.textContent.includes('Loading stored')",
        timeout=5000,
    )
    assert page.locator("#whaxon-live-chains").is_visible()
    assert page.locator("#chains-refresh").is_visible()


def test_dashboard_links_to_attack_chain_page(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="correlated-attack-chains"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/chains"

def test_attack_chain_page_never_displays_fictional_compromise_evidence(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/chains")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#chains-status')?.textContent.includes('relationship(s) returned') "
        "|| document.querySelector('#chains-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "dns-egress.corp",
        "K9#xL9!pQ_corp_secret",
        "AKIAIOSFODNN7EXAMPLE",
        "root:x:0:0:root",
        "sys_eval(",
        "ACTIVE EXPLOIT DETECTED",
        "LETHAL COMPROMISE",
        "Simulate Controlled Replay",
    ):
        assert marker not in visible, f"Fictional attack-chain fixture must not be shown: {marker}"
    assert page.locator("#whaxon-live-chains").is_visible()
    assert page.locator("#chains-refresh").is_enabled()

def test_attack_chain_page_renders_recorded_edges_and_refreshes(page, live_server):
    calls = {"count": 0}

    def graph(route):
        calls["count"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"edges":[{"parent":{"kind":"exploit","id":"job-a/finding-1"},"child":{"kind":"session","id":"job-b/finding-2"},"relation":"from_exploit","evidence":"recorded test evidence","created_at":1793260000}],"count":1}',
        )

    page.route("**/api/pivot/graph", graph)
    page.goto(f"{live_server}/ui-v2/chains")
    page.wait_for_function(
        "() => document.querySelector('#chains-status')?.textContent.includes('1 relationship(s) returned')",
        timeout=8000,
    )
    rendered = page.locator("#chains-list").inner_text()
    assert "exploit:job-a/finding-1" in rendered
    assert "session:job-b/finding-2" in rendered
    assert "from_exploit" in rendered
    assert "recorded test evidence" in rendered
    assert calls["count"] == 1

    page.get_by_role("button", name="Refresh").click()
    page.wait_for_function(
        "() => document.querySelector('#chains-status')?.textContent.includes('1 relationship(s) returned')",
        timeout=8000,
    )
    assert calls["count"] >= 2


def test_attack_chain_page_surfaces_graph_api_errors(page, live_server):
    page.route(
        "**/api/pivot/graph",
        lambda route: route.fulfill(
            status=503,
            content_type="application/json",
            body='{"error":"graph temporarily unavailable"}',
        ),
    )
    page.goto(f"{live_server}/ui-v2/chains")
    page.wait_for_function(
        "() => document.querySelector('#chains-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    assert "could not be loaded" in page.locator("#chains-status").inner_text()
