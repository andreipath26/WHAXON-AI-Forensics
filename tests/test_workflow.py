import asyncio
import inspect

import pytest


def _run_async_test(test_function):
    """Run an async test without competing pytest event-loop plugins.

    pytest-playwright and pytest-asyncio both wrap coroutine tests when
    asyncio_mode=auto. Keep these scheduler tests independent of browser
    fixtures by exposing a synchronous pytest test that owns its loop.
    """
    def run(*args, **kwargs):
        return asyncio.run(test_function(*args, **kwargs))

    # Preserve fixture discovery without exposing a coroutine function to
    # pytest-asyncio's auto mode (which would wrap it in a second event loop).
    run.__signature__ = inspect.signature(test_function)
    run.__name__ = test_function.__name__
    run.__qualname__ = test_function.__qualname__
    run.__doc__ = test_function.__doc__
    return run

from whaxon.core.workflow import (
    ApprovalBinding,
    WorkflowPlan,
    WorkflowTask,
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


@_run_async_test
async def test_scheduler_blocks_dependants_when_dependency_exhausts_retries(tmp_path):
    from whaxon.core.scheduler import WorkflowScheduler
    from whaxon.core.store import JobStore

    store = JobStore(tmp_path / "scheduler-exhausted.db")
    store.create_mission("mission-1", "objective")
    store.save_workflow_plan("p", _plan())
    calls = []

    def dispatch(task):
        calls.append(task.id)
        raise RuntimeError("provider unavailable")

    scheduler = WorkflowScheduler(store, authorize=lambda task: True, dispatch=dispatch)
    result = await scheduler.run("p", max_attempts=1)
    assert calls == ["recon"]
    assert result["tasks"] == [
        {"id": "recon", "status": "failed"},
        {"id": "web", "status": "blocked"},
    ]
    assert result["complete"] is True


@_run_async_test
async def test_scheduler_blocks_dependants_after_policy_denial(tmp_path):
    from whaxon.core.scheduler import WorkflowScheduler
    from whaxon.core.store import JobStore

    store = JobStore(tmp_path / "scheduler-blocked.db")
    store.create_mission("mission-1", "objective")
    store.save_workflow_plan("p", _plan())
    result = await WorkflowScheduler(
        store, authorize=lambda task: False, dispatch=lambda task: None,
    ).run("p")
    assert result["tasks"] == [
        {"id": "recon", "status": "blocked"},
        {"id": "web", "status": "blocked"},
    ]
    assert result["complete"] is True


def test_workflow_contract_nested_mappings_are_immutable():

    inputs = {"options": {"ports": [80, 443]}}
    metadata = {"labels": ["approved"]}
    task = WorkflowTask("scan", "network.port_scan", "192.0.2.10", inputs=inputs)
    plan = WorkflowPlan("m", (task,), metadata=metadata)
    digest = plan.digest
    inputs["options"]["ports"].append(8080)
    metadata["labels"].append("changed")
    assert plan.digest == digest
    with pytest.raises(TypeError, match="immutable"):
        task.inputs["new"] = "value"
    with pytest.raises(TypeError, match="immutable"):
        task.inputs["options"]["new"] = "value"
    assert task.inputs["options"]["ports"] == (80, 443)


def test_workflow_task_rejects_non_finite_timeout():
    import math


    with pytest.raises(ValueError, match="finite"):
        WorkflowTask("bad", "cap", "host", timeout_s=math.inf)
    with pytest.raises(ValueError, match="finite"):
        WorkflowTask("bad", "cap", "host", timeout_s=math.nan)


@_run_async_test
async def test_scheduler_applies_timeout_to_synchronous_provider(tmp_path):
    import time

    from whaxon.core.scheduler import WorkflowScheduler
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "scheduler-sync-timeout.db")
    store.create_mission("m", "objective")
    store.save_workflow_plan(
        "p", WorkflowPlan("m", (
            WorkflowTask("slow", "provider.sync", "192.0.2.10", timeout_s=0.01),
        )),
    )

    def dispatch(task):
        time.sleep(0.1)
        return {"done": True}

    result = await WorkflowScheduler(
        store, authorize=lambda task: True, dispatch=dispatch,
    ).run("p")
    assert result["tasks"] == [{"id": "slow", "status": "uncertain"}]
    assert result["attempts"] == 1



@_run_async_test
async def test_scheduler_runs_independent_tasks_concurrently(tmp_path):
    import asyncio

    from whaxon.core.scheduler import WorkflowScheduler
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "scheduler-parallel.db")
    store.create_mission("m", "objective")
    store.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("a", "provider.a", "192.0.2.10"),
        WorkflowTask("b", "provider.b", "192.0.2.11"),
        WorkflowTask("c", "provider.c", "192.0.2.12", depends_on=("a", "b")),
    )))
    active = 0
    peak = 0
    gate = asyncio.Event()

    async def dispatch(task):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        if task.id in ("a", "b"):
            if peak >= 2:
                gate.set()
            await asyncio.wait_for(gate.wait(), timeout=1)
        else:
            assert task.id == "c"
            states = store.list_workflow_tasks("p")
            assert all(x["status"] == "succeeded" for x in states[:2])
        active -= 1
        return {"task": task.id}

    result = await WorkflowScheduler(
        store, authorize=lambda task: True, dispatch=dispatch,
    ).run("p", max_concurrency=2)

    assert peak == 2
    assert result["attempts"] == 3
    assert result["complete"] is True
    assert [task["status"] for task in result["tasks"]] == [
        "succeeded", "succeeded", "succeeded",
    ]


@_run_async_test
async def test_scheduler_respects_max_concurrency_and_task_budget(tmp_path):
    import asyncio

    from whaxon.core.scheduler import WorkflowScheduler
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "scheduler-budget.db")
    store.create_mission("m", "objective")
    store.save_workflow_plan("p", WorkflowPlan("m", tuple(
        WorkflowTask(f"task-{i}", "provider.scan", f"192.0.2.{i + 1}")
        for i in range(5)
    )))
    active = 0
    peak = 0

    async def dispatch(task):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        return task.id

    result = await WorkflowScheduler(
        store, authorize=lambda task: True, dispatch=dispatch,
    ).run("p", max_tasks=3, max_concurrency=2)

    assert result["attempts"] == 3
    assert peak <= 2
    assert sum(task["status"] == "succeeded" for task in result["tasks"]) == 3
    assert result["complete"] is False
