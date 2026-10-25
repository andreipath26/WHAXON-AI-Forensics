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


def test_sqlmap_adapter_populates_canonical_request_context():
    from whaxon.adapters.sqlmap import SqlmapAdapter

    adapter = SqlmapAdapter()
    findings = adapter.parse(
        [
            ("stdout", "Parameter: id (GET)"),
            ("stdout", "    Type: boolean-based blind"),
            ("stdout", "    Title: AND boolean-based blind - WHERE or HAVING clause"),
            ("stdout", "    Payload: id=1 AND 1234=1234"),
        ],
        ctx={"target": "https://example.test/item?id=1"},
    )

    assert len(findings) == 1
    assert findings[0].request_context == {
        "method": "GET",
        "url": "https://example.test/item?id=1",
        "parameter": "id",
    }


def test_store_round_trips_canonical_request_context(tmp_path):
    from whaxon.core.store import JobStore

    context = {
        "url": "https://example.test/item?id=1",
        "method": "GET",
        "parameter": "id",
    }
    finding = _finding(request_context=context)
    store = JobStore(tmp_path / "whaxon.sqlite3")
    store.create("job-context")
    store.append_finding("job-context", finding, 0)

    saved = store.get_findings("job-context")
    assert saved is not None
    assert saved[0]["request_context"] == context


def test_cli_validate_restores_request_context(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from whaxon.interfaces.cli import validate_cmd

    context = {"url": "https://example.test/item?id=1", "method": "GET", "parameter": "id"}
    finding_row = {
        "seq": 0,
        "kind": "sqli",
        "severity": "high",
        "source": "sqlmap",
        "data": {"parameter": "id"},
        "raw_line": "SQL injection",
        "request_context": context,
    }
    store = SimpleNamespace(
        get_findings=lambda job_id: [finding_row],
        get=lambda job_id: {"target": "https://example.test"},
        update_verification=lambda *args, **kwargs: None,
        set_proof=lambda *args, **kwargs: None,
    )
    core = SimpleNamespace(
        initialize=_async_noop,
        store=store,
        scope=SimpleNamespace(check=lambda target: SimpleNamespace(allowed=True, reason="")),
    )
    monkeypatch.setattr(validate_cmd, "Core", lambda data_dir: core)
    seen = {}

    class FakeValidator:
        def __init__(self, payload_dir):
            pass

        def validate(self, finding, target_url=None):
            seen["context"] = finding.request_context
            return "candidate", "test"

    monkeypatch.setattr(validate_cmd, "Validator", FakeValidator)

    assert validate_cmd.main(["job-cli", "0", "--data", str(tmp_path)]) == validate_cmd.EXIT_OK
    assert seen["context"] == context


def test_cli_retest_restores_request_context(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from whaxon.interfaces.cli import retest_cmd

    context = {"url": "https://example.test/item?id=1", "method": "GET", "parameter": "id"}
    finding_row = {
        "seq": 0,
        "kind": "sqli",
        "severity": "high",
        "source": "sqlmap",
        "data": {"parameter": "id"},
        "raw_line": "SQL injection",
        "verification_status": "verified",
        "request_context": context,
    }
    store = SimpleNamespace(
        get_findings=lambda job_id: [finding_row],
        get=lambda job_id: {"target": "https://example.test"},
        update_verification=lambda *args, **kwargs: None,
    )
    core = SimpleNamespace(
        initialize=_async_noop,
        store=store,
        scope=SimpleNamespace(check=lambda target: SimpleNamespace(allowed=True, reason="")),
    )
    monkeypatch.setattr(retest_cmd, "Core", lambda data_dir: core)
    seen = {}

    class FakeValidator:
        def __init__(self, payload_dir):
            pass

        def revalidate(self, finding, target_url=None):
            seen["context"] = finding.request_context
            return "inconclusive", "test"

    monkeypatch.setattr(retest_cmd, "Validator", FakeValidator)

    assert retest_cmd.main(["job-cli", "0", "--data", str(tmp_path)]) == retest_cmd.EXIT_OK
    assert seen["context"] == context


async def _async_noop():
    return None
