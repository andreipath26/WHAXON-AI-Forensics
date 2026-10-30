from __future__ import annotations

import threading

import pytest

from whaxon.core import dependency_jobs


def test_install_job_rejects_stale_plan_before_queueing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        dependency_jobs,
        "load_dependency_manifest",
        lambda: {
            "dependencies": [{"id": "sample", "kind": "python-package"}],
            "policy": {
                "automatic_installation_enabled": True,
                "automatic_installation_kinds": ["python-package"],
            },
        },
    )
    monkeypatch.setattr(
        dependency_jobs,
        "build_remediation_plan",
        lambda **kwargs: {"plan_id": "plan-current", "actions": [], "unknown_dependency_ids": []},
    )
    monkeypatch.setattr(dependency_jobs.sys, "prefix", "/tmp/whaxon-test-venv")
    monkeypatch.setattr(dependency_jobs.sys, "base_prefix", "/usr")
    with pytest.raises(ValueError, match="approval does not match"):
        dependency_jobs.start_install_operation("sample", "plan-stale", tmp_path)
    assert list((tmp_path / ".whaxon" / "dependency-operations").glob("*.json")) == []


def test_install_job_lifecycle_persists_progress_and_result(tmp_path, monkeypatch):
    monkeypatch.setattr(
        dependency_jobs,
        "load_dependency_manifest",
        lambda: {
            "dependencies": [{"id": "sample", "kind": "python-package"}],
            "policy": {
                "automatic_installation_enabled": True,
                "automatic_installation_kinds": ["python-package"],
            },
        },
    )
    monkeypatch.setattr(
        dependency_jobs,
        "build_remediation_plan",
        lambda **kwargs: {
            "plan_id": "plan-0123456789abcdef",
            "actions": [{
                "dependency_id": "sample",
                "options": [{
                    "kind": "python-package",
                    "automated_execution_supported": True,
                }],
            }],
        },
    )
    monkeypatch.setattr(dependency_jobs.sys, "prefix", "/tmp/whaxon-test-venv")
    monkeypatch.setattr(dependency_jobs.sys, "base_prefix", "/usr")
    finished = threading.Event()

    def fake_install(dependency_id, plan_id, **kwargs):
        kwargs["progress_callback"]("VERIFYING", "Verifying package.")
        finished.set()
        return {
            "status": "VERIFIED",
            "verification": "Import and version verified.",
            "operation_id": "from-installer",
        }

    monkeypatch.setattr(dependency_jobs, "apply_approved_dependency_plan", fake_install)
    queued = dependency_jobs.start_install_operation(
        "sample", "plan-0123456789abcdef", tmp_path
    )
    assert queued["status"] == "QUEUED"
    assert finished.wait(timeout=3)
    operation = dependency_jobs.get_install_operation(
        tmp_path, queued["operation_id"]
    )
    assert operation["status"] == "VERIFIED"
    assert operation["progress"] == 100
    assert operation["result"]["status"] == "VERIFIED"


def test_cancel_marks_active_operation(tmp_path):
    operations = dependency_jobs._operations_dir(tmp_path)
    operation_id = "0123456789abcdef0123456789abcdef"
    state_path = operations / f"{operation_id}.json"
    dependency_jobs._write_state(state_path, {
        "schema_version": 1,
        "operation_id": operation_id,
        "status": "INSTALLING",
        "updated_at": dependency_jobs._now(),
    })
    result = dependency_jobs.cancel_install_operation(tmp_path, operation_id)
    assert result["cancel_requested"] is True
    assert (operations / f"{operation_id}.cancel").exists()


def test_operation_id_is_validated(tmp_path):
    with pytest.raises(ValueError, match="invalid dependency operation ID"):
        dependency_jobs.get_install_operation(tmp_path, "../escape")


def test_stale_operation_is_marked_interrupted(tmp_path):
    operations = dependency_jobs._operations_dir(tmp_path)
    operation_id = "abcdef0123456789abcdef0123456789"
    state_path = operations / f"{operation_id}.json"
    dependency_jobs._write_state(state_path, {
        "schema_version": 1,
        "operation_id": operation_id,
        "status": "INSTALLING",
        "updated_at": "2020-01-01T00:00:00+00:00",
    })
    operation = dependency_jobs.get_install_operation(tmp_path, operation_id)
    assert operation["status"] == "INTERRUPTED"


def test_queue_rejects_disabled_install_policy_before_locking(tmp_path, monkeypatch):
    monkeypatch.setattr(
        dependency_jobs,
        "load_dependency_manifest",
        lambda: {
            "dependencies": [{"id": "sample", "kind": "python-package"}],
            "policy": {
                "automatic_installation_enabled": False,
                "automatic_installation_kinds": [],
            },
        },
    )
    with pytest.raises(ValueError, match="disabled by the dependency policy"):
        dependency_jobs.start_install_operation("sample", "plan-0123456789abcdef", tmp_path)
    operations = dependency_jobs._operations_dir(tmp_path)
    assert list(operations.iterdir()) == []


def test_queue_requires_virtual_environment_before_locking(tmp_path, monkeypatch):
    monkeypatch.setattr(
        dependency_jobs,
        "load_dependency_manifest",
        lambda: {
            "dependencies": [{"id": "sample", "kind": "python-package"}],
            "policy": {
                "automatic_installation_enabled": True,
                "automatic_installation_kinds": ["python-package"],
            },
        },
    )
    monkeypatch.setattr(dependency_jobs.sys, "prefix", "/usr")
    monkeypatch.setattr(dependency_jobs.sys, "base_prefix", "/usr")
    with pytest.raises(ValueError, match="active virtual environment"):
        dependency_jobs.start_install_operation("sample", "plan-0123456789abcdef", tmp_path)
    operations = dependency_jobs._operations_dir(tmp_path)
    assert list(operations.iterdir()) == []


def test_operation_rejects_malformed_json_shape(tmp_path):
    operations = dependency_jobs._operations_dir(tmp_path)
    operation_id = "fedcba9876543210fedcba9876543210"
    (operations / f"{operation_id}.json").write_text("[]")
    with pytest.raises(RuntimeError, match="malformed"):
        dependency_jobs.get_install_operation(tmp_path, operation_id)


def test_operation_state_rejects_non_object_json(tmp_path):
    operations = dependency_jobs._operations_dir(tmp_path)
    operation_id = "0123456789abcdef0123456789abcdef"
    (operations / f"{operation_id}.json").write_text("[]")
    with pytest.raises(RuntimeError, match="malformed"):
        dependency_jobs.get_install_operation(tmp_path, operation_id)
