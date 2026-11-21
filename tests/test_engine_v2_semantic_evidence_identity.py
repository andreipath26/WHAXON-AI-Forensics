"""Semantic capability identities seal against their persisted catalog tool jobs."""
from __future__ import annotations

from whaxon.core import Core
from whaxon.core.provider_execution import (
    SEMANTIC_OPERATION_TO_TOOL,
    provider_tool_id_for_capability,
)
from whaxon.core.providers import SEMANTIC_OPERATION_IDS
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def test_semantic_operation_map_is_the_provider_tool_identity_contract():
    assert {
        tool_id: capability_id
        for capability_id, tool_id in SEMANTIC_OPERATION_TO_TOOL.items()
    } == SEMANTIC_OPERATION_IDS
    assert all(
        provider_tool_id_for_capability(capability_id) == tool_id
        for capability_id, tool_id in SEMANTIC_OPERATION_TO_TOOL.items()
    )
    assert provider_tool_id_for_capability("tool.nmap") == "nmap"
    assert provider_tool_id_for_capability("recon.http") == "recon.http"


def test_semantic_catalog_workflow_job_is_sealed_and_reportable(tmp_path):
    core = Core(tmp_path)
    core.create_mission("semantic", "seal semantic capability evidence")
    core.save_workflow_plan("semantic-plan", WorkflowPlan("semantic", (
        WorkflowTask(
            "scan", "network.services.discover", "192.0.2.10",
            permissions=("network.scan",), impact="moderate",
        ),
    )))
    claim = core.store.claim_ready_workflow_task(
        "semantic-plan", "test-worker", max_attempts=1,
    )
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "semantic-plan", attempt_id, provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(attempt_id)
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 0, 0.25)

    core.store.finish_task_attempt(attempt_id, "succeeded", result={
        "job_id": attempt_id,
        "tool_id": "nmap",
        "target": "192.0.2.10",
        "exit_code": 0,
        "findings": [],
    })

    assert core.store.has_valid_workflow_evidence_seal(attempt_id) is True
    evidence = core.workflow_evidence("semantic-plan")
    assert evidence["attempts"][0]["evidence_status"] == "recorded"
    assert evidence["attempts"][0]["integrity_status"] == "verified"
    assert core.store.get_workflow_audit_integrity("semantic-plan")["consistent"] is True


def test_semantic_provider_recovery_reuses_exact_catalog_tool_identity(tmp_path):
    core = Core(tmp_path)
    core.create_mission("semantic-recovery", "recover semantic provider result")
    core.save_workflow_plan("semantic-recovery-plan", WorkflowPlan("semantic-recovery", (
        WorkflowTask(
            "scan", "network.services.discover", "192.0.2.10",
            permissions=("network.scan",), impact="moderate",
        ),
    )))
    request = core.enqueue_workflow_run("semantic-recovery-plan")
    run_claim = core.workflow_requests.claim("run-worker")
    assert run_claim and run_claim["id"] == request["id"]
    claim = core.store.claim_ready_workflow_task(
        "semantic-recovery-plan", "task-worker", max_attempts=1,
    )
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "semantic-recovery-plan", attempt_id,
        provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(attempt_id)
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 0, 0.25)
    core.store.finish_task_attempt(
        attempt_id, "uncertain", error="worker lost after provider completion",
    )
    assert core.workflow_requests.finish(
        request["id"], run_claim["lease_token"], status="uncertain",
        error="worker lost after claim",
    )

    reconciliation = core.workflow_dispatch_reconciliation("semantic-recovery-plan")
    assert reconciliation[0]["provider_job"]["tool"] == "nmap"
    result = core.recover_workflow_attempt_from_provider_job(
        "semantic-recovery-plan", attempt_id,
    )

    assert result["task_status"] == "succeeded"
    evidence = core.workflow_evidence("semantic-recovery-plan")
    assert evidence["attempts"][0]["integrity_status"] == "verified"
    assert core.store.get_workflow_audit_integrity(
        "semantic-recovery-plan",
    )["consistent"] is True
