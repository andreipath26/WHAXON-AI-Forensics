"""Browser coverage for the canonical attack-surface monitoring page."""
from __future__ import annotations


def test_monitoring_page_loads_canonical_design_and_live_state(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/monitoring")
    assert response is not None and response.status == 200
    assert page.locator("#asset-ledger-container").count() == 1
    page.wait_for_function(
        """() => {
          const node = document.querySelector("#asset-ledger-container");
          return node && !node.textContent.includes("Loading recorded WHAXON jobs");
        }""",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    assert "api.internal.corp" not in visible
    assert "ENG-2026-X892" not in visible
    assert "CVE-2023-38606" not in visible
    assert "uid=0(root)" not in visible
    assert "184,209" not in visible
    assert "99.4%" not in visible
    assert "Rogue Port Exposed" not in visible
    assert "DAEMON: HOURLY SYNCHRONOUS SCAN ACTIVE" not in visible
    assert "PAGE 1 OF 6" not in visible
    assert page.locator("#asset-search-input").is_visible()
    assert page.locator("#asset-ledger-container .asset-card").count() == 0


def test_monitoring_page_uses_live_apis_and_hides_unsupported_controls(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/monitoring")
    assert response is not None and response.status == 200
    assert page.locator("#asset-search-input").count() == 1
    assert page.get_by_role("button", name="Emergency Halt Scan").count() == 0
    assert page.get_by_role("button", name="Trigger Delta Recon Now").count() == 0
