from whaxon.core.workflow import (
    ApprovalBinding, WorkflowPlan, WorkflowTask,
)


def _plan():
    return WorkflowPlan(
        mission_id="mission-1",
        tasks=(
            WorkflowTask(
                id="recon", capability_id="network.port_scan", target="192.0.2.10",
                inputs={"ports": [80, 443]}, permissions=("network.scan",),
            ),
            WorkflowTask(
                id="web", capability_id="web.fingerprint", target="192.0.2.10",
                depends_on=("recon",), impact="low",
            ),
        ),
    )


def test_plan_roundtrip_is_stable_and_digest_is_deterministic():
    plan = _plan()
    restored = WorkflowPlan.from_dict(plan.to_dict())
    assert restored == plan
    assert restored.digest == plan.digest
    assert len(plan.digest) == 64


def test_plan_rejects_missing_dependency_and_cycle():
    import pytest

    with pytest.raises(ValueError, match="unknown dependencies"):
        WorkflowPlan("m", (WorkflowTask("a", "x", "host", depends_on=("missing",)),))
    with pytest.raises(ValueError, match="cycle"):
        WorkflowPlan(
            "m",
            (
                WorkflowTask("a", "x", "host", depends_on=("b",)),
                WorkflowTask("b", "y", "host", depends_on=("a",)),
            ),
        )


def test_task_rejects_unsafe_or_invalid_contract_values():
    import pytest

    with pytest.raises(ValueError, match="impact"):
        WorkflowTask("x", "cap", "host", impact="unbounded")
    with pytest.raises(ValueError, match="timeout"):
        WorkflowTask("x", "cap", "host", timeout_s=0)


def test_approval_binding_is_invalidated_by_any_bound_change():
    plan = _plan()
    task = plan.tasks[0]
    approval = ApprovalBinding(
        plan_digest=plan.digest,
        task_id=task.id,
        target=task.target,
        input_digest=ApprovalBinding.digest_inputs(task.inputs),
        policy_version="policy.v1",
        expires_at=200.0,
        permissions=task.permissions,
        impact=task.impact,
    )
    assert approval.is_valid(
        plan_digest=plan.digest, task=task, policy_version="policy.v1", now=100.0,
    )
    assert not approval.is_valid(
        plan_digest="changed", task=task, policy_version="policy.v1", now=100.0,
    )
    changed = WorkflowTask(
        id=task.id, capability_id=task.capability_id, target=task.target,
        inputs={"ports": [22]}, permissions=task.permissions, impact=task.impact,
    )
    assert not approval.is_valid(
        plan_digest=plan.digest, task=changed, policy_version="policy.v1", now=100.0,
    )
    assert not approval.is_valid(
        plan_digest=plan.digest, task=task, policy_version="policy.v2", now=100.0,
    )
    assert not approval.is_valid(
        plan_digest=plan.digest, task=task, policy_version="policy.v1", now=200.0,
    )
