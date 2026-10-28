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
