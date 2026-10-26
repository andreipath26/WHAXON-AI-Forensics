"""Browser smoke tests for the canonical roadmap UI served at /ui."""
from __future__ import annotations

import pytest


UI_ROUTES = [
    "/ui",
    "/ui/scope-and-targets",
    "/ui/run-and-orchestration",
    "/ui/trust-layer-and-findings",
    "/ui/trust-layer-approvals-queue-modal",
    "/ui/ptes-coverage-and-reports",
    "/ui/bas-and-detection-validation",
    "/ui/compliance-and-framework-crosswalk",
    "/ui/threat-intel-and-exploit-arsenal",
    "/ui/ai-strategy-gate",
    "/ui/remediation-retest-studio",
    "/ui/attack-surface-and-continuous-monitoring",
    "/ui/correlated-attack-chains",
    "/ui/bug-bounty-and-live-browser-studio",
    "/ui/ptaas-client-portal",
    "/ui/job-execution-history",
    "/ui/evidence-file-inspector",
    "/ui/cryptographic-audit-log",
    "/ui/system-diagnostics-and-health",
    "/ui/adapter-and-plugin-manager",
    "/ui/settings-and-api-explorer",
]


@pytest.mark.parametrize("route", UI_ROUTES)
def test_canonical_ui_route_loads_without_uncaught_page_errors(page, live_server, route):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    response = page.goto(f"{live_server}{route}", wait_until="domcontentloaded")
    assert response is not None and response.status == 200, route
    assert "WHAXON" in page.locator("body").inner_text(), route
    page.wait_for_timeout(250)
    assert errors == [], f"{route} raised browser errors: {errors}"


def test_legacy_ui_is_still_reachable(page, live_server):
    response = page.goto(f"{live_server}/legacy-ui", wait_until="domcontentloaded")
    assert response is not None and response.status == 200
    assert page.locator(".sb-brand .label-text").inner_text() == "WHAXON"
