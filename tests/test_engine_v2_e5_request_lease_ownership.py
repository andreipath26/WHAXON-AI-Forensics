"""Durable run-request lease loss must stop its active scheduler immediately.

These fixtures never invoke an external provider or target; they exercise the
shared Core queue-to-scheduler authority boundary with a suspended DAG.
"""
import asyncio

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


@pytest.mark.parametrize("heartbeat_fails_with_exception", (False, True))
def test_lost_run_request_lease_cancels_active_workflow_and_never_succeeds(
    tmp_path, monkeypatch, heartbeat_fails_with_exception,
):
    core = Core(tmp_path)
    core.create_mission("mission", "controlled local lease-loss fixture")
    core.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("one", "fixture", "192.0.2.10"),
    )))
    request = core.enqueue_workflow_run("plan")
    started = asyncio.Event()
    stopped = asyncio.Event()

    async def hung_workflow(*_args, **_kwargs):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()

    monkeypatch.setattr(core, "run_workflow_plan", hung_workflow)

    def lost_heartbeat(*_args):
        if heartbeat_fails_with_exception:
            raise OSError("simulated loss of durable heartbeat storage")
        return False

    monkeypatch.setattr(core.workflow_requests, "heartbeat", lost_heartbeat)

    async def scenario():
        drained = await asyncio.wait_for(
            core.drain_workflow_run_requests(initialized=True, max_runs=1),
            timeout=9,
        )
        assert drained == 1
        assert started.is_set()
        assert stopped.is_set()

    asyncio.run(scenario())
    record = core.workflow_run_request(request["id"])
    assert record["status"] == "uncertain"
    assert "lease lost" in record["error"]
    assert core.workflow_requests.claim("other-worker") is None


def test_lost_run_request_lease_stops_real_scheduler_and_dependents(
    tmp_path, monkeypatch,
):
    """Exercise Core -> durable request -> scheduler -> attempt DB lifecycle."""
    from whaxon.core.scheduler import WorkflowScheduler

    core = Core(tmp_path)
    core.create_mission("mission", "controlled local durable-workflow fixture")
    core.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("first", "fixture", "192.0.2.10"),
        WorkflowTask("dependent", "fixture", "192.0.2.10", depends_on=("first",)),
    )))
    request = core.enqueue_workflow_run("plan")
    entered = asyncio.Event()
    interrupted = asyncio.Event()
    dispatched = []

    async def provider(task):
        dispatched.append(task.id)
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            interrupted.set()

    monkeypatch.setattr(
        core, "workflow_scheduler",
        lambda **_kwargs: WorkflowScheduler(
            core.store, authorize=lambda task: True, dispatch=provider,
        ),
    )
    monkeypatch.setattr(core.workflow_requests, "heartbeat", lambda *_args: False)

    async def scenario():
        assert await asyncio.wait_for(
            core.drain_workflow_run_requests(initialized=True, max_runs=1),
            timeout=9,
        ) == 1

    asyncio.run(scenario())
    tasks = {item["id"]: item["status"] for item in core.store.list_workflow_tasks("plan")}
    assert entered.is_set()
    assert interrupted.is_set()
    assert dispatched == ["first"]
    assert tasks["first"] == "uncertain"
    assert tasks["dependent"] != "succeeded"
    assert core.workflow_run_request(request["id"])["status"] == "uncertain"
    assert core.workflow_requests.claim("replacement") is None
