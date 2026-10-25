"""Smoke tests for the default Obsidian Kinetic UI and legacy reference route."""
from __future__ import annotations


def test_server_is_reachable(page, live_server):
    page.goto(f"{live_server}/api/health/simple")
    body = page.text_content("body")
    assert body is not None
    assert "ok" in body.lower() or "healthy" in body.lower() or len(body) > 0


def test_root_and_ui_render_new_default(page, live_server):
    for path in ("/", "/ui"):
        page.goto(f"{live_server}{path}")
        assert page.title() == "WHAXON · Security Operations"
        assert page.locator("#main-nav .nav-item[data-view='overview']").count() == 1
        assert page.locator("#view-overview").count() == 1
        assert page.locator(".brand strong").text_content() == "WHAXON"


def test_new_ui_navigation_switches_views(page, live_server):
    page.goto(f"{live_server}/ui")
    page.click('.nav-item[data-view="scope"]')
    assert page.locator("#view-scope").is_visible()
    assert page.locator("#page-title").text_content() == "Scope & targets"
    page.click('.nav-item[data-view="run"]')
    assert page.locator("#view-run").is_visible()
    assert page.locator("#run-form").count() == 1
    page.click('.nav-item[data-view="evidence"]')
    assert page.locator("#view-evidence").is_visible()
    assert page.locator("#evidence-note-form").count() == 1


def test_new_ui_loads_live_tools_and_scope(page, live_server):
    page.goto(f"{live_server}/ui")
    page.wait_for_function("() => document.querySelector('#run-tool')?.options.length > 1", timeout=5000)
    page.click('.nav-item[data-view="scope"]')
    page.wait_for_function("() => document.querySelector('#scope-summary')?.textContent !== 'Loading scope…'", timeout=5000)
    assert page.locator("#scope-summary").text_content().strip()


def test_legacy_ui_remains_available_for_reference(page, live_server):
    page.goto(f"{live_server}/ui/legacy")
    assert page.locator(".sb-brand .label-text").text_content() == "WHAXON"
    assert page.locator("#page-findings").count() == 1
