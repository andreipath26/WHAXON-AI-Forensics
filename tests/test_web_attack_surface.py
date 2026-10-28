"""Browser coverage for the legacy UI's live attack-surface graph."""
from __future__ import annotations

import json


def test_attack_surface_graph_renders_live_pivot_relationships(page, live_server):
    payload = {
        "edges": [
            {
                "parent": {"kind": "host", "id": "127.0.0.1"},
                "relation": "contains",
                "child": {"kind": "service", "id": "http"},
                "evidence": "browser-test-evidence",
                "created_at": 1700000000,
            }
        ]
    }
    page.route(
        "**/api/pivot/graph",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(payload),
        ),
    )
    page.goto(f"{live_server}/ui")
    page.locator('.sb-item[data-page="graph"]').click()
    page.wait_for_function(
        "() => document.querySelector('#graph-summary')?.textContent.includes('1 recorded relationship')",
        timeout=5000,
    )
    rows = page.locator("#graph-tbody").inner_text()
    assert "host: 127.0.0.1" in rows
    assert "contains" in rows
    assert "service: http" in rows
    assert "browser-test-evidence" in rows


def test_attack_surface_graph_shows_empty_state_for_no_pivot_edges(page, live_server):
    page.route(
        "**/api/pivot/graph",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"edges":[]}',
        ),
    )
    page.goto(f"{live_server}/ui")
    page.locator('.sb-item[data-page="graph"]').click()
    page.wait_for_function(
        "() => document.querySelector('#graph-summary')?.textContent.includes('0 recorded relationships')",
        timeout=5000,
    )
    assert "No pivot relationships have been recorded" in page.locator("#graph-tbody").inner_text()
