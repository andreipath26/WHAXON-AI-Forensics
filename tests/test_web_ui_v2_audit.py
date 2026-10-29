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

def test_audit_ledger_filters_live_records_and_refreshes(page, live_server):
    calls = {"count": 0}

    def history(route):
        calls["count"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='['
                 '{"id":"job-alpha","tool":"nmap","status":"finished","target":"192.0.2.10","exit_code":0,"duration_s":1.2},'
                 '{"id":"job-beta","tool":"nikto","status":"failed","target":"192.0.2.20","exit_code":2,"duration_s":2.4}'
                 ']',
        )

    page.route("**/api/history", history)
    page.goto(f"{live_server}/ui-v2/audit")
    page.wait_for_function(
        "() => document.querySelector('#audit-status')?.textContent.includes('2 execution record(s)')",
        timeout=8000,
    )
    assert page.locator(".audit-card").count() == 2
    page.get_by_label("Filter recorded jobs").fill("job-beta")
    assert page.locator(".audit-card:visible").count() == 1
    assert "job-beta" in page.locator(".audit-card:visible").inner_text()
    assert "job-alpha" not in page.locator(".audit-card:visible").inner_text()
    page.get_by_role("button", name="Refresh ledger").click()
    page.wait_for_function("() => document.querySelector('#audit-status')?.textContent.includes('1 of 2 execution record(s)')")
    assert calls["count"] >= 2
