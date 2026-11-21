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
    assert SEMANTIC_OPERATION_IDS == {
        tool_id: capability_id
        for capability_id, tool_id in SEMANTIC_OPERATION_TO_TOOL.items()
    }
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
