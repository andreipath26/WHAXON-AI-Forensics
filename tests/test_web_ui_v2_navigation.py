"""Cross-page browser coverage for the integrated canonical UI v2 pages."""
from __future__ import annotations


def test_core_pages_navigate_without_leaving_ui_v2(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/findings")
    assert response is not None and response.status == 200

    page.locator('a[data-path="dashboard-zero-state"]').click()
    assert page.url.endswith("/ui-v2")
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()

    page.locator('a[data-path="scope-and-targets"]').click()
    assert page.url.endswith("/ui-v2/scope")
    assert page.locator("h1").first.is_visible()

    page.locator('a[data-path="run-and-orchestration"]').click()
    assert page.url.endswith("/ui-v2/run")
    assert page.locator("#run-target-input").is_visible()

    page.locator('a[data-path="trust-layer-and-findings"]').click()
    assert page.url.endswith("/ui-v2")
    assert page.locator('a[data-path="dashboard-zero-state"]').get_attribute("href") == "/ui-v2"
    assert page.locator('a[data-path="scope-and-targets"]').is_visible()


def test_ui_v2_entry_route_opens_integrated_interface(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    assert page.url.endswith("/ui-v2/findings")
    assert page.locator("#whaxon-findings-list").is_visible()


def test_dashboard_uses_live_state_and_hides_fake_engagements(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('table tbody')?.textContent.includes('No job history') "
        "|| document.querySelector('table tbody tr')?.textContent.length > 0",
        timeout=5000,
    )
    html = response.text()
    assert "api.internal.corp" not in html
    assert "identity.gateway.corp" not in html
    assert "CVE-2023-38606" not in html
    assert page.locator('a[data-path="scope-and-targets"]').get_attribute("href") == "/ui-v2/scope"
    assert page.locator('a[data-path="run-and-orchestration"]').get_attribute("href") == "/ui-v2/run"
    assert page.locator('a[data-path="trust-layer-and-findings"]').get_attribute("href") == "/ui-v2/findings"
