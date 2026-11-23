"""Atomic legacy human-review writes and Engine V2 ownership fencing."""
from __future__ import annotations

import threading
import time

from whaxon.core.store import JobStore


def _store_with_finding(path):
    store = JobStore(path)
    store.create("job")
    store.append_finding("job", {
        "kind": "sqli",
        "severity": "high",
        "source": "legacy",
        "data": {"parameter": "id"},
        "raw_line": "candidate finding",
    }, 0)
    return store


def test_legacy_verification_update_reports_typed_outcomes(tmp_path):
    store = _store_with_finding(tmp_path / "state.db")

    assert store.update_legacy_verification_if_unowned(
        "job", 0, "verified", by="human:reviewer", reason="reviewed",
    ) == "updated"
    finding = store.get_findings("job")[0]
    assert finding["verification_status"] == "verified"
    assert finding["verified_by"] == "human:reviewer"
    assert finding["verification_reason"] == "reviewed"

    assert store.update_legacy_verification_if_unowned(
        "missing-job", 0, "verified",
    ) == "not_found"
    assert store.update_legacy_verification_if_unowned(
        "job", 9, "verified",
    ) == "not_found"


def test_legacy_verification_rechecks_ownership_after_stale_preflight(tmp_path):
    store = _store_with_finding(tmp_path / "state.db")
    assert store.is_engine_v2_execution_job("job") is False
    before = store.get_findings("job")

    # Deterministically interleave the old route's false ownership preflight
    # with V2's durable ownership commit before the legacy update is attempted.
    store.mark_engine_v2_execution_job("job")
    result = store.update_legacy_verification_if_unowned(
        "job", 0, "verified", by="human:reviewer", reason="reviewed",
    )

    assert result == "v2_owned"
    assert store.get_findings("job") == before


def test_v2_marker_commit_precedes_waiting_legacy_resolution_transaction(tmp_path):
    store = _store_with_finding(tmp_path / "state.db")
    blocker = store._conn()
    blocker.execute("BEGIN IMMEDIATE")
    marker_written = threading.Event()
    outcome = []
    errors = []

    original_connect = store._conn

    def observed_connect():
        connection = original_connect()
        if threading.current_thread().name == "legacy-resolution":
            marker_written.set()
        return connection

    store._conn = observed_connect

    def resolve():
        try:
            outcome.append(store.update_legacy_verification_if_unowned(
                "job", 0, "verified", by="human:reviewer", reason="reviewed",
            ))
        except Exception as exc:
            errors.append(exc)

    resolver = threading.Thread(target=resolve, name="legacy-resolution")
    resolver.start()
    try:
        assert marker_written.wait(timeout=5)
        blocker.execute(
            "INSERT INTO engine_v2_execution_jobs (job_id, marked_at) VALUES (?, ?)",
            ("job", time.time()),
        )
        blocker.commit()
    finally:
        if blocker.in_transaction:
            blocker.rollback()
        blocker.close()
    resolver.join(timeout=5)

    assert not resolver.is_alive()
    assert errors == []
    assert outcome == ["v2_owned"]
    finding = store.get_findings("job")[0]
    assert finding["verification_status"] == "candidate"
    assert finding["verified_by"] == "engine"


