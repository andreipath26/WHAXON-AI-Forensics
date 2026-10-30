from __future__ import annotations

import json

from whaxon.core.remediation import build_remediation_plan


def test_plan_is_read_only_and_deterministic():
    first = build_remediation_plan(dependency_ids=["textual"])
    second = build_remediation_plan(dependency_ids=["textual"])
    assert first == second
    assert first["safety"]["read_only"] is True
    assert first["safety"]["commands_executed"] is False
    assert first["safety"]["installation_attempted"] is False
    assert first["safety"]["approval_granted"] is False
    json.dumps(first)


def test_plan_never_invents_command_for_external_tool():
    plan = build_remediation_plan(dependency_ids=["nmap"])
    if plan["actions"]:
        option = plan["actions"][0]["options"][0]
        assert option["kind"] == "manual"
        assert option["command"] is None
        assert option["automated_execution_supported"] is False


def test_unknown_dependency_is_reported():
    plan = build_remediation_plan(dependency_ids=["not-a-real-dependency"])
    assert plan["unknown_dependency_ids"] == ["not-a-real-dependency"]


def test_empty_dependency_selection_produces_no_actions():
    plan = build_remediation_plan(dependency_ids=[])
    assert plan["actions"] == []
    assert plan["unknown_dependency_ids"] == []


def test_python_package_plan_discloses_exact_restricted_install_contract():
    plan = build_remediation_plan(dependency_ids=["textual"])
    if not plan["actions"]:
        return
    option = plan["actions"][0]["options"][0]
    assert option["kind"] == "python-package"
    assert option["command"][0].endswith("python") or option["command"][0].endswith("python.exe")
    assert "--isolated" in option["command"]
    assert "--only-binary=:all:" in option["command"]
    assert option["package_source"] == "https://pypi.org/simple"
    assert option["may_install_transitive_dependencies"] is True
    assert "transitive dependencies" in option["warning"]
