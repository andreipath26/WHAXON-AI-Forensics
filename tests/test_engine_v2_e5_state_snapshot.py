"""E5 cold state recovery includes evidence/config and rejects tampering."""
import sqlite3
from pathlib import Path

import pytest

from whaxon.core import Core
from whaxon.core.state_snapshot import (
    create_offline_snapshot,
    restore_offline_snapshot,
    verify_offline_snapshot,
)
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _make_state(root: Path):
    core = Core(root)
    core.create_mission("cold-restore", "restoration test")
    core.save_workflow_plan(
        "cold-plan",
        WorkflowPlan("cold-restore", (
            WorkflowTask("task", "unsupported.fixture", "192.0.2.10"),
        )),
    )
    request = core.enqueue_workflow_run("cold-plan")
    (root / "scope.json").write_text('{"enabled":false,"in_scope":[]}', encoding="utf-8")
    evidence = root / "evidence" / "proof.bin"
    evidence.parent.mkdir()
    evidence.write_bytes(b"controlled-e5-evidence\x00\xff")
    return request


def test_e5_offline_snapshot_restores_queue_scope_and_evidence(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    request = _make_state(original)
    backup = tmp_path / "snapshot"
    report = create_offline_snapshot(original, backup)
    assert report["files_verified"] is True
    assert report["external_anchor_verified"] is False
    assert (backup / "scope.json").read_bytes() == (original / "scope.json").read_bytes()
    assert (backup / "evidence" / "proof.bin").read_bytes() == (
        original / "evidence" / "proof.bin"
    ).read_bytes()
    restored_dir = tmp_path / "restored"
    assert restore_offline_snapshot(backup, restored_dir)["files_verified"]
    restored = Core(restored_dir)
    assert restored.workflow_run_request(request["id"])["status"] == "queued"
    assert restored.store.verify_workflow_plan_integrity("cold-plan")["digest"] == (
        request["plan_digest"]
    )
    assert (restored_dir / "scope.json").read_bytes() == (original / "scope.json").read_bytes()
    assert (restored_dir / "evidence" / "proof.bin").read_bytes() == b"controlled-e5-evidence\x00\xff"


def test_e5_snapshot_integrity_rejects_changed_evidence_and_refuses_restore(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    _make_state(original)
    backup = tmp_path / "snapshot"
    create_offline_snapshot(original, backup)
    (backup / "evidence" / "proof.bin").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_offline_snapshot(backup)
    with pytest.raises(ValueError, match="checksum mismatch"):
        restore_offline_snapshot(backup, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_e5_snapshot_rejects_symlink_and_never_overwrites_state(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    _make_state(original)
    outside = tmp_path / "outside-secret"
    outside.write_text("secret", encoding="utf-8")
    (original / "external").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        create_offline_snapshot(original, tmp_path / "snapshot")
    (original / "external").unlink()
    create_offline_snapshot(original, tmp_path / "snapshot")
    with pytest.raises(ValueError, match="destination must be new"):
        create_offline_snapshot(original, tmp_path / "snapshot")
    with pytest.raises(ValueError, match="restore destination must be new"):
        restore_offline_snapshot(tmp_path / "snapshot", original)


def test_e5_snapshot_refuses_destination_hidden_under_symlink_parent(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    _make_state(original)
    (tmp_path / "alias").symlink_to(original, target_is_directory=True)
    with pytest.raises(ValueError, match="outside source state"):
        create_offline_snapshot(original, tmp_path / "alias" / "hidden-backup")
    assert not (original / "hidden-backup").exists()


def test_e5_snapshot_rejects_broken_database(tmp_path):
    root = tmp_path / "invalid"
    root.mkdir()
    (root / "whaxon.db").write_bytes(b"not a sqlite database")
    with pytest.raises(sqlite3.DatabaseError):
        create_offline_snapshot(root, tmp_path / "snapshot")
    assert not (tmp_path / "snapshot").exists()
