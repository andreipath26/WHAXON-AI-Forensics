"""E3/E5 durable request limits are independently checked before claim."""
import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _queue(tmp_path):
    core = Core(tmp_path)
    core.create_mission("mission", "durable queue contract")
    for n in (1, 2):
        core.save_workflow_plan(
            f"p{n}",
            WorkflowPlan("mission", (
                WorkflowTask(f"task{n}", "fixture", f"192.0.2.{n}"),
            )),
        )
    a = core.enqueue_workflow_run("p1")
    b = core.enqueue_workflow_run("p2")
    return core, a, b


@pytest.mark.parametrize("tampered", [
    "not-json", "[]", "null", '{"max_tasks":0,"max_attempts":1,"max_concurrency":1}',
    '{"max_tasks":true,"max_attempts":1,"max_concurrency":1}',
    '{"max_tasks":1,"max_attempts":1,"max_concurrency":1,"unsafe":1}',
])
def test_e5_invalid_persisted_limits_are_quarantined_and_valid_work_continues(
    tmp_path, tampered,
):
    core, poisoned, good = _queue(tmp_path)
    db = core.store._conn()
    try:
        db.execute(
            "UPDATE workflow_run_requests SET limits_json=?,submitted_at=1 "
            "WHERE id=?", (tampered, poisoned["id"]),
        )
    finally:
        db.close()
    restored = Core(tmp_path)
    claim = restored.workflow_requests.claim("worker")
    assert claim is not None and claim["id"] == good["id"]
    # The raw SQLite record retains the invalid payload for manual
    # reconciliation; the worker does not lease or dispatch the request.
    with restored.store._conn() as conn:
        status = conn.execute(
            "SELECT status FROM workflow_run_requests WHERE id=?",
            (poisoned["id"],),
        ).fetchone()["status"]
    assert status == "uncertain"
    events = [
        event for event in restored.store.list_workflow_events("p1")
        if event["event_type"] == "workflow_run_uncertain"
    ]
    assert len(events) == 1
    assert events[0]["detail"]["reason"] == "invalid_execution_limits"
    assert restored.workflow_requests.claim("another") is None


def test_e5_worker_claim_uses_valid_stored_execution_limits(tmp_path):
    core, first, second = _queue(tmp_path)
    claim = core.workflow_requests.claim("worker")
    assert claim["id"] in {first["id"], second["id"]}
    assert claim["limits"] == {
        "max_tasks": 100, "max_attempts": 2, "max_concurrency": 4,
    }
    assert isinstance(claim["lease_token"], str)
    assert claim["lease_token"]
