"""Durable Engine V2 workflow-run request acceptance and restart behavior."""
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


def _core(tmp_path):
    core = Core(tmp_path)
    core.create_mission("m", "authorized controlled workflow")
    core.save_workflow_plan("p", WorkflowPlan(
        "m", (WorkflowTask("recon", "fixture", "192.0.2.10"),),
    ))
    return core


def test_run_request_survives_core_restart_and_deduplicates(tmp_path):
    first = _core(tmp_path)
    limits = {"max_tasks": 3, "max_attempts": 2, "max_concurrency": 1}
    queued = first.workflow_requests.enqueue("p", limits=limits)
    same = first.workflow_requests.enqueue("p", limits=limits)
    assert queued["id"] == same["id"]
    with pytest.raises(ValueError, match="different limits"):
        first.workflow_requests.enqueue(
            "p", limits={**limits, "max_concurrency": 2},
        )
    second = Core(tmp_path)
    from_disk = second.workflow_run_request(queued["id"])
    assert from_disk["status"] == "queued"
    assert from_disk["plan_digest"] == queued["plan_digest"]
    assert from_disk["limits"] == limits


def test_run_request_uses_atomic_claim_and_lease_fencing(tmp_path):
    first = _core(tmp_path)
    row = first.enqueue_workflow_run("p")
    second = Core(tmp_path)
    claim = second.workflow_requests.claim("worker-a")
    assert claim["id"] == row["id"]
    assert first.workflow_requests.claim("worker-b") is None
    assert not first.workflow_requests.heartbeat(row["id"], "wrong-token")
    assert not first.workflow_requests.finish(
        row["id"], "wrong-token", status="completed",
    )
    assert second.workflow_requests.heartbeat(row["id"], claim["lease_token"])
    assert second.workflow_requests.finish(
        row["id"], claim["lease_token"], status="completed",
    )
    assert first.workflow_run_request(row["id"])["status"] == "completed"


def test_stale_run_is_uncertain_not_automatically_replayed(tmp_path):
    core = _core(tmp_path)
    request = core.enqueue_workflow_run("p")
    claimed = core.workflow_requests.claim("worker")
    conn = core.store._conn()
    try:
        conn.execute(
            "UPDATE workflow_run_requests SET heartbeat_at=? WHERE id=?",
            (time.time() - 1000, request["id"]),
        )
    finally:
        conn.close()
    assert core.workflow_requests.reconcile_stale(older_than_s=60) == 1
    assert core.workflow_run_request(request["id"])["status"] == "uncertain"
    assert core.workflow_requests.claim("other") is None
    assert not core.workflow_requests.finish(
        request["id"], claimed["lease_token"], status="completed",
    )
    with pytest.raises(ValueError, match="different limits"):
        core.enqueue_workflow_run(
            "p", max_tasks=1, max_attempts=2, max_concurrency=4,
        )


def test_drain_queued_work_after_restart_without_unsafe_reexecution(tmp_path):
    first = _core(tmp_path)
    request = first.enqueue_workflow_run("p")
    second = Core(tmp_path)
    # The fixture capability cannot execute: policy must block it, rather
    # than using an unverified binary or another execution path.
    with ThreadPoolExecutor(max_workers=1) as executor:
        assert executor.submit(
            lambda: asyncio.run(second.drain_workflow_run_requests()),
        ).result() == 1
    row = first.workflow_run_request(request["id"])
    assert row["status"] == "completed"
    assert first.workflow_progress("p")["counts"]["blocked"] == 1
    with ThreadPoolExecutor(max_workers=1) as executor:
        assert executor.submit(
            lambda: asyncio.run(second.drain_workflow_run_requests()),
        ).result() == 0


def test_api_202_is_persisted_before_worker_wakeup(tmp_path, monkeypatch):
    core = _core(tmp_path)
    recorded = []
    monkeypatch.setattr(AsyncRunner, "submit", lambda self, callback: recorded.append(callback))
    app = create_app(core, JobRegistry(core), AsyncRunner(core))
    app.config["TESTING"] = True
    client = app.test_client()
    result = client.post("/api/v2/workflows/p/run", json={
        "max_tasks": 2, "max_attempts": 2, "max_concurrency": 1,
    })
    assert result.status_code == 202
    payload = result.get_json()
    request_id = payload["run_request_id"]
    assert payload["execution_completed"] is False
    assert len(recorded) == 1
    assert core.workflow_run_request(request_id)["status"] == "queued"
    assert client.get(payload["run_request_url"]).get_json()["id"] == request_id
    again = client.post("/api/v2/workflows/p/run", json={
        "max_tasks": 2, "max_attempts": 2, "max_concurrency": 1,
    })
    assert again.get_json()["run_request_id"] == request_id
    assert client.get("/api/v2/workflow-runs/missing").status_code == 404
    assert client.post("/api/v2/workflows/missing/run").status_code == 404
    assert client.post("/api/v2/workflows/p/run", json={
        "max_tasks": 0,
    }).status_code == 400
    assert client.post("/api/v2/workflows/p/run", json={
        "max_tasks": True,
    }).status_code == 400


def test_cancelled_workflow_cannot_be_newly_submitted(tmp_path):
    core = _core(tmp_path)
    core.cancel_workflow_plan("p")
    with pytest.raises(ValueError, match="cancelled"):
        core.enqueue_workflow_run("p")

def test_cancel_closes_queued_run_request_without_executing(tmp_path):
    core = _core(tmp_path)
    request = core.enqueue_workflow_run("p")
    core.cancel_workflow_plan("p")
    assert core.workflow_run_request(request["id"])["status"] == "cancelled"
    assert core.workflow_requests.claim("worker") is None
    assert core.workflow_progress("p")["cancellation_requested"] is True
