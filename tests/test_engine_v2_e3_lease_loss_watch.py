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


def test_persisted_attempt_loss_on_provider_return_does_not_certify_success(tmp_path):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan

    async def scenario():
        store = JobStore(tmp_path / "lost-before-heartbeat.db")
        store.create_mission("mission", "controlled local ownership race")
        store.save_workflow_plan("plan", WorkflowPlan("mission", (
            WorkflowTask("first", "fixture", "192.0.2.10"),
            WorkflowTask(
                "dependent", "fixture", "192.0.2.10",
                depends_on=("first",),
            ),
        )))
        dispatched = []

        async def provider(task):
            dispatched.append(task.id)
            # Simulate lease reconciliation by another worker between the
            # last heartbeat and provider completion.
            store.finish_task_attempt(
                getattr(task, "_attempt_id"), "uncertain",
                error="simulated worker ownership loss",
            )
            return {"result": "must not be certified"}

        result = await WorkflowScheduler(
            store, authorize=lambda task: True, dispatch=provider,
        ).run("plan", max_attempts=1)
        assert dispatched == ["first"]
        assert result["outcomes"] == [
            {"task_id": "first", "status": "uncertain"},
        ]
        tasks = {row["id"]: row["status"] for row in result["tasks"]}
        assert tasks["first"] == "uncertain"
        assert tasks["dependent"] != "succeeded"
        assert store.list_workflow_tasks("plan")[0]["status"] == "uncertain"

    asyncio.run(scenario())


def test_reconciled_attempt_cannot_be_rewritten_by_late_provider_error(tmp_path):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan

    async def scenario():
        store = JobStore(tmp_path / "lost-before-exception.db")
        store.create_mission("mission", "controlled local error race")
        store.save_workflow_plan("plan", WorkflowPlan("mission", (
            WorkflowTask("first", "fixture", "192.0.2.10"),
        )))

        async def provider(task):
            store.finish_task_attempt(
                getattr(task, "_attempt_id"), "uncertain",
                error="simulated independent reconciliation",
            )
            raise RuntimeError("late provider disconnect")

        result = await WorkflowScheduler(
            store, authorize=lambda task: True, dispatch=provider,
        ).run("plan", max_attempts=1)
        assert result["outcomes"] == [
            {"task_id": "first", "status": "uncertain"},
        ]
        task = store.list_workflow_tasks("plan")[0]
        assert task["status"] == "uncertain"
        assert task["error"] == "simulated independent reconciliation"

    asyncio.run(scenario())
