"""Mission runtime-budget terminalization fences for Engine V2."""
import time

from whaxon.core.store import JobStore
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _store(tmp_path):
    store = JobStore(tmp_path / "terminal-runtime.db")
    store.create_mission("mission", "controlled local runtime test")
    for plan_id in ("first", "second"):
        store.save_workflow_plan(plan_id, WorkflowPlan("mission", (
            WorkflowTask("scan", "fixture", "192.0.2.10"),
        )))
    return store


def test_exhausted_runtime_budget_blocks_late_success_commit(tmp_path):
    store = _store(tmp_path)
    claim = store.claim_ready_workflow_task("first", "worker")
    assert claim is not None
    assert store.mark_workflow_dispatch_started("first", claim["attempt_id"])
    store.set_mission_runtime_limit("mission", max_runtime_s=1)
    # A provider returned before the stop watcher polled again. The
    # terminal write must enforce the cap against persisted attempt time.
    with store._lock:
        conn = store._conn()
        try:
            conn.execute(
                "UPDATE task_attempts SET started_at=? WHERE id=?",
                (time.time() - 5, claim["attempt_id"]),
            )
        finally:
            conn.close()
    store.finish_task_attempt(claim["attempt_id"], "succeeded", result={"ok": True})
    rows = store.list_workflow_tasks("first")
    assert rows[0]["status"] == "uncertain"
    assert rows[0]["result"] is None
    assert "runtime budget exhausted" in rows[0]["error"]
    assert not any(
        e["event_type"] == "task_succeeded"
        for e in store.list_workflow_events("first")
    )
    assert store.claim_ready_workflow_task("second", "other-worker") is None


def test_unexhausted_runtime_budget_allows_success(tmp_path):
    store = _store(tmp_path)
    store.set_mission_runtime_limit("mission", max_runtime_s=120)
    claim = store.claim_ready_workflow_task("first", "worker")
    assert claim is not None
    store.finish_task_attempt(claim["attempt_id"], "succeeded", result={"ok": True})
    assert store.list_workflow_tasks("first")[0]["status"] == "succeeded"
