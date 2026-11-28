"""Desktop keyboard and accessible-name checks for every V2 sidebar route.

This is internal browser evidence for shared navigation only; it does not close
page-control, visual-design, assistive-technology, or deployment acceptance.
"""
from __future__ import annotations

ROUTES = (
    "/ui-v2",
    "/ui-v2/dashboard",
    "/ui-v2/scope",
    "/ui-v2/run",
    "/ui-v2/findings",
    "/ui-v2/report",
    "/ui-v2/reports",
    "/ui-v2/history",
    "/ui-v2/diagnostics",
    "/ui-v2/evidence",
    "/ui-v2/ai",
    "/ui-v2/retest",
    "/ui-v2/chains",
    "/ui-v2/adapters",
    "/ui-v2/settings",
    "/ui-v2/audit",
    "/ui-v2/monitoring",
    "/ui-v2/bas",
    "/ui-v2/bug-bounty",
    "/ui-v2/compliance",
    "/ui-v2/ptaas",
    "/ui-v2/threat-intel",
    "/ui-v2/approvals",
)


def test_sidebar_links_are_named_focusable_and_keyboard_ordered(page, live_server):
    """Every page exposes named navigation links in the sidebar's tab order."""
    for route in ROUTES:
        response = page.goto(f"{live_server}{route}")
        assert response is not None and response.ok, route

        links = page.locator("aside nav a:visible")
        count = links.count()
        assert count > 0, f"{route}: no visible sidebar links"

        for index in range(count):
            link = links.nth(index)
            name = link.evaluate(
                "node => (node.getAttribute('aria-label') || node.innerText || node.title || '').trim()"
            )
            assert name, f"{route}: sidebar link {index} has no accessible name"
            assert link.get_attribute("href") in ROUTES, (
                f"{route}: sidebar link {name!r} has a non-canonical destination"
            )
            assert link.evaluate("node => node.tabIndex") >= 0, (
                f"{route}: sidebar link {name!r} is not keyboard-focusable"
            )

        # Native anchor focus plus Tab checks actual keyboard order without
        # relying on visual screenshots or claiming broader accessibility.
        for index in range(count - 1):
            links.nth(index).focus()
            page.keyboard.press("Tab")
            assert links.nth(index + 1).evaluate(
                "node => document.activeElement === node"
            ), f"{route}: Tab skips sidebar link {index + 1}"
