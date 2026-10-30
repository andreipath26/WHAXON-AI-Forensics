"""Security and provenance tests for §26.12 program ingestion."""
from __future__ import annotations

import socket

import pytest

from whaxon.core import bounty_ingest


def test_only_https_yeswehack_program_urls_are_accepted():
    for url in (
        "http://yeswehack.com/programs/example",
        "https://evil.example/programs/example",
        "https://yeswehack.com.evil.example/programs/example",
        "https://user:pass@yeswehack.com/programs/example",
        "https://yeswehack.com:8443/programs/example",
        "https://yeswehack.com/",
        "https://yeswehack.com/programs/example#fragment",
    ):
        with pytest.raises(bounty_ingest.IngestionError):
            bounty_ingest._validated_url(url)


def test_url_path_requires_a_single_program_slug():
    bounty_ingest._validated_url("https://yeswehack.com/programs/example-1")
    with pytest.raises(bounty_ingest.IngestionError):
        bounty_ingest._validated_url("https://yeswehack.com/programs/a/../b")


def test_non_public_dns_resolution_is_rejected(monkeypatch):
    def private_dns(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]
    monkeypatch.setattr(socket, "getaddrinfo", private_dns)
    with pytest.raises(bounty_ingest.IngestionError, match="non-public"):
        bounty_ingest._public_ip("yeswehack.com")


def test_all_dns_answers_must_be_public(monkeypatch):
    def mixed_dns(*args, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.5", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ]
    monkeypatch.setattr(socket, "getaddrinfo", mixed_dns)
    with pytest.raises(bounty_ingest.IngestionError, match="non-public"):
        bounty_ingest._public_ip("yeswehack.com")


def test_pasted_text_returns_draft_with_provenance_and_no_activation(monkeypatch):
    page = """Public programs
Example Program
https://app.example.org
Web application
High
"""
    result = bounty_ingest.ingest_yeswehack_text(page)
    assert result["status"] == "draft_requires_review"
    assert result["source"]["content_sha256"]
    assert result["source"]["parser_version"] == bounty_ingest.PARSER_VERSION
    assert result["policy_draft"]["slug"] == "example-program"
    assert any("not proof of authorization" in item for item in result["warnings"])
    assert "saved" in result["warnings"][-1]


def test_pasted_text_size_limit_is_enforced():
    with pytest.raises(bounty_ingest.IngestionError, match="2 MiB"):
        bounty_ingest.ingest_yeswehack_text("x" * (2 * 1024 * 1024 + 1))


def test_html_extractor_ignores_script_and_style_content():
    parser = bounty_ingest._VisibleText()
    parser.feed("<h1>Program</h1><script>ignore me</script><p>In scope</p>")
    result = parser.text()
    assert "Program" in result
    assert "In scope" in result
    assert "ignore me" not in result
