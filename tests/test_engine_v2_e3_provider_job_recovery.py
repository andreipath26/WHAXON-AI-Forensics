"""Recover only complete, attempt-bound provider results after lost acks."""
from __future__ import annotations

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _uncertain_catalog_attempt(
    tmp_path, *, job_status="finished", exit_code=0,
    capability_id="tool.nmap",
):
    core = Core(tmp_path)
    core.create_mission("m", "recover lost provider acknowledgement")
    task_args = {"permissions": ("network.scan",), "impact": "moderate"} \
        if capability_id.startswith("tool.") else {}
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", capability_id, "192.0.2.10", **task_args),
    )))
    request = core.enqueue_workflow_run("p")
    run_claim = core.workflow_requests.claim("run-worker")
    assert run_claim and run_claim["id"] == request["id"]
    claim = core.store.claim_ready_workflow_task("p", "task-worker", max_attempts=2)
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "p", attempt_id, provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(attempt_id)
    core.store.create(attempt_id)
    tool_id = capability_id.removeprefix("tool.")
    assert core.store.set_started(attempt_id, tool_id, "192.0.2.10")
    if job_status == "finished":
        assert core.store.set_finished(attempt_id, exit_code, 0.25)
    else:
        core.store.set_failed(attempt_id, "provider failure")
    core.store.finish_task_attempt(
        attempt_id, "uncertain", error="worker lost after provider completion",
    )
    assert core.workflow_requests.finish(
        request["id"], run_claim["lease_token"], status="uncertain",
        error="worker lost after claim",
    )
    return core, request, attempt_id


def test_recovery_seals_successful_job_and_never_replays(tmp_path):
    core, request, attempt_id = _uncertain_catalog_attempt(tmp_path)

    recovered = core.recover_workflow_attempt_from_provider_job("p", attempt_id)

    assert recovered["task_status"] == "succeeded"
    assert recovered["provider_execution_id"] == attempt_id
    assert recovered["automatic_replay"] is False
    assert recovered["run_requests_closed"] == 1
    assert core.workflow_run_request(request["id"])["status"] == "incomplete"
    assert core.store.get_workflow_attempt_status(attempt_id) == "succeeded"
    assert core.workflow_evidence("p")["attempts"][0]["integrity_status"] == "verified"
    audit = core.store.get_workflow_audit_integrity("p")
    assert audit["consistent"] is True, audit
    assert core.workflow_requests.claim("worker") is None
    with pytest.raises(ValueError, match="only uncertain"):
        core.recover_workflow_attempt_from_provider_job("p", attempt_id)


def test_recovery_supports_first_party_provider_capabilities(tmp_path):
    capability_id = "recon.http"
    core, _, attempt_id = _uncertain_catalog_attempt(
        tmp_path, capability_id=capability_id,
    )

    recovered = core.recover_workflow_attempt_from_provider_job("p", attempt_id)

    assert recovered["task_status"] == "succeeded"
    assert core.workflow_evidence("p")["attempts"][0]["integrity_status"] == "verified"
    audit = core.store.get_workflow_audit_integrity("p")
    assert audit["consistent"] is True, audit


@pytest.mark.parametrize(("job_status", "exit_code"), [
    ("running", 0), ("failed", 1),
])
def test_recovery_refuses_incomplete_provider_results(
    tmp_path, job_status, exit_code,
):
    core, _, attempt_id = _uncertain_catalog_attempt(
        tmp_path, job_status=job_status, exit_code=exit_code,
    )
    with pytest.raises(ValueError, match="no matching successful durable"):
        core.recover_workflow_attempt_from_provider_job("p", attempt_id)
    assert core.store.get_workflow_attempt_status(attempt_id) == "uncertain"
    assert core.store.get_workflow_audit_integrity("p")["consistent"] is True


@pytest.mark.parametrize("tamper", ["tool", "target", "ownership"])
def test_recovery_fails_closed_on_provider_identity_mismatch(tmp_path, tamper):
    core, _, attempt_id = _uncertain_catalog_attempt(tmp_path)
    conn = core.store._conn()
    try:
        if tamper == "tool":
            conn.execute("UPDATE jobs SET tool='nikto' WHERE id=?", (attempt_id,))
        elif tamper == "target":
            conn.execute("UPDATE jobs SET target='198.51.100.8' WHERE id=?", (attempt_id,))
        else:
            conn.execute(
                "DELETE FROM engine_v2_execution_jobs WHERE job_id=?", (attempt_id,),
            )
    finally:
        conn.close()
    with pytest.raises(ValueError, match="no matching successful durable"):
        core.recover_workflow_attempt_from_provider_job("p", attempt_id)
    assert core.store.get_workflow_attempt_status(attempt_id) == "uncertain"


def test_cancelled_plan_cannot_recover_successful_provider_effect(tmp_path):
    core, _, attempt_id = _uncertain_catalog_attempt(tmp_path)
    core.cancel_workflow_plan("p")
    with pytest.raises(ValueError, match="cancelled workflows"):
        core.recover_workflow_attempt_from_provider_job("p", attempt_id)
    assert core.store.get_workflow_attempt_status(attempt_id) == "uncertain"


def test_recovery_rejects_changed_provider_output_after_recovery(tmp_path):
    core, _, attempt_id = _uncertain_catalog_attempt(tmp_path)
    core.recover_workflow_attempt_from_provider_job("p", attempt_id)
    with core.store._lock:
        conn = core.store._conn()
        try:
            conn.execute(
                "UPDATE jobs SET target='198.51.100.8' WHERE id=?", (attempt_id,),
            )
        finally:
            conn.close()
    audit = core.store.get_workflow_audit_integrity("p")
    assert audit["consistent"] is False
    assert attempt_id in audit["mismatched_recovery_events"]


def test_recovery_api_does_not_accept_caller_supplied_results(tmp_path):
    from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app

    core, _, attempt_id = _uncertain_catalog_attempt(tmp_path)
    client = create_app(core, JobRegistry(core), AsyncRunner(core)).test_client()
    accepted = client.post("/api/v2/workflows/p/reconcile", json={
        "attempt_id": attempt_id, "recover_provider_result": True,
    })
    assert accepted.status_code == 200
    assert accepted.get_json()["automatic_replay"] is False

    rejected = client.post("/api/v2/workflows/p/reconcile", json={
        "attempt_id": attempt_id, "recover_provider_result": True,
        "result": {"status": "success"},
    })
    assert rejected.status_code == 400
