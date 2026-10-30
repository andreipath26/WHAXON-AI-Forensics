from __future__ import annotations

import json
import sys
import subprocess

import pytest

from whaxon.core.installer import apply_approved_dependency_plan
from whaxon.core.remediation import build_remediation_plan


def test_install_requires_current_explicit_plan_approval():
    plan = build_remediation_plan(dependency_ids=["textual"])
    if not plan["actions"]:
        pytest.skip("Textual is already ready in this test environment")
    with pytest.raises(ValueError, match="Approval does not match"):
        apply_approved_dependency_plan("textual", "wrong-plan-id")


def test_install_refuses_external_tools():
    plan = build_remediation_plan(dependency_ids=["nmap"])
    if not plan["actions"]:
        pytest.skip("Nmap is already detected")
    with pytest.raises(ValueError, match="No supported automated installation"):
        apply_approved_dependency_plan("nmap", plan["plan_id"])


def test_audit_redaction():
    from whaxon.core.installer import _redact

    value = _redact("api_key=abc123 Bearer secretvalue")
    assert "abc123" not in value
    assert "secretvalue" not in value
    json.dumps({"output": value})


def test_install_refuses_non_virtual_environment(monkeypatch):
    from whaxon.core.installer import apply_approved_dependency_plan

    plan = build_remediation_plan()
    candidates = [action for action in plan["actions"]
                  if action["options"][0]["kind"] == "python-package"]
    if not candidates:
        pytest.skip("No missing Python package to install")
    dependency_id = candidates[0]["dependency_id"]
    focused = build_remediation_plan(dependency_ids=[dependency_id])
    monkeypatch.setattr(sys, "prefix", "/usr")
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    with pytest.raises(ValueError, match="virtual environment"):
        apply_approved_dependency_plan(dependency_id, focused["plan_id"])


def test_approved_install_uses_fixed_pypi_wheel_command(monkeypatch, tmp_path):
    import whaxon.core.installer as installer

    monkeypatch.setattr(sys, "prefix", "/tmp/whaxon-test-venv")
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    plan = build_remediation_plan()
    candidates = [action for action in plan["actions"]
                  if action["options"][0]["kind"] == "python-package"]
    if not candidates:
        pytest.skip("No missing Python package to install")
    dependency_id = candidates[0]["dependency_id"]
    focused = build_remediation_plan(dependency_ids=[dependency_id])
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, stdout="installed", stderr="")

    monkeypatch.setattr(installer.subprocess, "run", fake_run)
    monkeypatch.setattr(installer.importlib.metadata, "version", lambda _name: "99.0")
    monkeypatch.setattr(installer.importlib, "import_module", lambda _name: object())
    monkeypatch.setattr(installer, "_audit_path", lambda: tmp_path / "audit.jsonl")

    result = installer.apply_approved_dependency_plan(dependency_id, focused["plan_id"])
    assert result["status"] == "VERIFIED"
    argv, kwargs = calls[0]
    assert kwargs["shell"] is False
    assert "--only-binary=:all:" in argv
    assert argv[argv.index("--index-url") + 1] == "https://pypi.org/simple"
    records = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text().splitlines()]
    assert [record["status"] for record in records] == ["STARTED", "VERIFIED"]
