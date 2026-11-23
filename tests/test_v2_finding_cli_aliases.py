"""Tests for proposal-only V2 validate/retest CLI aliases."""
import asyncio
import json
from types import SimpleNamespace

import pytest

from whaxon.core import workflow_proposals
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.cli import retest_cmd, validate_cmd


class _Store:
    def get_findings(self, _job_id):
        return [{"seq": 2, "kind": "sqli", "verification_status": "candidate"}]

    def is_engine_v2_execution_job(self, _job_id):
        return True


class _Core:
    def __init__(self):
        self.store = _Store()
        self.saved = []

    async def initialize(self, *, drain=False):
        assert drain is False

    def save_workflow_plan(self, plan_id, plan):
        self.saved.append((plan_id, plan))
        return True


@pytest.mark.parametrize(
    ("command", "mode"),
    [(validate_cmd, "verify"), (retest_cmd, "retest")],
)
@pytest.mark.parametrize("save", [False, True])
def test_v2_finding_alias_proposes_and_saves_only_when_requested(
    command, mode, save, monkeypatch, capsys,
):
    core = _Core()
    calls = []
    plan = WorkflowPlan(
        mission_id="mission-1",
        tasks=(WorkflowTask(
            id="verification-1",
            capability_id="tool.verify_sqli",
            target="http://192.0.2.10/search",
            inputs={"source_job_id": "0123456789ab", "finding_seq": 2},
            impact="moderate",
            timeout_s=30,
        ),),
    )

    def propose(_core, **kwargs):
        calls.append((_core, kwargs))
        return {
            "status": "proposed",
            "plan_id": kwargs["plan_id"],
            "plan": plan.to_dict(),
            "execution_submitted": False,
            "approval_granted": False,
        }

    monkeypatch.setattr(command, "Core", lambda _data_dir: core)
    monkeypatch.setattr(workflow_proposals, "propose_finding_verification_plan", propose)

    args = [
        "0123456789ab", "2", "--mission-id", "mission-1", "--plan-id", "plan-1",
    ]
    if save:
        args.append("--save")
    assert command.main(args) == command.EXIT_OK

    output = json.loads(capsys.readouterr().out)
    assert calls == [(core, {
        "mission_id": "mission-1",
        "plan_id": "plan-1",
        "source_job_id": "0123456789ab",
        "finding_seq": 2,
        "mode": mode,
    })]
    assert output["execution_submitted"] is False
    assert output["approval_granted"] is False
    assert output["created"] is save
    assert len(core.saved) == int(save)
