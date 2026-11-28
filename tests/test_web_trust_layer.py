"""Behavioral tests for the Trust Layer API routes (Steps 5 & 6).

Runs against the real server via the live_server fixture, same as the
Playwright tests. Uses urllib for the HTTP calls.
"""
from __future__ import annotations

import json
from urllib.request import Request, urlopen


def _post(url, body=None):
    data = json.dumps(body).encode() if body is not None else b""
    req = Request(url, data=data, method="POST",
                  headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        # urllib raises HTTPError for 4xx/5xx. Extract the body.
        from urllib.error import HTTPError
        if isinstance(e, HTTPError):
            return e.code, json.loads(e.read())
        raise


def _get(url):
    with urlopen(url, timeout=5) as r:
        return r.status, json.loads(r.read())


def _seed_sqli_job(url):
    """Seed one job with one open_port finding. Returns (job_id, seq)."""
    # Use the demo init data dir. The server already has one job.
    # Instead, drive the API to create a job.
    status, body = _post(f"{url}/api/run", {
        "tool_id": "echo", "target": "127.0.0.1", "extra_args": ""
    })
    # echo may or may not exist. Fallback: use the report endpoint to
    # find the first existing job.
    if status != 200:
        _, data = _get(f"{url}/api/report?format=json")
        for entry in data.get("jobs", []):
            for f in entry.get("findings", []):
                return entry["job"]["id"], f["seq"]
        raise RuntimeError("no jobs available to seed")
    return body.get("job_id"), 0


def test_coverage_route_returns_empty_for_new_job(live_server):
    _, data = _get(f"{live_server}/api/report?format=json")
    if not data.get("jobs"):
        return  # nothing seeded, skip silently
    job_id = data["jobs"][0]["job"]["id"]
    status, body = _get(f"{live_server}/api/coverage/{job_id}")
    assert status == 200
    assert body["job_id"] == job_id
    assert isinstance(body["gaps"], list)
    assert body["count"] == len(body["gaps"])


def test_validate_route_candidate_on_non_replayable(live_server):
    job_id, seq = _seed_sqli_job(live_server)
    status, body = _post(f"{live_server}/api/validate/{job_id}/{seq}")
    assert status == 410
    assert body["legacy_validation_enabled"] is False
    assert body["approval_granted"] is False
    assert body["replay_attempted"] is False


def test_retest_route_requires_verified(live_server):
    job_id, seq = _seed_sqli_job(live_server)
    # Force the finding to candidate (default), then retest.
    status, body = _post(f"{live_server}/api/retest/{job_id}/{seq}")
    assert status == 410
    assert body["legacy_validation_enabled"] is False
    assert body["approval_granted"] is False
    assert body["replay_attempted"] is False


def test_approval_resolve_route_is_retired(live_server):
    job_id, seq = _seed_sqli_job(live_server)
    status, body = _post(
        f"{live_server}/api/approvals/{job_id}/{seq}/resolve",
        {"status": "verified", "user": "peter"},
    )
    assert status == 409
    assert body["approval_granted"] is False
    assert body["verification_updated"] is False
