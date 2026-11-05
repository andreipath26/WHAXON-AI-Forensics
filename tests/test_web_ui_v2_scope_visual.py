"""Scope UI candidate screenshots and automated accessibility; manual sign-off separate."""
import json
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("width", "height", "label"),
    [(1440, 900, "desktop"), (390, 844, "mobile")],
)
def test_scope_visual_candidate(page, live_server, width, height, label):
    page.set_viewport_size({"width": width, "height": height})
    response = page.goto(f"{live_server}/ui-v2/scope")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=12000,
    )
    page.evaluate("() => document.fonts.ready")
    output = Path("scope-visual-evidence")
    output.mkdir(exist_ok=True)
    page.screenshot(path=str(output / f"scope-{label}.png"), full_page=True)
    (output / f"scope-{label}.json").write_text(json.dumps({
        "viewport": {"width": width, "height": height},
        "page": "/ui-v2/scope",
        "background": page.evaluate("() => getComputedStyle(document.body).backgroundColor"),
        "source": "live seeded acceptance fixture — not owner-approved visual baseline",
    }, indent=2), encoding="utf-8")
    assert page.locator("main").is_visible()
    assert page.evaluate(
        "() => getComputedStyle(document.body).backgroundColor === 'rgb(15, 19, 28)'"
    )


@pytest.mark.parametrize(("width", "height"), [(1440, 900), (390, 844)])
def test_scope_automated_accessibility(page, live_server, width, height):
    axe = Path(__file__).resolve().parents[1] / "node_modules" / "axe-core" / "axe.min.js"
    assert axe.is_file(), "Dedicated acceptance workflow must install pinned axe-core"
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=12000,
    )
    page.add_script_tag(path=str(axe))
    result = page.evaluate(
        """async () => await axe.run(document, {
          runOnly:{type:'tag', values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}
        })"""
    )
    output = Path("scope-visual-evidence")
    output.mkdir(exist_ok=True)
    issues = [{"id": v["id"], "nodes": [n["target"] for n in v["nodes"]]}
              for v in result["violations"]]
    (output / f"scope-axe-{width}.json").write_text(
        json.dumps(issues, indent=2), encoding="utf-8")
    assert not issues, issues


def test_scope_mobile_nav_restores_viewport_and_keyboard_focus(page, live_server):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=12000,
    )
    assert page.evaluate("() => document.documentElement.scrollWidth <= innerWidth")
    button = page.get_by_role("button", name="Open Scope navigation")
    assert button.is_visible()
    assert page.locator("body > aside").get_attribute("aria-hidden") == "true"
    button.click()
    assert page.locator("body > aside").get_attribute("aria-hidden") == "false"
    assert button.get_attribute("aria-expanded") == "true"
    page.keyboard.press("Escape")
    assert button.get_attribute("aria-expanded") == "false"
    assert button.evaluate("(el) => document.activeElement === el")


def test_scope_mobile_primary_actions_are_accessible(page, live_server):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{live_server}/ui-v2/scope")
    page.wait_for_function(
        "() => document.querySelector('#scope-ui-notice')?.textContent.includes('Loaded the active scope')",
        timeout=12000,
    )
    assert page.locator("#openTargetModalBtn").is_visible()
    assert page.locator("#openImportDrawerBtn").is_visible()
