"""A fatal parallel scheduler error must not strand active sibling coroutines."""
import asyncio

import pytest

from whaxon.core.scheduler import WorkflowScheduler
from whaxon.core.store import JobStore
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def test_parallel_worker_failure_cancels_and_joins_remaining_work(tmp_path):
    store = JobStore(tmp_path / "worker-failure.db")
    store.create_mission("mission", "controlled local scheduler failure")
    store.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("first", "fixture", "192.0.2.10"),
        WorkflowTask("second", "fixture", "192.0.2.11"),
    )))
    active = asyncio.Event()
    stopped = asyncio.Event()
    calls = []

    async def synthetic_execute(row):
        calls.append(row["id"])
        if row["id"] == "first":
            active.set()
            try:
                await asyncio.Event().wait()
            finally:
                stopped.set()
        await active.wait()
        raise RuntimeError("synthetic fatal worker failure")

    async def scenario():
        scheduler = WorkflowScheduler(
            store, authorize=lambda task: True, dispatch=lambda task: None,
        )
        scheduler._execute = synthetic_execute
        with pytest.raises(RuntimeError, match="synthetic fatal worker failure"):
            await asyncio.wait_for(
                scheduler.run("plan", max_concurrency=2, max_tasks=2),
                timeout=5,
            )
        # Assert inside the still-running loop: shutdown of asyncio.run()
        # must not be the thing that eventually cancels the sibling worker.
        assert stopped.is_set()
        assert calls == ["first", "second"]

    asyncio.run(scenario())
