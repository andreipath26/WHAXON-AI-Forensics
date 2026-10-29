"""Browser coverage for the truthful execution ledger page."""
from __future__ import annotations


def test_audit_page_loads_recorded_execution_metadata(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/audit")
    assert response is not None and response.status == 200
    page.wait_for_function("() => !document.querySelector('#audit-status')?.textContent.includes('Loading recorded')")
    assert page.locator("#whaxon-live-audit").is_visible()
    assert "does not claim cryptographic signing" in page.locator("#whaxon-live-audit").inner_text()


def test_dashboard_links_to_audit_page(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="cryptographic-audit-log"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/audit"

def test_audit_page_never_claims_fixture_signatures_or_merkle_attestation(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/audit")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#audit-status')?.textContent.includes('execution record(s)') "
        "|| document.querySelector('#audit-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "EVT-9941",
        "EVT-9940",
        "DUAL_SIGNED_BRAV",
        "Merkle Root 100% Attested",
        "BEGIN ED25519 ATTESTATION SIGNATURE",
        "Court-Ready Forensic Bundle",
        "SHA-256 CHECKSUM MATCHED",
        "Cryptographic QR Verification Slip",
    ):
        assert marker not in visible, f"Fabricated audit claim must not be shown: {marker}"
    assert page.locator("#whaxon-live-audit").is_visible()
    assert "does not claim cryptographic signing" in page.locator("#whaxon-live-audit").inner_text()

