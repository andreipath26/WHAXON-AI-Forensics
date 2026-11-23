"""Regression tests for scheduler ownership fencing during provider dispatch."""
import asyncio

from whaxon.core.scheduler import WorkflowScheduler
from whaxon.core.workflow import WorkflowTask


class _NeverStoppedStore:
    def workflow_execution_stop_reason(self, plan_id):
        assert plan_id == "plan"
        return None


def test_lost_lease_cancels_in_flight_async_provider():
    async def scenario():
        started = asyncio.Event()
        cancelled = asyncio.Event()
        lease_lost = asyncio.Event()

        async def provider(task):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        scheduler = WorkflowScheduler(
            _NeverStoppedStore(), authorize=lambda task: True,
            dispatch=provider,
        )
        task = WorkflowTask("task", "fixture", "192.0.2.10")
        loop = asyncio.get_running_loop()
        work = asyncio.create_task(
            scheduler._dispatch_with_cancellation_watch(
                "plan", task, loop.time() + 10, lease_lost,
            )
        )
        await asyncio.wait_for(started.wait(), timeout=3)
        lease_lost.set()
        reason, result = await asyncio.wait_for(work, timeout=3)
        assert reason == "lease_lost"
        assert result is None
        assert cancelled.is_set()

    asyncio.run(scenario())


def test_lease_loss_precedes_a_simultaneous_provider_result():
    async def scenario():
        lease_lost = asyncio.Event()

        async def provider(task):
            lease_lost.set()
            return {"unexpected": "success"}

        scheduler = WorkflowScheduler(
            _NeverStoppedStore(), authorize=lambda task: True,
            dispatch=provider,
        )
        loop = asyncio.get_running_loop()
        reason, result = await scheduler._dispatch_with_cancellation_watch(
            "plan", WorkflowTask("task", "fixture", "192.0.2.10"),
            loop.time() + 10, lease_lost,
        )
        assert reason == "lease_lost"
        assert result is None

    asyncio.run(scenario())
