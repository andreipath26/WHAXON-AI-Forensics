from __future__ import annotations

import pytest

from whaxon.core.recon_v2 import CAPABILITY_ID
from whaxon.interfaces.cli import recon_cmd


class _FakeCore:
    def __init__(self, *, tasks=None, result=None, report=None):
        self.tasks = tasks if tasks is not None else [{
            "id": "task-1",
            "capability_id": CAPABILITY_ID,
            "target": "example.test",
            "inputs": {},
            "depends_on": [],
        }]
        self.result = result or {
            "complete": True,
            "tasks": [{"id": "task-1", "status": "succeeded"}],
        }
        self.report = report or {
            "status": "complete",
            "findings": [{
                "severity": "info",
                "kind": "dns_record",
                "raw_line": "example.test A 192.0.2.1",
            }],
        }
        self.run_calls = []
        self.legacy_calls = []

    async def initialize(self, *, drain=False):
        assert drain is False

    def workflow_plan_details(self, plan_id):
        assert plan_id == "dns-plan"
        return {"plan": {"tasks": self.tasks}}

    async def run_workflow_plan(self, plan_id):
        self.run_calls.append(plan_id)
        return self.result

    def workflow_report(self, plan_id):
        assert plan_id == "dns-plan"
        return self.report


@pytest.mark.parametrize(
    "tasks",
    [
        [{
            "id": "task-1",
            "capability_id": "network.services.discover",
            "target": "example.test",
            "inputs": {},
            "depends_on": [],
        }],
        [{
            "id": "task-1",
            "capability_id": CAPABILITY_ID,
            "target": "other.test",
            "inputs": {},
            "depends_on": [],
        }],
        [
            {
                "id": "task-1",
                "capability_id": CAPABILITY_ID,
                "target": "example.test",
                "inputs": {},
                "depends_on": [],
            },
            {
                "id": "task-2",
                "capability_id": CAPABILITY_ID,
                "target": "example.test",
                "inputs": {},
                "depends_on": [],
            },
        ],
        [{
            "id": "task-1",
            "capability_id": CAPABILITY_ID,
            "target": "example.test",
            "inputs": {"record_types": ["A"]},
            "depends_on": [],
        }],
    ],
)
def test_v2_recon_rejects_non_exact_plan_before_dispatch(monkeypatch, capsys, tasks):
    core = _FakeCore(tasks=tasks)
    monkeypatch.setattr(recon_cmd, "Core", lambda _data_dir: core)

    status = recon_cmd.main([
        "example.test", "--engine", "v2", "--plan-id", "dns-plan",
    ])

    assert status == recon_cmd.EXIT_USAGE
    assert core.run_calls == []
    assert "V2 recon" in capsys.readouterr().err


def test_v2_recon_delegates_to_approved_workflow_and_prints_persisted_findings(
    monkeypatch, capsys,
):
    core = _FakeCore()
    monkeypatch.setattr(recon_cmd, "Core", lambda _data_dir: core)

    status = recon_cmd.main([
        "example.test", "--engine", "v2", "--plan-id", "dns-plan",
    ])

    output = capsys.readouterr().out
    assert status == recon_cmd.EXIT_OK
    assert core.run_calls == ["dns-plan"]
    assert "plan dns-plan, succeeded, 1 findings" in output
    assert "example.test A 192.0.2.1" in output


def test_v2_recon_unapproved_plan_remains_failed_by_workflow_engine(
    monkeypatch, capsys,
):
    core = _FakeCore(result={
        "complete": False,
        "tasks": [{"id": "task-1", "status": "failed"}],
    }, report={"findings": []})
    monkeypatch.setattr(recon_cmd, "Core", lambda _data_dir: core)

    status = recon_cmd.main([
        "example.test", "--engine", "v2", "--plan-id", "dns-plan",
    ])

    assert status == recon_cmd.EXIT_ERROR
    assert core.run_calls == ["dns-plan"]
    assert "failed, 0 findings" in capsys.readouterr().out


def test_v2_recon_requires_plan_and_disallows_legacy_check_filter():
    assert recon_cmd.main(["example.test", "--engine", "v2"]) == recon_cmd.EXIT_USAGE
    assert recon_cmd.main([
        "example.test", "--engine", "v2", "--plan-id", "dns-plan",
        "--checks", "dns",
    ]) == recon_cmd.EXIT_USAGE


def test_legacy_recon_default_remains_available(monkeypatch, capsys):
    core = _FakeCore()
    core.scope = type("Scope", (), {
        "check": lambda _self, _target: type("Decision", (), {
            "allowed": True, "reason": "", "matched_rule": "",
        })(),
    })()
    core.recon = type("Recon", (), {
        "run": lambda _self, target, checks=None: "legacy-job",
    })()
    core.store = type("Store", (), {
        "get_findings": lambda _self, _job_id: [],
    })()
    monkeypatch.setattr(recon_cmd, "Core", lambda _data_dir: core)

    status = recon_cmd.main(["example.test"])

    assert status == recon_cmd.EXIT_OK
    assert "legacy-job" in capsys.readouterr().out


def test_v2_recon_partial_persisted_report_is_not_success(
    monkeypatch, capsys,
):
    core = _FakeCore(report={"status": "partial", "findings": [{
        "severity": "info",
        "kind": "dns_record",
        "raw_line": "example.test A 192.0.2.1",
    }]})
    monkeypatch.setattr(recon_cmd, "Core", lambda _data_dir: core)

    status = recon_cmd.main([
        "example.test", "--engine", "v2", "--plan-id", "dns-plan",
    ])

    assert status == recon_cmd.EXIT_ERROR
    assert core.run_calls == ["dns-plan"]
    assert "succeeded, 1 findings" in capsys.readouterr().out
