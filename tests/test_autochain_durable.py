"""The auto-chain survives process exit (regression for the stuck job).

Old bug: nmap's chain spawned a daemon-thread nikto job; the CLI exited;
the thread died; the job row stayed 'running' forever. Now the chain
writes a pending row, and `whaxon jobs drain` runs it from a new process.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _whaxon(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "whaxon.cli", *args],
        cwd=str(REPO), capture_output=True, text=True, timeout=60,
    )


def _db(tmp: Path) -> Path:
    return tmp / "whaxon.db"


def test_legacy_queue_drain_is_retired_even_with_explicit_opt_in(
    tmp_path: Path, monkeypatch,
) -> None:
    from whaxon.core.store import JobStore

    monkeypatch.setenv("WHAXON_LEGACY_QUEUE_DRAIN_ENABLED", "true")
    data = tmp_path / "data"
    data.mkdir()
    (data / "tools.json").write_text((REPO / "src" / "whaxon" / "data" / "tools.json").read_text())
    (data / "scope.json").write_text(json.dumps({
        "engagement": "test", "enabled": True,
        "in_scope": ["127.0.0.1"], "out_of_scope": [],
    }))

    store = JobStore(_db(data))
    store.create_pending("legacy-pending", "echo", "127.0.0.1")
    del store

    result = _whaxon("jobs", "drain", "--data", str(data))

    assert result.returncode == 2
    assert "legacy queue drain is retired" in result.stderr
    reopened = JobStore(_db(data))
    assert reopened.get("legacy-pending")["status"] == "pending"


def test_reconcile_on_init_marks_old_running_failed(tmp_path: Path) -> None:
    from whaxon.core.store import JobStore
    data = tmp_path / "data"
    data.mkdir()
    (data / "tools.json").write_text((REPO / "src" / "whaxon" / "data" / "tools.json").read_text())
    (data / "scope.json").write_text(json.dumps({
        "engagement": "test", "enabled": True,
        "in_scope": ["127.0.0.1"], "out_of_scope": [],
    }))
    store = JobStore(_db(data))
    store.create_pending("zombie", "nikto", "127.0.0.1:80")
    store.claim_pending()  # now running
    import time
    c = sqlite3.connect(_db(data))
    c.execute("UPDATE jobs SET started_at=?, heartbeat_at=NULL WHERE id='zombie'", (time.time() - 3600,))
    c.commit(); c.close()
    del store

    # Any interface that calls initialize reconciles. Use jobs drain,
    # which builds a Core and drains — but reconcile happens in initialize,
    # which jobs drain does not call. So test the store method directly here.
    s2 = JobStore(_db(data))
    assert s2.reconcile_stale(older_than_s=60) == 1
    assert s2.get("zombie")["status"] == "failed"
