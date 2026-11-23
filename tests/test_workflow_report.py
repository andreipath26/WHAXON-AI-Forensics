from __future__ import annotations

import json

from whaxon.core import Core


def _evidence(*, status="recorded", integrity="verified", attempt_status="succeeded"):
    return {
        "plan_id": "plan-1", "mission_id": "mission-1", "plan_digest": "digest-1",
        "attempts": [{
            "task_key": "verify", "target": "http://127.0.0.1:8000/item?q=x",
            "capability_id": "tool.verify_xss", "attempt_id": "attempt-1",
            "attempt_no": 1, "attempt_status": attempt_status,
            "job_id": "123456789abc", "evidence_status": status,
            "integrity_status": integrity, "finding_count": 1,
            "findings": [{"seq": 0, "kind": "xss", "severity": "high"}],
        }],
        "all_evidence_recorded": status == "recorded",
        "all_evidence_integrity_verified": integrity == "verified",
    }


def _core_with(evidence, *, ready=True, persisted_attempts=None):
    core = Core.__new__(Core)
    core.workflow_evidence = lambda plan_id, limit=100: evidence
    core.workflow_readiness = lambda plan_id: {
        "plan_id": plan_id, "ready_to_report_success": ready,
        "complete": ready, "all_succeeded": ready, "blockers": [],
    }
    core.workflow_progress = lambda plan_id: {
        "plan_id": plan_id,
        "attempts": persisted_attempts if persisted_attempts is not None
        else len(evidence["attempts"]),
        "total_tasks": 1,
        "complete": True,
        "cancellation_requested": False,
        "counts": {"succeeded": 1} if ready else {"failed": 1},
    }
    return core


def test_core_workflow_report_uses_only_sealed_plan_evidence():
    report = Core.workflow_report(_core_with(_evidence()), "plan-1")
    assert report["schema_version"] == "whaxon.workflow-report.v1"
    assert report["status"] == "complete"
    assert report["summary"] == {
        "planned_tasks": 1, "task_status_counts": {"succeeded": 1},
        "pending_tasks": 0,
        "task_attempts": 1, "recorded_attempts": 1,
        "verified_seals": 1, "findings": 1,
    }
    assert report["coverage"]["completeness_claim"] is False
    assert report["coverage"]["persisted_attempts"] == 1
    assert report["coverage"]["unsupported_or_inaccessible_work"] == {
        "status": "not_recorded", "count": None, "items": [],
    }
    assert report["findings"][0]["job_id"] == "123456789abc"
    assert report["findings"][0]["target"].startswith("http://127.0.0.1")


def test_core_workflow_report_flags_failed_or_unsealed_evidence_partial():
    for evidence in (
        _evidence(status="unavailable", integrity="unsealed", attempt_status="failed"),
        _evidence(status="integrity_mismatch", integrity="changed"),
    ):
        report = Core.workflow_report(_core_with(evidence), "plan-1")
        assert report["status"] == "partial"
        assert report["findings"] == []


def test_core_workflow_report_flags_incomplete_plan_partial():
    report = Core.workflow_report(_core_with(_evidence(), ready=False), "plan-1")
    assert report["status"] == "partial"


def test_core_workflow_report_surfaces_pending_and_uncertain_tasks():
    core = _core_with(_evidence(), ready=False)
    core.workflow_progress = lambda _plan_id: {
        "plan_id": "plan-1", "attempts": 2, "total_tasks": 4,
        "counts": {"succeeded": 1, "pending": 2, "uncertain": 1},
    }

    report = Core.workflow_report(core, "plan-1")

    assert report["status"] == "partial"
    assert report["summary"]["planned_tasks"] == 4
    assert report["summary"]["pending_tasks"] == 2
    assert report["summary"]["task_status_counts"] == {
        "succeeded": 1, "pending": 2, "uncertain": 1,
    }


def test_core_workflow_report_flags_truncated_attempt_history():
    report = Core.workflow_report(
        _core_with(_evidence(), persisted_attempts=2), "plan-1", limit=1,
    )
    assert report["status"] == "partial"
    assert report["truncated"] is True


def test_core_workflow_report_refuses_stale_readiness_after_cancellation():
    core = _core_with(_evidence(), ready=True)
    core.workflow_progress = lambda _plan_id: {
        "plan_id": "plan-1", "attempts": 1, "total_tasks": 1,
        "complete": True, "cancellation_requested": True,
        "counts": {"succeeded": 1},
    }

    report = Core.workflow_report(core, "plan-1")

    assert report["status"] == "partial"
    assert report["readiness"]["ready_to_report_success"] is True


def test_core_workflow_report_refuses_inconsistent_terminal_counts():
    core = _core_with(_evidence(), ready=True)
    core.workflow_progress = lambda _plan_id: {
        "plan_id": "plan-1", "attempts": 1, "total_tasks": 1,
        "complete": True, "cancellation_requested": False,
        "counts": {"succeeded": 0, "failed": 1},
    }

    report = Core.workflow_report(core, "plan-1")

    assert report["status"] == "partial"


def test_core_workflow_report_honors_evidence_snapshot_truncation_flag():
    evidence = _evidence()
    evidence["truncated"] = True
    core = _core_with(evidence, ready=True, persisted_attempts=1)

    report = Core.workflow_report(core, "plan-1")

    assert report["truncated"] is True
    assert report["coverage"]["attempt_history_truncated"] is True
    assert report["status"] == "partial"


def test_plan_report_cli_prints_json_and_returns_failure_for_partial(monkeypatch, capsys):
    from whaxon.interfaces.cli import workflow_cmd

    class FakeCore:
        def __init__(self, data_dir):
            self.report = {
                "schema_version": "whaxon.workflow-report.v1",
                "plan_id": "plan-1", "status": "partial", "findings": [],
            }

        def workflow_report(self, plan_id, *, limit):
            assert (plan_id, limit) == ("plan-1", 20)
            return self.report

    monkeypatch.setattr(workflow_cmd, "Core", FakeCore)
    result = workflow_cmd.main(["--data-dir", ".", "plan", "report", "--id", "plan-1", "--limit", "20"])
    assert result == 1
    assert json.loads(capsys.readouterr().out)["status"] == "partial"



def test_workflow_report_projects_failed_attempt_without_raw_error(tmp_path):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "workflow-report.db")
    store.create_mission("report-mission", "report failure safely")
    store.save_workflow_plan(
        "report-plan",
        WorkflowPlan("report-mission", (
            WorkflowTask("scan", "tool.nmap", "192.0.2.10"),
        )),
    )
    claim = store.claim_ready_workflow_task("report-plan", "report-test-worker")
    assert claim is not None
    secret = "credential=do-not-report-this"
    store.finish_task_attempt(
        claim["attempt_id"], "failed",
        error=f"RuntimeError: provider response contained {secret}",
    )

    core = Core.__new__(Core)
    core.workflow_evidence = lambda plan_id, limit=100: store.get_workflow_evidence(
        plan_id, limit=limit,
    )
    core.workflow_readiness = store.get_workflow_readiness
    core.workflow_progress = store.get_workflow_progress

    report = Core.workflow_report(core, "report-plan")
    attempt = report["evidence"]["attempts"][0]
    assert report["status"] == "partial"
    assert attempt["attempt_status"] == "failed"
    assert attempt["attempt_error_category"] == "task_failed"
    rendered = json.dumps(report)
    assert secret not in rendered
    assert "provider response contained" not in rendered


def test_workflow_report_inputs_share_one_sqlite_snapshot(tmp_path, monkeypatch):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "workflow-report-snapshot.db")
    store.create_mission("snapshot-mission", "pin report reads")
    store.save_workflow_plan("snapshot-plan", WorkflowPlan("snapshot-mission", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    original_progress = store._get_workflow_progress_tx
    cancellation_committed = False

    def cancel_after_evidence_snapshot(conn, plan_id):
        nonlocal cancellation_committed
        store.request_workflow_cancellation(plan_id)
        cancellation_committed = True
        return original_progress(conn, plan_id)

    monkeypatch.setattr(
        store, "_get_workflow_progress_tx", cancel_after_evidence_snapshot,
    )
    snapshot = store.get_workflow_report_snapshot("snapshot-plan")

    assert cancellation_committed is True
    assert snapshot["progress"]["cancellation_requested"] is False
    assert snapshot["readiness"]["blockers"] == []
    assert snapshot["tasks"][0]["status"] == "pending"
    assert store.get_workflow_progress("snapshot-plan")["cancellation_requested"] is True


def test_core_report_uses_store_report_snapshot_when_available(tmp_path):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "workflow-report-core-snapshot.db")
    store.create_mission("snapshot-mission", "core report snapshot")
    store.save_workflow_plan("snapshot-plan", WorkflowPlan("snapshot-mission", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    core = Core.__new__(Core)
    core.store = store

    report = Core.workflow_report(core, "snapshot-plan")

    assert report["status"] == "partial"
    assert report["summary"]["planned_tasks"] == 1
    assert report["summary"]["task_status_counts"] == {"pending": 1}



def test_workflow_report_projects_scope_skip_without_raw_coverage_details(tmp_path):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "workflow-skip-report.db")
    store.create_mission("skip-mission", "report skipped coverage")
    target = "192.0.2.11"
    store.save_workflow_plan(
        "skip-plan",
        WorkflowPlan("skip-mission", (
            WorkflowTask("scan", "tool.nmap", target),
        )),
    )
    claim = store.claim_ready_workflow_task("skip-plan", "skip-report-worker")
    assert claim is not None
    attempt_id = claim["attempt_id"]
    store.mark_workflow_dispatch_started(
        "skip-plan", attempt_id, provider_execution_id=attempt_id,
    )
    secret_detail = f"scope denial included private context for {target}"
    store.record_coverage(
        attempt_id, "nmap", target, "scope_blocked", secret_detail, phase="workflow",
    )
    store.finish_task_attempt(
        attempt_id, "uncertain",
        error="provider outcome unknown after dispatch: OutOfScopeError; reconcile before retry",
    )

    core = Core.__new__(Core)
    core.workflow_evidence = lambda plan_id, limit=100: store.get_workflow_evidence(
        plan_id, limit=limit,
    )
    core.workflow_readiness = store.get_workflow_readiness
    core.workflow_progress = store.get_workflow_progress

    report = Core.workflow_report(core, "skip-plan")
    attempt = report["evidence"]["attempts"][0]
    assert attempt["attempt_status"] == "uncertain"
    assert attempt["attempt_error_category"] == "provider_outcome_uncertain"
    assert attempt["coverage_outcomes"] == [{
        "status": "skipped", "kind": "scope_blocked", "phase": "workflow",
    }]
    rendered = json.dumps(report)
    assert secret_detail not in rendered
    assert "private context" not in rendered
    assert "target" not in attempt["coverage_outcomes"][0]
    assert report["coverage"]["recorded_skips"] == {"scope_blocked": 1}
    assert report["coverage"]["attempt_history_truncated"] is False


def test_workflow_report_projects_plan_bound_unsupported_and_unavailable_checks(tmp_path):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    store = JobStore(tmp_path / "workflow-report-omissions.db")
    store.create_mission("omissions-mission", "report omitted checks")
    plan = WorkflowPlan("omissions-mission", (
        WorkflowTask("scan", "tool.nmap", "192.0.2.12"),
    ), metadata={
        "proposal_type": "passive_recon",
        "requested_checks": ["dns", "cookies", "tech"],
        "included_checks": ["dns"],
        "omitted_checks": [
            {"check": "cookies", "reason": "legacy only", "disposition": "unsupported"},
            {"check": "dns_full", "reason": "provider not ready", "disposition": "provider_unavailable"},
                {"check": "tech", "reason": "legacy-only; no admitted V2 provider"},
                {"check": "secret", "reason": "untyped provider note"},
        ],
    })
    store.save_workflow_plan("omissions-plan", plan)

    core = Core.__new__(Core)
    core.store = store
    core.workflow_evidence = lambda plan_id, limit=100: store.get_workflow_evidence(
        plan_id, limit=limit,
    )
    core.workflow_plan_details = lambda plan_id: {
        "plan": store.get_workflow_plan(plan_id)["plan"],
        "tasks": store.list_workflow_tasks(plan_id),
    }
    core.workflow_readiness = store.get_workflow_readiness
    core.workflow_progress = store.get_workflow_progress

    report = Core.workflow_report(core, "omissions-plan")

    assert report["coverage"]["unsupported_or_inaccessible_work"] == {
        "status": "recorded",
        "count": 3,
        "items": [
            {"check": "cookies", "disposition": "unsupported"},
            {"check": "dns_full", "disposition": "provider_unavailable"},
            {"check": "tech", "disposition": "unsupported"},
        ],
    }
    assert report["coverage"]["requested_checks"] == ["dns", "cookies", "tech"]
    assert report["coverage"]["included_checks"] == ["dns"]
    assert report["coverage"]["unrequested_checks"] == [
        "dns_full", "ssl", "https", "headers", "redirects", "robots",
        "security_txt", "waf",
    ]

    # The report must not trust a changed omission list that no longer matches
    # the immutable plan digest stored with the workflow evidence.
    with store._conn() as connection:
        raw_plan = connection.execute(
            "SELECT plan_json FROM workflow_plans WHERE id=?", ("omissions-plan",),
        ).fetchone()["plan_json"]
        changed_plan = json.loads(raw_plan)
        changed_plan["metadata"]["omitted_checks"].append({
            "check": "forged", "disposition": "unsupported",
        })
        connection.execute(
            "UPDATE workflow_plans SET plan_json=? WHERE id=?",
            (json.dumps(changed_plan), "omissions-plan"),
        )
    changed_report = Core.workflow_report(core, "omissions-plan")
    assert changed_report["coverage"]["unrequested_checks"] is None
    assert changed_report["coverage"]["unsupported_or_inaccessible_work"] == {
        "status": "not_recorded", "count": None, "items": [],
    }



def test_workflow_report_derives_finding_verification_outcomes_from_plan_tasks():
    class TaskStore:
        def __init__(self, tasks):
            self.tasks = tasks

        def list_workflow_tasks(self, plan_id):
            assert plan_id == "plan-1"
            return self.tasks

    source_job = "123456789abc"
    source_finding = {"seq": 0, "kind": "sqli", "severity": "high"}
    scan_attempt = {
        "task_key": "scan", "target": "http://127.0.0.1/item?id=1",
        "capability_id": "tool.sqlmap", "attempt_id": "scan-attempt",
        "attempt_no": 1, "attempt_status": "succeeded",
        "job_id": source_job, "evidence_status": "recorded",
        "integrity_status": "verified", "finding_count": 1,
        "findings": [source_finding],
    }

    def make_report(tasks, extra_attempts=()):
        report_attempts = [scan_attempt, *extra_attempts]
        evidence = {
            "plan_id": "plan-1", "mission_id": "mission-1",
            "plan_digest": "digest-1",
            "attempts": report_attempts,
            "all_evidence_recorded": all(
                attempt.get("evidence_status") == "recorded"
                for attempt in report_attempts
            ),
            "all_evidence_integrity_verified": all(
                attempt.get("integrity_status") == "verified"
                for attempt in report_attempts
            ),
        }
        core = _core_with(evidence, ready=False)
        core.store = TaskStore(tasks)
        def task_counts():
            counts = {}
            for task in tasks:
                status = task.get("status")
                counts[status] = counts.get(status, 0) + 1
            return counts
        core.workflow_progress = lambda _plan_id: {
            "plan_id": "plan-1", "attempts": len(evidence["attempts"]),
            "total_tasks": len(tasks),
            "counts": task_counts(),
        }
        return Core.workflow_report(core, "plan-1")

    scan_task = {
        "id": "scan", "capability_id": "tool.sqlmap", "status": "succeeded",
        "inputs": {},
    }
    verify_task = {
        "id": "verify", "capability_id": "tool.verify_sqli",
        "inputs": {"source_job_id": source_job, "finding_seq": 0},
    }

    not_requested = make_report([scan_task])
    assert not_requested["findings"][0]["verification_outcome"] == {
        "status": "not_requested",
    }
    assert not_requested["coverage"]["unrequested_verification_findings"] == 1
    assert not_requested["coverage"]["finding_verification_outcomes"] == {
        "not_requested": 1,
    }

    pending = make_report([scan_task, {**verify_task, "status": "pending"}])
    assert pending["findings"][0]["verification_outcome"] == {
        "status": "pending", "task_key": "verify",
    }

    failed_attempt = {
        "task_key": "verify", "attempt_status": "failed",
        "evidence_status": "not_successful", "integrity_status": "unsealed",
        "findings": [],
    }
    failed = make_report(
        [scan_task, {**verify_task, "status": "failed"}], [failed_attempt],
    )
    assert failed["findings"][0]["verification_outcome"] == {
        "status": "failed", "task_key": "verify",
        "attempt_statuses": ["failed"],
    }

    recorded_attempt = {
        "task_key": "verify", "target": "http://127.0.0.1/item?id=1",
        "capability_id": "tool.verify_sqli", "attempt_id": "verify-attempt",
        "attempt_no": 1, "attempt_status": "succeeded",
        "job_id": "abcdef123456", "evidence_status": "recorded",
        "integrity_status": "verified", "finding_count": 1,
        "findings": [{
            "seq": 0, "kind": "sqli", "severity": "high",
            "source": "engine-v2-verifier",
            "verification_status": "verified",
            "source_observation": {"job_id": source_job, "finding_seq": 0},
        }],
    }
    recorded = make_report(
        [scan_task, {**verify_task, "status": "succeeded"}], [recorded_attempt],
    )
    assert recorded["findings"][0]["verification_outcome"] == {
        "status": "recorded", "task_key": "verify",
        "attempt_statuses": ["succeeded"],
        "verification_status": "verified", "job_id": "abcdef123456",
    }
    assert recorded["findings"][1]["verification_outcome"] == {
        "status": "recorded", "verification_status": "verified",
        "job_id": "abcdef123456",
    }
    assert "source_job_id" not in json.dumps(recorded)
    assert "source_finding_seq" not in json.dumps(recorded)


def _declared_coverage_report(
    tmp_path, contract, *, stale_digest=False, extra_metadata=None,
):
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    tmp_path.mkdir(parents=True, exist_ok=True)
    store = JobStore(tmp_path / "declared-coverage.db")
    store.create_mission("mission-1", "declared coverage test")
    metadata = {"coverage_contract": contract}
    metadata.update(extra_metadata or {})
    plan = WorkflowPlan(
        "mission-1",
        (WorkflowTask("scan", "tool.nmap", "192.0.2.10"),),
        metadata=metadata,
    )
    store.save_workflow_plan("declared-plan", plan)
    evidence = _evidence()
    evidence["plan_id"] = "declared-plan"
    evidence["mission_id"] = "mission-1"
    evidence["plan_digest"] = "stale-digest" if stale_digest else plan.digest
    core = _core_with(evidence)
    core.workflow_plan_details = lambda _plan_id: {
        "plan": store.get_workflow_plan("declared-plan")["plan"],
    }
    return Core.workflow_report(core, "declared-plan")


def test_workflow_report_projects_digest_bound_generic_declared_coverage(tmp_path):
    contract = {
        "schema_version": 1,
        "checklist": ["dns", "http", "tls", "headers"],
        "requested": ["dns", "http", "tls"],
        "included": ["dns"],
        "dispositions": [
            {"check_id": "http", "disposition": "provider_unavailable"},
            {"check_id": "tls", "disposition": "inaccessible"},
        ],
    }

    report = _declared_coverage_report(tmp_path, contract)

    assert report["coverage"]["declared_coverage"] == {
        "status": "recorded",
        "schema_version": 1,
        "checklist": ["dns", "http", "tls", "headers"],
        "requested": ["dns", "http", "tls"],
        "included": ["dns"],
        "unrequested": ["headers"],
        "omissions": [
            {"check_id": "http", "disposition": "provider_unavailable"},
            {"check_id": "tls", "disposition": "inaccessible"},
        ],
    }
    assert report["coverage"]["completeness_claim"] is False
    assert report["status"] == "complete"


def test_workflow_report_fails_closed_on_invalid_declared_coverage(tmp_path):
    from copy import deepcopy

    valid = {
        "schema_version": 1,
        "checklist": ["dns", "http"],
        "requested": ["dns", "http"],
        "included": ["dns"],
        "dispositions": [{"check_id": "http", "disposition": "unsupported"}],
    }
    invalid_contracts = []
    duplicate = deepcopy(valid)
    duplicate["checklist"].append("dns")
    invalid_contracts.append(duplicate)
    outside_requested = deepcopy(valid)
    outside_requested["included"] = ["dns", "elsewhere"]
    invalid_contracts.append(outside_requested)
    missing_omission = deepcopy(valid)
    missing_omission["dispositions"] = []
    invalid_contracts.append(missing_omission)
    unknown_disposition = deepcopy(valid)
    unknown_disposition["dispositions"][0]["disposition"] = "timeout"
    invalid_contracts.append(unknown_disposition)
    unknown_field = deepcopy(valid)
    unknown_field["dispositions"][0]["reason"] = "private provider detail"
    invalid_contracts.append(unknown_field)
    invalid_contracts.append({
        "schema_version": 1,
        "checklist": ["x"] * 257,
        "requested": ["x"],
        "included": [],
        "dispositions": [{"check_id": "x", "disposition": "unsupported"}],
    })

    for index, contract in enumerate(invalid_contracts):
        report = _declared_coverage_report(tmp_path / str(index), contract)
        declared = report["coverage"]["declared_coverage"]
        assert declared["status"] == "invalid"
        assert declared["checklist"] == []
        assert declared["requested"] == []
        assert declared["included"] == []
        assert declared["unrequested"] == []
        assert declared["omissions"] == []
        assert report["coverage"]["completeness_claim"] is False


def test_workflow_report_suppresses_declared_coverage_on_digest_mismatch(tmp_path):
    contract = {
        "schema_version": 1,
        "checklist": ["dns", "http"],
        "requested": ["dns"],
        "included": ["dns"],
        "dispositions": [],
    }

    report = _declared_coverage_report(tmp_path, contract, stale_digest=True)

    assert report["coverage"]["declared_coverage"]["status"] == "not_recorded"
    assert report["coverage"]["declared_coverage"]["checklist"] == []
    assert report["coverage"]["unrequested_checks"] is None


def test_workflow_report_has_no_declared_projection_without_checklist(tmp_path):
    report = Core.workflow_report(
        _core_with(_evidence()), "plan-1",
    )

    assert report["coverage"]["declared_coverage"]["status"] == "not_recorded"


def test_workflow_report_fails_closed_on_conflicting_recon_projections(tmp_path):
    contract = {
        "schema_version": 1,
        "checklist": ["dns", "tls"],
        "requested": ["dns", "tls"],
        "included": ["dns"],
        "dispositions": [{"check_id": "tls", "disposition": "provider_unavailable"}],
    }
    legacy_metadata = {
        "proposal_type": "passive_recon",
        "requested_checks": ["dns"],
        "included_checks": ["dns"],
        "omitted_checks": [
            {"check": "tls", "reason": "provider unavailable",
             "disposition": "provider_unavailable"},
        ],
    }

    report = _declared_coverage_report(
        tmp_path, contract, extra_metadata=legacy_metadata,
    )

    assert report["coverage"]["declared_coverage"]["status"] == "invalid"
    assert report["coverage"]["declared_coverage"]["omissions"] == []
    assert report["coverage"]["requested_checks"] is None
    assert report["coverage"]["included_checks"] is None
    assert report["coverage"]["unrequested_checks"] is None
    assert report["coverage"]["unsupported_or_inaccessible_work"] == {
        "status": "not_recorded", "count": None, "items": [],
    }
