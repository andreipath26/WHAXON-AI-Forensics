"""Active mission execution deadlines must not certify post-cutoff effects."""
import asyncio
import time

from whaxon.core.scheduler import WorkflowScheduler
from whaxon.core.store import JobStore
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _store(tmp_path):
    store = JobStore(tmp_path / "mission-deadline.db")
    store.create_mission("mission", "local deadline enforcement fixture")
    store.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("first", "fixture", "192.0.2.10"),
    )))
    return store


def test_deadline_exhaustion_refuses_late_success_commit(tmp_path):
    store = _store(tmp_path)
    claimed = store.claim_ready_workflow_task("plan", "worker")
    assert claimed is not None
    assert store.mark_workflow_dispatch_started("plan", claimed["attempt_id"])
    store.set_mission_deadline("mission", deadline_at=time.time() - 1)
    assert store.workflow_execution_stop_reason("plan") == "mission_deadline_exceeded"
    store.finish_task_attempt(claimed["attempt_id"], "succeeded", result={"ok": True})
    task = store.list_workflow_tasks("plan")[0]
    assert task["status"] == "uncertain"
    assert task["result"] is None
    assert "mission deadline expired" in task["error"]
    assert not any(
        event["event_type"] == "task_succeeded"
        for event in store.list_workflow_events("plan")
    )


def test_mission_deadline_stops_active_async_provider(tmp_path):
    async def scenario():
        store = _store(tmp_path)
        started = asyncio.Event()
        stopped = asyncio.Event()

        async def provider(task):
            assert task.id == "first"
            store.set_mission_deadline("mission", deadline_at=time.time() - 1)
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                stopped.set()

        result = await asyncio.wait_for(
            WorkflowScheduler(
                store, authorize=lambda task: True, dispatch=provider,
            ).run("plan", max_attempts=1),
            timeout=5,
        )
        assert started.is_set()
        assert stopped.is_set()
        assert result["outcomes"] == [
            {"task_id": "first", "status": "uncertain"},
        ]
        assert store.list_workflow_tasks("plan")[0]["status"] == "uncertain"

    asyncio.run(scenario())
