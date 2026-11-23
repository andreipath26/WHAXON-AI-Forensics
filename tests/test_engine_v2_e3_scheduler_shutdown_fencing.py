"""End-to-end scheduler cancellation distinguishes pre/post dispatch effects."""
import asyncio

import pytest

from whaxon.core.scheduler import WorkflowScheduler
from whaxon.core.store import JobStore
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


@pytest.mark.parametrize("after_dispatch", (False, True))
def test_scheduler_shutdown_preserves_dispatch_boundary(tmp_path, after_dispatch):
    store = JobStore(tmp_path / "scheduler-stop.db")
    store.create_mission("mission", "local cancellation fixture")
    store.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("first", "fixture", "192.0.2.10"),
        WorkflowTask(
            "dependent", "fixture", "192.0.2.10", depends_on=("first",),
        ),
    )))
    started = asyncio.Event()
    exited = asyncio.Event()
    provider_calls = []

    async def authorize(task):
        if not after_dispatch:
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                exited.set()
        return True

    async def provider(task):
        provider_calls.append(task.id)
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            exited.set()

    async def scenario():
        scheduler = WorkflowScheduler(
            store, authorize=authorize, dispatch=provider,
        )
        run = asyncio.create_task(scheduler.run("plan", max_attempts=1))
        await asyncio.wait_for(started.wait(), timeout=5)
        run.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(run, timeout=5)

    asyncio.run(scenario())
    tasks = {item["id"]: item for item in store.list_workflow_tasks("plan")}
    expected = "uncertain" if after_dispatch else "cancelled"
    assert exited.is_set()
    assert tasks["first"]["status"] == expected
    assert tasks["dependent"]["status"] != "succeeded"
    assert provider_calls == (["first"] if after_dispatch else [])
    events = store.list_workflow_events("plan")
    dispatches = [e for e in events if e["event_type"] == "dispatch_started"]
    assert len(dispatches) == (1 if after_dispatch else 0)
    assert any(e["event_type"] == f"task_{expected}" for e in events)
    assert store.claim_ready_workflow_task("plan", "replacement") is None
