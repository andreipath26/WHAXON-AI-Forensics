from __future__ import annotations

import json

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
