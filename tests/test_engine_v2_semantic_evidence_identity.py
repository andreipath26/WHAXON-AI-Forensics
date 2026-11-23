"""Semantic capability identities seal against their persisted catalog tool jobs."""
from __future__ import annotations

from whaxon.core import Core
from whaxon.core.provider_execution import (
    SEMANTIC_OPERATION_TO_TOOL,
    provider_tool_id_for_capability,
)
from whaxon.core.providers import SEMANTIC_OPERATION_IDS
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def _provider_metadata(manifest):
    return {"provider_bindings": {"scan": {
        "provider_id": manifest.provider_id,
        "provider_version": manifest.provider_version,
        "manifest_fingerprint": manifest.fingerprint,
    }}}


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
    manifest = core.providers.manifest_for("network.services.discover")
    core.save_workflow_plan("semantic-plan", WorkflowPlan("semantic", (
        WorkflowTask(
            "scan", "network.services.discover", "192.0.2.10",
            permissions=("network.scan",), impact="moderate",
        ),
    ), metadata=_provider_metadata(manifest)))
    claim = core.store.claim_ready_workflow_task(
        "semantic-plan", "test-worker", max_attempts=1,
    )
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "semantic-plan", attempt_id, provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(
        attempt_id, manifest,
    )
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 0, 0.25)
    conn = core.store._conn()
    try:
        conn.execute(
            "INSERT INTO findings (job_id, seq, kind, severity, source, data_json, "
            "raw_line, enrichment_json) VALUES (?, 0, 'open_port', 'info', 'nmap', ?, ?, ?)",
            (attempt_id, '{"port":443,"protocol":"tcp"}', "443/tcp open https", "{}"),
        )
    finally:
        conn.close()
    assert core.store.seal_engine_v2_provider_result(attempt_id)

    core.store.finish_task_attempt(attempt_id, "succeeded", result={
        "job_id": attempt_id,
        "tool_id": "nmap",
        "target": "192.0.2.10",
        "provider_id": core.providers.manifest_for("network.services.discover").provider_id,
        "provider_version": core.providers.manifest_for("network.services.discover").provider_version,
        "manifest_fingerprint": core.providers.manifest_for("network.services.discover").fingerprint,
        "exit_code": 0,
        "findings": [],
    })

    assert core.store.has_valid_workflow_evidence_seal(attempt_id) is True
    evidence = core.workflow_evidence("semantic-plan")
    assert evidence["attempts"][0]["evidence_status"] == "recorded"
    assert evidence["attempts"][0]["integrity_status"] == "verified"
    assert core.store.get_workflow_audit_integrity("semantic-plan")["consistent"] is True


def test_success_terminalization_rejects_provider_output_changed_after_completion(tmp_path):
    core = Core(tmp_path)
    core.create_mission("semantic-mutated", "reject output changed after provider completion")
    manifest = core.providers.manifest_for("network.services.discover")
    core.save_workflow_plan("semantic-mutated-plan", WorkflowPlan("semantic-mutated", (
        WorkflowTask(
            "scan", "network.services.discover", "192.0.2.10",
            permissions=manifest.permissions, impact=manifest.impact,
        ),
    ), metadata=_provider_metadata(manifest)))
    claim = core.store.claim_ready_workflow_task(
        "semantic-mutated-plan", "test-worker", max_attempts=1,
    )
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "semantic-mutated-plan", attempt_id, provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(attempt_id, manifest)
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 0, 0.25)
    assert core.store.seal_engine_v2_provider_result(attempt_id)

    conn = core.store._conn()
    try:
        conn.execute(
            "INSERT INTO findings (job_id, seq, kind, severity, source, data_json, "
            "raw_line, enrichment_json) VALUES (?, 0, 'open_port', 'info', 'nmap', ?, ?, ?)",
            (attempt_id, '{"port":80,"protocol":"tcp"}', "80/tcp open http", "{}"),
        )
    finally:
        conn.close()

    core.store.finish_task_attempt(attempt_id, "succeeded", result={
        "job_id": attempt_id, "tool_id": "nmap", "target": "192.0.2.10",
        "exit_code": 0, "findings": [],
        "provider_id": manifest.provider_id,
        "provider_version": manifest.provider_version,
        "manifest_fingerprint": manifest.fingerprint,
    })

    assert core.store.get_workflow_attempt_status(attempt_id) == "uncertain"
    assert core.store.has_valid_workflow_evidence_seal(attempt_id) is False
    assert core.store.get_workflow_audit_integrity("semantic-mutated-plan")["consistent"] is True


def test_success_terminalization_rejects_nonzero_durable_provider_exit(tmp_path):
    core = Core(tmp_path)
    core.create_mission("semantic-nonzero", "reject a nonzero provider job as success")
    manifest = core.providers.manifest_for("network.services.discover")
    core.save_workflow_plan("semantic-nonzero-plan", WorkflowPlan(
        "semantic-nonzero", (
            WorkflowTask(
                "scan", "network.services.discover", "192.0.2.10",
                permissions=manifest.permissions, impact=manifest.impact,
            ),
        ), metadata=_provider_metadata(manifest),
    ))
    claim = core.store.claim_ready_workflow_task(
        "semantic-nonzero-plan", "test-worker", max_attempts=1,
    )
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "semantic-nonzero-plan", attempt_id, provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(attempt_id, manifest)
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 2, 0.25)
    assert core.store.seal_engine_v2_provider_result(attempt_id)

    core.store.finish_task_attempt(attempt_id, "succeeded", result={
        "job_id": attempt_id, "tool_id": "nmap", "target": "192.0.2.10",
        "exit_code": 0, "findings": [],
        "provider_id": manifest.provider_id,
        "provider_version": manifest.provider_version,
        "manifest_fingerprint": manifest.fingerprint,
    })

    assert core.store.get_workflow_attempt_status(attempt_id) == "uncertain"
    assert core.store.has_valid_workflow_evidence_seal(attempt_id) is False


def test_semantic_provider_recovery_reuses_exact_catalog_tool_identity(tmp_path):
    core = Core(tmp_path)
    core.create_mission("semantic-recovery", "recover semantic provider result")
    manifest = core.providers.manifest_for("network.services.discover")
    core.save_workflow_plan("semantic-recovery-plan", WorkflowPlan("semantic-recovery", (
        WorkflowTask(
            "scan", "network.services.discover", "192.0.2.10",
            permissions=("network.scan",), impact="moderate",
        ),
    ), metadata=_provider_metadata(manifest)))
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
    core.store.mark_engine_v2_execution_job(
        attempt_id, manifest,
    )
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 0, 0.25)
    assert core.store.seal_engine_v2_provider_result(attempt_id)
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



def test_semantic_provider_recovery_preserves_nonzero_exit_as_failure(tmp_path):
    core = Core(tmp_path)
    core.create_mission("semantic-failure", "recover failed provider result")
    manifest = core.providers.manifest_for("network.services.discover")
    core.save_workflow_plan("semantic-failure-plan", WorkflowPlan("semantic-failure", (
        WorkflowTask(
            "scan", "network.services.discover", "192.0.2.10",
            permissions=("network.scan",), impact="moderate",
        ),
    ), metadata=_provider_metadata(manifest)))
    claim = core.store.claim_ready_workflow_task(
        "semantic-failure-plan", "task-worker", max_attempts=1,
    )
    assert claim is not None
    attempt_id = claim["attempt_id"]
    assert core.store.mark_workflow_dispatch_started(
        "semantic-failure-plan", attempt_id,
        provider_execution_id=attempt_id,
    )
    core.store.mark_engine_v2_execution_job(
        attempt_id, manifest,
    )
    core.store.create(attempt_id)
    assert core.store.set_started(attempt_id, "nmap", "192.0.2.10")
    assert core.store.set_finished(attempt_id, 2, 0.25)
    assert core.store.seal_engine_v2_provider_result(attempt_id)
    core.store.finish_task_attempt(
        attempt_id, "uncertain", error="worker lost after provider completion",
    )

    result = core.recover_workflow_attempt_from_provider_job(
        "semantic-failure-plan", attempt_id,
    )

    assert result["task_status"] == "failed"
    assert result["provider_exit_code"] == 2
    snapshot = core.store.get_workflow_progress("semantic-failure-plan")
    assert snapshot["counts"] == {"failed": 1}
    evidence = core.workflow_evidence("semantic-failure-plan")
    assert evidence["attempts"][0]["evidence_status"] == "recorded"
    assert evidence["attempts"][0]["provider_exit_code"] == 2
    assert evidence["attempts"][0]["integrity_status"] == "verified"
    assert core.store.get_workflow_audit_integrity(
        "semantic-failure-plan",
    )["consistent"] is True
