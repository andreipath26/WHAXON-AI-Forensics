"""Browser coverage for canonical auxiliary WHAXON v2 pages."""
from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("path", "live_id"),
    [
        ("/ui-v2/bas", "whaxon-live-bas"),
        ("/ui-v2/bug-bounty", "whaxon-live-bug-bounty"),
        ("/ui-v2/compliance", "whaxon-live-compliance"),
        ("/ui-v2/ptaas", "whaxon-live-ptaas"),
        ("/ui-v2/threat-intel", "whaxon-live-threat-intel"),
        ("/ui-v2/approvals", "whaxon-live-approvals"),
    ],
)
def test_auxiliary_canonical_pages_render_live_panels(page, live_server, path, live_id):
    response = page.goto(f"{live_server}{path}")
    assert response is not None and response.status == 200
    assert page.locator(f"#{live_id}").count() == 1
    page.wait_for_function(
        "(id) => { const el = document.getElementById(id); return el && !el.textContent.includes('Fetching current backend state.'); }",
        arg=live_id,
        timeout=20000,
    )


def test_bug_bounty_hides_unimplemented_browser_actions(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/bug-bounty")
    assert response is not None and response.status == 200
    assert page.locator("#whaxon-live-bug-bounty").count() == 1
    for label in ("CLEAR CACHE", "DUMP DOM SNAPSHOT", "SEND TO VALIDATOR", "DIFF ANALYSIS", "PING SEC-OPS"):
        assert page.locator("button:visible").filter(has_text=label).count() == 0
    visible = page.locator("body").inner_text()
    assert "24 Ev/s" not in visible
    assert "api.staging.internal" not in visible


def test_ptaas_hides_unimplemented_client_actions(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/ptaas")
    assert response is not None and response.status == 200
    assert page.locator("#whaxon-live-ptaas").count() == 1
    for label in ("PING SEC-OPS", "REQUEST RETEST", "VIEW RAW PACKET", "VIEW SCRIPT"):
        assert page.locator("button:visible").filter(has_text=label).count() == 0
    visible = page.locator("body").inner_text()
    assert "BOLA / IDOR in Merchant Transfer Settlement Route" not in visible
    assert "REPRODUCIBLE EXPLOIT ARTIFACT" not in visible

def test_bas_validation_only_offers_actions_for_real_sequence_ids(page, live_server):
    calls = []

    def findings(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job":{"id":"job-bas"},"findings":['
                 '{"seq":3,"kind":"recorded finding","severity":"low","verification_status":"candidate"},'
                 '{"seq":null,"kind":"missing sequence","severity":"high","verification_status":"candidate"}]}]}',
        )

    def validate(route):
        calls.append(route.request.url)
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"candidate","reason":"no deterministic replay signal"}',
        )

    page.route("**/api/ui-v2/findings", findings)
    page.route("**/api/validate/**", validate)
    page.goto(f"{live_server}/ui-v2/bas")
    page.wait_for_function(
        "() => document.querySelector('#whaxon-live-bas-status')?.textContent.includes('2 persisted finding(s)') || document.body.innerText.includes('2 persisted finding(s)')",
        timeout=8000,
    )
    buttons = page.get_by_role("button", name="Validate recorded finding")
    assert buttons.count() == 1
    buttons.first.click()
    page.wait_for_function(
        "() => document.body.innerText.includes('Validation result: candidate')",
        timeout=8000,
    )
    assert calls == [f"{live_server}/api/validate/job-bas/3"]
