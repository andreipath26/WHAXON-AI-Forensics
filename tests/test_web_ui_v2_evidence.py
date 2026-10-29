"""Browser coverage for the canonical evidence inspector."""
from __future__ import annotations


def test_evidence_inspector_loads_recorded_jobs(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/evidence")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => !document.querySelector('#evidence-job')?.textContent.includes('Loading recorded jobs')",
        timeout=5000,
    )
    assert page.locator("#whaxon-live-evidence").is_visible()
    assert page.locator("#evidence-refresh").is_visible()
    assert page.locator("#evidence-status").inner_text()


def test_dashboard_links_to_evidence_inspector(page, live_server):
    response = page.goto(f"{live_server}/ui-v2")
    assert response is not None and response.status == 200
    link = page.locator('a[data-path="evidence-file-inspector"]')
    assert link.is_visible()
    assert link.get_attribute("href") == "/ui-v2/evidence"

def test_evidence_inspector_does_not_show_fixture_scan_output_as_live_evidence(page, live_server):
    response = page.goto(f"{live_server}/ui-v2/evidence")
    assert response is not None and response.status == 200
    page.wait_for_function(
        "() => document.querySelector('#evidence-status')?.textContent !== 'Evidence is loaded only from WHAXON records.'",
        timeout=8000,
    )
    visible = page.locator("body").inner_text()
    for marker in (
        "staging-api.corp.net",
        "Apache Envoy 1.18.0",
        "SHA-256 CHECKSUM MATCHED",
        "LOCAL REPLAY CACHE INTACT",
        "Merkle Leaf #4",
        "0x8891...E25519",
        "Direct Finding Ingestion Preview",
    ):
        assert marker not in visible, f"Fictional evidence fixture must not be shown: {marker}"
    assert page.locator("#whaxon-live-evidence").is_visible()

def test_evidence_inspector_saves_notes_and_uploads_files(page, live_server):
    calls = []

    def history(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"id":"job-ui","tool":"echo","target":"127.0.0.1"}]',
        )

    def evidence(route):
        if route.request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body="[]")
            return
        if route.request.method == "POST":
            calls.append({
                "method": "POST",
                "content_type": route.request.headers.get("content-type", ""),
                "body": route.request.post_data or (route.request.post_data_buffer or b"").decode("latin-1", errors="replace"),
            })
            route.fulfill(
                status=201,
                content_type="application/json",
                body='{"seq":4,"name":"proof.txt"}',
            )
            return
        route.continue_()

    page.route("**/api/history", history)
    page.route("**/api/jobs/job-ui/evidence", evidence)
    page.goto(f"{live_server}/ui-v2/evidence")
    page.wait_for_function(
        "() => document.querySelector('#evidence-job')?.value === 'job-ui'",
        timeout=8000,
    )

    page.get_by_label("Evidence note title").fill("Reproduction notes")
    page.get_by_label("Evidence note", exact=True).fill("Observed response reproduced from the recorded request.")
    page.get_by_role("button", name="Save note").click()
    page.wait_for_function("() => document.querySelector('#evidence-status')?.textContent.includes('Evidence note saved')", timeout=8000)
    assert calls and '"kind":"note"' in calls[0]["body"]
    assert "Observed response reproduced" in calls[0]["body"]

    page.locator("#evidence-file").set_input_files({
        "name": "proof.txt",
        "mimeType": "text/plain",
        "buffer": b"recorded proof",
    })
    page.get_by_role("button", name="Upload file").click()
    page.wait_for_function("() => document.querySelector('#evidence-status')?.textContent.includes('Evidence file uploaded')", timeout=8000)
    assert len(calls) == 2
    assert "multipart/form-data" in calls[1]["content_type"]
    assert "proof.txt" in calls[1]["body"]

def test_evidence_layout_remains_available_beside_live_inspector(page, live_server):
    page.goto(f"{live_server}/ui-v2/evidence")
    assert page.locator("#whaxon-live-evidence").is_visible()
    assert page.get_by_text("RECORDED EVIDENCE INSPECTOR", exact=True).is_visible()
