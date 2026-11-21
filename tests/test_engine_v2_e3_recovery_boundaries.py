"""Engine V2 E3: cross-boundary recovery input and plan identity hardening."""
from __future__ import annotations

import asyncio

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _core(tmp_path):
    core = Core(tmp_path)
    core.create_mission("mission", "E3 recovery boundary regression")
    core.save_workflow_plan(
        "plan",
        WorkflowPlan("mission", (
            WorkflowTask("task", "fixture", "192.0.2.10"),
        )),
    )
    return core


@pytest.mark.parametrize("running", [False, True])
def test_duplicate_enqueue_refuses_changed_plan_digest_without_rebinding(
    tmp_path, running,
):
    core = _core(tmp_path)
    request = core.enqueue_workflow_run("plan")
    if running:
        claim = core.workflow_requests.claim("original-worker")
        assert claim is not None and claim["id"] == request["id"]

    # Simulate changed persisted plan identity in an independent process.
    db = core.store._conn()
    try:
        db.execute(
            "UPDATE workflow_plans SET digest=? WHERE id=?",
            ("changed-plan-digest", "plan"),
        )
    finally:
        db.close()

    restarted = Core(tmp_path)
    with pytest.raises(ValueError, match="different plan digest"):
        restarted.enqueue_workflow_run("plan")
    record = restarted.workflow_run_request(request["id"])
    assert record["plan_digest"] == request["plan_digest"]
    assert record["status"] == ("running" if running else "queued")
    assert "lease_token" not in record
    if not running:
        assert restarted.workflow_requests.claim("replacement-worker") is None
        assert restarted.workflow_run_request(request["id"])["status"] == "uncertain"


@pytest.mark.parametrize("threshold", [
    True, False, 0, -1, float("nan"), float("inf"),
    float("-inf"), "nan", "invalid", object(),
])
def test_recovery_rejects_invalid_stale_threshold_without_mutation(
    tmp_path, threshold,
):
    core = _core(tmp_path)
    row = core.store.claim_ready_workflow_task("plan", "original-worker")
    assert row is not None
    before = core.store.list_workflow_attempts("plan")
    with pytest.raises(ValueError, match="finite and positive"):
        core.store.reconcile_workflow_attempts(stale_after_s=threshold)
    assert core.store.list_workflow_attempts("plan") == before


def test_recovery_with_valid_threshold_preserves_fresh_lease(tmp_path):
    core = _core(tmp_path)
    claimed = core.store.claim_ready_workflow_task("plan", "original-worker")
    assert claimed is not None
    assert core.store.reconcile_workflow_attempts(stale_after_s=60) == 0
    assert core.store.workflow_attempt_owned(claimed["attempt_id"])


@pytest.mark.parametrize("limit", [True, False, 0, -1, 1025, 1.5, "128"])
def test_recovery_rejects_invalid_batch_limit_without_mutation(tmp_path, limit):
    core = _core(tmp_path)
    claimed = core.store.claim_ready_workflow_task("plan", "original-worker")
    assert claimed is not None
    before = core.store.list_workflow_attempts("plan")
    with pytest.raises(ValueError, match="limit must be an integer"):
        core.store.reconcile_workflow_attempts(limit=limit)
    assert core.store.list_workflow_attempts("plan") == before


def test_initialize_drains_stale_attempts_in_bounded_pages(tmp_path, monkeypatch):
    core = Core(tmp_path)
    core.create_mission("mission", "bounded stale-attempt recovery")
    attempt_count = 129
    core.configure_mission_execution_limits(
        "mission", max_total_attempts=attempt_count,
        max_concurrency=attempt_count,
    )
    attempt_ids = []
    for index in range(attempt_count):
        plan_id = f"plan-{index:03d}"
        core.save_workflow_plan(
            plan_id,
            WorkflowPlan("mission", (
                WorkflowTask(f"task-{index:03d}", "fixture", "192.0.2.10"),
            )),
        )
        claim = core.store.claim_ready_workflow_task(
            plan_id, f"worker-{index:03d}",
        )
        assert claim is not None
        attempt_ids.append(claim["attempt_id"])

    conn = core.store._conn()
    try:
        conn.execute("UPDATE task_attempts SET heartbeat_at=0, started_at=0")
    finally:
        conn.close()

    reconcile = core.store.reconcile_workflow_attempts
    page_results = []

    def record_pages(*args, **kwargs):
        result = reconcile(*args, **kwargs)
        page_results.append(result)
        return result

    monkeypatch.setattr(core.store, "reconcile_workflow_attempts", record_pages)
    asyncio.run(core.initialize(drain=False))

    assert page_results == [128, 1, 0]
    assert all(
        core.store.get_workflow_attempt_status(attempt_id) == "uncertain"
        for attempt_id in attempt_ids
    )
