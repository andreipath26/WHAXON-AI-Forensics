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
