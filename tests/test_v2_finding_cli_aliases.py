"""Tests for proposal-only V2 validate/retest CLI aliases."""
import json

import pytest

from whaxon.core import workflow_proposals
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.cli import retest_cmd, validate_cmd


class _Store:
    def __init__(self, verification_status):
        self.verification_status = verification_status

    def get_findings(self, _job_id):
        return [{"seq": 2, "kind": "sqli", "verification_status": self.verification_status}]

    def is_engine_v2_execution_job(self, _job_id):
        return True


class _Core:
    def __init__(self):
        self.store = _Store("candidate")
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
    # This mocks the shared proposal service to isolate CLI argument/mode/save wiring.
    # Sealed-source and retest eligibility are enforced by that service/provider path.
    core = _Core()
    core.store.verification_status = "verified" if mode == "retest" else "candidate"
    calls = []
    plan = WorkflowPlan(
        mission_id="mission-1",
        tasks=(WorkflowTask(
            id="verification-1",
            capability_id="tool.retest_sqli" if mode == "retest" else "tool.verify_sqli",
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


@pytest.mark.parametrize(
    "args",
    [
        ["job-1", "2", "--mission-id", "mission-1", "--plan-id", "--save"],
        ["job-1", "2", "--mission-id", "mission-1", "--mission-id", "other"],
        ["job-1", "-1"],
    ],
)
@pytest.mark.parametrize("command", [validate_cmd, retest_cmd])
def test_v2_alias_rejects_malformed_flags_before_core_initialization(
    command, args, monkeypatch, capsys,
):
    monkeypatch.setattr(
        command, "Core",
        lambda *_args, **_kwargs: pytest.fail("malformed invocation initialized Core"),
    )

    assert command.main(args) == command.EXIT_USAGE
    assert "Usage:" in capsys.readouterr().err


def test_v2_alias_rejects_malformed_proposal_even_without_save(capsys):
    from whaxon.interfaces.cli.finding_proposal_cli import run_finding_proposal

    class CoreWithoutSave:
        def save_workflow_plan(self, *_args):
            pytest.fail("dry proposal attempted persistence")

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            workflow_proposals,
            "propose_finding_verification_plan",
            lambda *_args, **_kwargs: {
                "status": "proposed", "plan_id": "plan-1",
                "plan": {"mission_id": "wrong", "tasks": []},
                "execution_submitted": False, "approval_granted": False,
            },
        )
        assert run_finding_proposal(
            CoreWithoutSave(), mission_id="mission-1", plan_id="plan-1",
            source_job_id="0123456789ab", finding_seq=2, mode="verify", save=False,
        ) == 4
        assert json.loads(capsys.readouterr().out)["status"] == "blocked"
    finally:
        monkeypatch.undo()
