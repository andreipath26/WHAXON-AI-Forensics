"""Web API tests for safe bounty program import."""
from __future__ import annotations


_PROGRAM_TEXT = """Public programs
Example Program
Last update on 2026-10-29
https://app.example.org
Web application
High
Do not use automated scanners.
No vulnerability disclosure is allowed.
"""


def test_pasted_program_import_returns_reviewable_draft(page, live_server):
    response = page.request.post(
        f"{live_server}/api/bounty/import",
        data={"text": _PROGRAM_TEXT},
    )
    assert response.status == 200
    result = response.json()
    assert result["status"] == "draft_requires_review"
    assert result["policy_draft"]["program_url"] == ""
    assert result["policy_draft"]["scope"]["in_scope"]
    assert result["source"]["content_sha256"]
    assert result["evidence"]
    assert result["policy_draft"]["tools"]["allowlist"] == []
    assert result["policy_draft"]["ai_policy"]["allow_live_requests"] is False
    assert any("not proof of authorization" in warning for warning in result["warnings"])


def test_program_import_rejects_unsafe_url_without_fetching(page, live_server):
    response = page.request.post(
        f"{live_server}/api/bounty/import",
        data={"url": "http://127.0.0.1/programs/attack"},
    )
    assert response.status == 400
    assert "HTTPS" in response.json()["error"]


def test_program_import_requires_exactly_one_source(page, live_server):
    response = page.request.post(
        f"{live_server}/api/bounty/import",
        data={"url": "https://yeswehack.com/programs/example", "text": _PROGRAM_TEXT},
    )
    assert response.status == 400
    assert "either url or text" in response.json()["error"]
