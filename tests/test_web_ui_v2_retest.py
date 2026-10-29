"""Browser coverage for the canonical live remediation retest page."""
from __future__ import annotations


def test_retest_page_loads_current_findings(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/retest")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#retest-status')?.textContent.includes('Loading recorded')",
        timeout=5000,
    )
    assert page.locator("#whaxon-live-retest").is_visible()
    assert page.locator("#retest-list").is_visible()


def test_dashboard_links_to_retest_page(page, live_server):
    page.goto(f"{live_server}/ui-v2")
    link = page.locator('a[data-path="remediation-retest-studio"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/retest"

def test_retest_page_never_displays_static_fixture_evidence_or_commands(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/retest")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('finding record(s)') "
        "|| document.querySelector('#retest-status')?.textContent.includes('could not be loaded')",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "staging-api.corp.net",
        "pg_sleep(5)",
        "K9#xL9!pQ_corp_secret",
        "AKIAIOSFODNN7EXAMPLE",
        "5,009ms",
        "COMMIT 3-WAY VERDICT TO AUDIT LEDGER",
        "RE-EXECUTE IMMEDIATE PROBE",
    ):
        assert marker not in visible, f"Fictional retest fixture must not be shown: {marker}"
    assert page.locator("#whaxon-live-retest").is_visible()


def test_retest_page_only_posts_for_verified_findings_with_valid_sequence(page, live_server):
    calls = []
    report_calls = {"count": 0}

    def report(route):
        report_calls["count"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs":[{"job_id":"job-live-1","findings":['
                 '{"seq":7,"kind":"verified finding","severity":"low","verification_status":"verified"},'
                 '{"seq":8,"kind":"unverified finding","severity":"high","verification_status":"pending"},'
                 '{"seq":null,"kind":"missing sequence","verification_status":"verified"}]}]}',
        )

    def retest(route):
        calls.append({"method": route.request.method, "url": route.request.url})
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"INCONCLUSIVE","reason":"test replay completed without a decisive signal"}',
        )

    page.route("**/api/report?format=json", report)
    page.route("**/api/retest/**", retest)
    page.goto(f"{live_server}/ui-v2/retest")
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('2 finding record(s)')",
        timeout=8000,
    )

    verified = page.get_by_role("button", name="Retest verified finding").nth(0)
    unverified = page.get_by_role("button", name="Retest verified finding").nth(1)
    assert verified.is_enabled()
    assert unverified.is_disabled()
    assert page.get_by_role("button", name="Retest verified finding").count() == 2

    verified.click()
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('Retest result: INCONCLUSIVE')",
        timeout=8000,
    )
    assert calls == [{
        "method": "POST",
        "url": f"{live_server}/api/retest/job-live-1/7",
    }]
