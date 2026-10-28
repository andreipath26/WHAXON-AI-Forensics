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
