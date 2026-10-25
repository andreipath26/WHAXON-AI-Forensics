from pathlib import Path

from whaxon.core.findings import Finding
from whaxon.core.validator import Validator


def _finding(*, data=None, request_context=None):
    return Finding(
        kind="sqli",
        severity="high",
        source="test",
        data=data or {},
        request_context=request_context or {},
    )


def test_validator_uses_canonical_finding_request_context(tmp_path, monkeypatch):
    context = {"url": "https://example.test/search?q=original", "method": "GET"}
    finding = _finding(request_context=context)
    validator = Validator(Path(tmp_path))

    def replay(received_context, target_url=None, kind=None):
        assert received_context is context
        assert target_url == "https://example.test"
        assert kind == "sqli"
        return "verified", "mocked replay"

    monkeypatch.setattr(validator, "_replay_ctx", replay)

    assert validator.validate(finding, target_url="https://example.test") == (
        "verified",
        "mocked replay",
    )


def test_validator_falls_back_to_legacy_data_request_context(tmp_path, monkeypatch):
    context = {"url": "https://example.test/search?q=original", "method": "GET"}
    finding = _finding(data={"_request_context": context})
    validator = Validator(Path(tmp_path))

    def replay(received_context, target_url=None, kind=None):
        assert received_context is context
        return "candidate", "legacy context"

    monkeypatch.setattr(validator, "_replay_ctx", replay)

    assert validator.validate(finding, target_url="https://example.test") == (
        "candidate",
        "legacy context",
    )


def test_canonical_context_takes_precedence_over_legacy_context(tmp_path, monkeypatch):
    canonical = {"url": "https://example.test/canonical", "method": "GET"}
    legacy = {"url": "https://example.test/legacy", "method": "GET"}
    finding = _finding(
        data={"_request_context": legacy},
        request_context=canonical,
    )
    validator = Validator(Path(tmp_path))

    def replay(received_context, target_url=None, kind=None):
        assert received_context is canonical
        return "candidate", "canonical context"

    monkeypatch.setattr(validator, "_replay_ctx", replay)

    assert validator.validate(finding, target_url="https://example.test") == (
        "candidate",
        "canonical context",
    )
