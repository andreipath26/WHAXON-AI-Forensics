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

def test_retest_header_reflects_live_scope_and_routes_to_scope_and_run(page, live_server):
    page.goto(f"{live_server}/ui-v2/retest")
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('finding record(s)')"
        " || document.querySelector('#retest-status')?.textContent.includes('Findings could not be loaded')",
        timeout=8000,
    )
    page.wait_for_function(
        "() => !document.querySelector('header')?.innerText.includes('api.internal.corp')",
        timeout=8000,
    )
    scope = page.evaluate("() => fetch('/api/scope').then(response => response.json())")
    target = scope["in_scope"][0] if scope.get("in_scope") else "No target configured"
    header = page.locator("header").inner_text()
    assert target in header
    assert "SCOPE CONFIGURATION LOADED" in header or "SCOPE ENFORCEMENT DISABLED" in header

    page.locator("header button").filter(has_text="New").click()
    page.wait_for_url("**/ui-v2/scope")
    assert page.url.endswith("/ui-v2/scope")

    page.goto(f"{live_server}/ui-v2/retest")
    page.locator("header button").filter(has_text="Terminal Log").click()
    page.wait_for_url("**/ui-v2/run")
    assert page.url.endswith("/ui-v2/run")


def test_retest_halt_uses_live_history_and_fixture_controls_are_disabled(page, live_server):
    page.route(
        "**/api/history",
        lambda route: route.fulfill(status=200, content_type="application/json", body="[]"),
    )
    page.goto(f"{live_server}/ui-v2/retest")
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('finding record(s)')"
        " || document.querySelector('#retest-status')?.textContent.includes('Findings could not be loaded')",
        timeout=8000,
    )
    page.locator("header button").filter(has_text="Emergency Halt Scan").click()
    page.wait_for_function(
        "() => document.querySelector('#retest-status')?.textContent.includes('No running or queued jobs were found')",
        timeout=5000,
    )
    for button in page.locator("main button:visible").all():
        if button.evaluate("(el) => el.closest('#whaxon-live-retest') !== null"):
            continue
        assert button.is_disabled(), f"Disconnected retest control remains enabled: {button.inner_text()}"
    assert "server must re-check scope" in page.locator("#whaxon-live-retest").inner_text()

