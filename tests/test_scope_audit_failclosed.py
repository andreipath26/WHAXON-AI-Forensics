from __future__ import annotations

import json

import pytest

from whaxon.core import override_log
from whaxon.core.scope import ScopeManager


def test_scope_save_refuses_policy_change_when_audit_write_fails(tmp_path, monkeypatch):
    path = tmp_path / "scope.json"
    initial = {
        "engagement": "audit failure regression",
        "enabled": True,
        "in_scope": ["127.0.0.1"],
        "out_of_scope": [],
        "notes": "",
    }
    path.write_text(json.dumps(initial), encoding="utf-8")
    scope = ScopeManager(path)
    original_bytes = path.read_bytes()

    monkeypatch.setattr(override_log, "log_override", lambda *args, **kwargs: False)

    with pytest.raises(RuntimeError, match="audit record could not be written"):
        scope.save({**initial, "enabled": False})

    assert path.read_bytes() == original_bytes
    assert scope.enabled is True
    assert scope.check("8.8.8.8").allowed is False


def test_scope_save_does_not_swallow_audit_writer_exception(tmp_path, monkeypatch):
    path = tmp_path / "scope.json"
    initial = {
        "engagement": "audit exception regression",
        "enabled": True,
        "in_scope": ["127.0.0.1"],
        "out_of_scope": [],
        "notes": "",
    }
    path.write_text(json.dumps(initial), encoding="utf-8")
    scope = ScopeManager(path)
    original_bytes = path.read_bytes()

    def fail_audit(*args, **kwargs):
        raise OSError("audit storage unavailable")

    monkeypatch.setattr(override_log, "log_override", fail_audit)

    with pytest.raises(OSError, match="audit storage unavailable"):
        scope.save({**initial, "enabled": False})

    assert path.read_bytes() == original_bytes
    assert scope.enabled is True
    assert scope.check("8.8.8.8").allowed is False
