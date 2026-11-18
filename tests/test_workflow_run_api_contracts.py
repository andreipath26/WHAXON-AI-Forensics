"""Regression coverage for typed validation behind the stable workflow-run API."""
from __future__ import annotations

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.web.api_contracts import WorkflowRunAccepted, WorkflowRunRequest
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


def test_workflow_run_request_contract_is_strict_bounded_and_ignores_extras():
    assert WorkflowRunRequest.model_validate({}).model_dump() == {
        "max_tasks": 100,
        "max_attempts": 2,
        "max_concurrency": 4,
    }
    assert WorkflowRunRequest.model_validate({
        "max_tasks": 1,
        "max_attempts": 1000,
        "max_concurrency": 4,
        "future_client_field": "ignored",
    }).model_dump() == {
        "max_tasks": 1,
        "max_attempts": 1000,
        "max_concurrency": 4,
    }


def test_workflow_run_response_contract_keeps_existing_fields():
    response = WorkflowRunAccepted.model_validate({
        "plan_id": "plan-1",
        "run_request_id": "request-1",
        "request_status": "queued",
        "execution_submitted": True,
        "execution_completed": False,
        "durable_progress_url": "/api/v2/workflows/plan-1/progress",
        "run_request_url": "/api/v2/workflow-runs/request-1",
        "run_snapshot_url": "/api/v2/workflow-runs/request-1/snapshot",
    })
    assert set(response.model_dump()) == {
        "plan_id",
        "run_request_id",
        "request_status",
        "execution_submitted",
        "execution_completed",
        "durable_progress_url",
        "run_request_url",
        "run_snapshot_url",
    }


def test_workflow_run_endpoint_preserves_http_contract(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_DATA", str(tmp_path))
    core = Core(data_dir=tmp_path)
    core.create_mission("mission", "authorized test")
    core.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    runner = AsyncRunner(core)
    runner.submit = lambda _work: None
    app = create_app(core, JobRegistry(core), runner)
    app.config["TESTING"] = True
    client = app.test_client()

    invalid_body = {"error": "execution limits must be positive and bounded"}
    for payload in (
        {"max_tasks": True},
        {"max_tasks": 1.0},
        {"max_tasks": 0},
        {"max_tasks": 1001},
        {"max_attempts": "2"},
        {"max_concurrency": -1},
    ):
        response = client.post("/api/v2/workflows/plan/run", json=payload)
        assert response.status_code == 400
        assert response.get_json() == invalid_body

    non_object = client.post("/api/v2/workflows/plan/run", json=[])
    assert non_object.status_code == 400
    assert non_object.get_json() == {"error": "JSON object required"}

    response = client.post(
        "/api/v2/workflows/plan/run",
        json={"future_client_field": "ignored"},
    )
    assert response.status_code == 202
    body = response.get_json()
    assert set(body) == {
        "plan_id",
        "run_request_id",
        "request_status",
        "execution_submitted",
        "execution_completed",
        "durable_progress_url",
        "run_request_url",
        "run_snapshot_url",
    }
    assert body["plan_id"] == "plan"
    assert body["request_status"] == "queued"
    assert body["execution_submitted"] is True
    assert body["execution_completed"] is False
    assert body["durable_progress_url"] == "/api/v2/workflows/plan/progress"
    assert body["run_request_url"] == (
        f"/api/v2/workflow-runs/{body['run_request_id']}"
    )
    assert body["run_snapshot_url"] == (
        f"/api/v2/workflow-runs/{body['run_request_id']}/snapshot"
    )
    queued = core.workflow_run_request(body["run_request_id"])
    assert queued["max_tasks"] == 100
    assert queued["max_attempts"] == 2
    assert queued["max_concurrency"] == 4
