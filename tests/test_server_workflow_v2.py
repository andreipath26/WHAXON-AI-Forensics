"""Engine V2 API uses the same persisted Core service as the headless CLI."""
from __future__ import annotations

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


def _client(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_DATA", str(tmp_path))
    core = Core(data_dir=tmp_path)
    app = create_app(core, JobRegistry(core), AsyncRunner(core))
    app.config["TESTING"] = True
    return app.test_client(), core


def test_workflow_v2_read_only_routes_use_shared_persistence(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    assert client.get("/api/v2/missions").get_json()[0]["id"] == "m"
    assert client.get("/api/v2/missions/m/plans").get_json()[0]["id"] == "p"
    progress = client.get("/api/v2/workflows/p/progress")
    assert progress.status_code == 200
    assert progress.get_json()["total_tasks"] == 1
    assert client.get("/api/v2/workflows/p/events").get_json() == []
    readiness = client.get("/api/v2/workflows/p/readiness").get_json()
    assert readiness["ready_to_report_success"] is False
    assert client.get("/api/v2/workflows/p/reconciliation").get_json() == []


def test_workflow_v2_api_bounds_and_missing_plan(tmp_path, monkeypatch):
    client, _ = _client(tmp_path, monkeypatch)
    assert client.get("/api/v2/workflows/missing/progress").status_code == 404
    assert client.get("/api/v2/workflows/missing/readiness").status_code == 404
    assert client.get("/api/v2/workflows/missing/events?limit=0").status_code == 400
    assert client.get("/api/v2/missions?limit=0").status_code == 400


def test_workflow_v2_cancel_shares_persisted_stop_barrier(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    result = client.post("/api/v2/workflows/p/cancel")
    assert result.status_code == 200
    assert result.get_json()["cancellation_requested"] is True
    assert result.get_json()["external_effects_stopped"] is False
    assert core.store.claim_ready_workflow_task("p", "worker") is None
    assert client.post("/api/v2/workflows/p/cancel").get_json()["tasks_cancelled"] == 0


def test_workflow_v2_cancel_rejects_cross_origin(tmp_path, monkeypatch):
    client, _ = _client(tmp_path, monkeypatch)
    response = client.post(
        "/api/v2/workflows/p/cancel",
        headers={"Origin": "https://attacker.invalid"},
    )
    assert response.status_code == 403


def test_workflow_v2_diagnostics_routes_share_live_store(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    assert client.get("/api/v2/workflows/p/attempts").get_json() == []
    assert client.get("/api/v2/workflows/p/audit").get_json()["consistent"]
    resource = client.get("/api/v2/workflows/p/resources").get_json()
    assert resource["cost_usd"] is None
    assert client.get("/api/v2/workflows/p/limits").get_json()["limits"]["max_concurrency"] == 4
    assert client.get("/api/v2/workflows/p/attempts?limit=0").status_code == 400


def test_workflow_v2_control_routes_reject_invalid_budgets(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    assert client.post(
        "/api/v2/workflows/p/limits",
        json={"max_total_attempts": 3, "max_concurrency": 1},
    ).get_json()["limits"]["max_concurrency"] == 1
    assert client.post(
        "/api/v2/workflows/p/limits",
        json={"max_total_attempts": 4, "max_concurrency": 2},
    ).status_code == 400
    assert client.post(
        "/api/v2/workflows/p/limits", json={"max_total_attempts": -1},
    ).status_code == 400
    assert client.post(
        "/api/v2/workflows/p/deadline", json={"deadline_at": 1000000000.0},
    ).status_code == 200
    assert client.post(
        "/api/v2/workflows/p/deadline", json={"deadline_at": 2000000000.0},
    ).status_code == 400
    assert client.post(
        "/api/v2/workflows/p/rate-limit", json={"min_spacing_s": 5.0},
    ).status_code == 200
    assert client.post(
        "/api/v2/workflows/p/rate-limit", json={"min_spacing_s": 1.0},
    ).status_code == 400


def test_workflow_v2_control_routes_enforce_cross_origin_gate(tmp_path, monkeypatch):
    client, _ = _client(tmp_path, monkeypatch)
    for route in (
        "/api/v2/workflows/p/limits",
        "/api/v2/workflows/p/deadline",
        "/api/v2/workflows/p/rate-limit",
    ):
        assert client.post(route, headers={"Origin": "https://attacker.invalid"}).status_code == 403


def test_workflow_v2_mission_budget_is_shared_with_store(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    response = client.post("/api/v2/missions/m/budget", json={
        "max_total_attempts": 4, "max_concurrency": 2,
    })
    assert response.status_code == 200
    assert response.get_json()["max_total_attempts"] == 4
    assert core.store.get_mission_execution_limits("m")["max_concurrency"] == 2
    assert client.get("/api/v2/missions/m/budget").get_json()["enforced"] is True
    assert client.post("/api/v2/missions/m/budget", json={
        "max_total_attempts": 5, "max_concurrency": 2,
    }).status_code == 400
    assert client.get("/api/v2/missions/missing/budget").status_code == 404


def test_mission_deadline_api_blocks_later_claims(tmp_path, monkeypatch):
    import time

    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.1"),
    )))
    response = client.post(
        "/api/v2/missions/m/deadline", json={"deadline_at": time.time() - 1},
    )
    assert response.status_code == 200
    assert response.get_json()["deadline_exceeded"] is True
    assert core.store.claim_ready_workflow_task("p", "worker") is None
    assert client.post(
        "/api/v2/missions/m/deadline", json={"deadline_at": time.time() + 100},
    ).status_code == 400


def test_mission_cost_api_requires_explicit_cost_evidence(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    response = client.post("/api/v2/missions/m/cost", json={"max_cost_microusd": 100})
    assert response.status_code == 200
    assert response.get_json()["cap_microusd"] == 100
    assert client.get("/api/v2/missions/m/cost").get_json()["reported_attempts"] == 0
    assert client.post(
        "/api/v2/workflows/attempts/unknown/cost",
        json={"cost_microusd": 3, "source": "invoice"},
    ).status_code == 400


def test_v2_api_creates_mission_and_persists_plan_using_core(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    created = client.post("/api/v2/missions", json={"id": "m", "objective": "controlled"})
    assert created.status_code == 201
    assert created.get_json()["created"] is True
    plan = WorkflowPlan("m", (WorkflowTask("scan", "fixture", "192.0.2.10"),))
    saved = client.post("/api/v2/workflows", json={"id": "p", "plan": plan.to_dict()})
    assert saved.status_code == 201
    assert saved.get_json()["digest"] == plan.digest
    assert core.store.get_workflow_plan("p")["digest"] == plan.digest
    detail = client.get("/api/v2/workflows/p")
    assert detail.status_code == 200
    assert detail.get_json()["plan"]["mission_id"] == "m"
    assert len(detail.get_json()["tasks"]) == 1
    assert client.get("/api/v2/workflows/unknown").status_code == 404
    assert client.post("/api/v2/workflows", json={"id": "bad", "plan": {}}).status_code == 400
    assert client.post("/api/v2/missions", json={"id": 1, "objective": "x"}).status_code == 400


def test_v2_api_mission_rate_limit_shared_and_fail_closed(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p1", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    core.save_workflow_plan("p2", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.11"),
    )))
    response = client.post("/api/v2/missions/m/rate-limit", json={"min_spacing_s": 3600})
    assert response.status_code == 200
    assert response.get_json()["min_spacing_s"] == 3600
    assert core.store.claim_ready_workflow_task("p1", "worker-1") is not None
    assert core.store.claim_ready_workflow_task("p2", "worker-2") is None
    assert client.get("/api/v2/missions/m/rate-limit").get_json()["last_claimed_at"] is not None
    assert client.post("/api/v2/missions/m/rate-limit", json={"min_spacing_s": 1}).status_code == 400
    assert client.get("/api/v2/missions/unknown/rate-limit").status_code == 404
    assert client.post(
        "/api/v2/missions/m/rate-limit", json={"min_spacing_s": 7200},
        headers={"Origin": "https://attacker.invalid"},
    ).status_code == 403
    assert client.post(
        "/api/v2/workflows", json={"id": "evil", "plan": {}},
        headers={"Origin": "https://attacker.invalid"},
    ).status_code == 403


def test_v2_api_run_submits_bounded_core_execution_without_claiming_success(
    tmp_path, monkeypatch,
):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    captured = []
    monkeypatch.setattr(
        "whaxon.interfaces.web.server.AsyncRunner.submit",
        lambda self, factory: captured.append(factory),
    )
    response = client.post(
        "/api/v2/workflows/p/run",
        json={"max_tasks": 1, "max_attempts": 1, "max_concurrency": 1},
    )
    assert response.status_code == 202
    assert response.get_json()["execution_submitted"] is True
    assert response.get_json()["execution_completed"] is False
    assert response.get_json()["durable_progress_url"] == "/api/v2/workflows/p/progress"
    assert len(captured) == 1
    assert core.workflow_progress("p")["total_tasks"] == 1
    assert client.post("/api/v2/workflows/missing/run", json={}).status_code == 404
    for value in (True, 0, -1, "1", 1.5):
        assert client.post(
            "/api/v2/workflows/p/run", json={"max_tasks": value},
        ).status_code == 400
    assert len(captured) == 1
    assert client.post(
        "/api/v2/workflows/p/run", json={},
        headers={"Origin": "https://attacker.invalid"},
    ).status_code == 403
    assert len(captured) == 1


def test_v2_api_approval_and_reconciliation_parity(tmp_path, monkeypatch):
    import time

    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10", impact="moderate"),
    )))
    assert client.post("/api/v2/workflows/p/approvals", json={
        "task_key": "scan", "approval_id": "approval-1",
        "actor": "operator", "expires_at": time.time() + 300,
    }).status_code == 200
    assert len(client.get("/api/v2/workflows/p/approvals").get_json()) == 1
    assert client.post(
        "/api/v2/workflows/p/approvals/approval-1/revoke",
        json={"actor": "operator"},
    ).status_code == 200
    assert client.post(
        "/api/v2/workflows/p/reconcile", json={"stale_after_s": 60},
    ).status_code == 200
    assert client.post(
        "/api/v2/workflows/p/approvals", json={"task_key": "scan"},
    ).status_code == 400
    assert client.post(
        "/api/v2/workflows/p/approvals", json={},
        headers={"Origin": "https://attacker.invalid"},
    ).status_code == 403


def test_v2_api_event_consumer_parity_and_validation(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    core.save_workflow_plan("p", WorkflowPlan("m", (
        WorkflowTask("scan", "fixture", "192.0.2.10"),
    )))
    assert client.get("/api/v2/workflows/p/event-inbox").status_code == 400
    assert client.get(
        "/api/v2/workflows/p/event-inbox?consumer=worker",
    ).status_code == 200
    assert client.post(
        "/api/v2/workflows/p/event-ack", json={"consumer": "worker", "event_id": True},
    ).status_code == 400
    assert client.post(
        "/api/v2/workflows/p/event-ack", json={"consumer": "worker", "event_id": 0},
    ).status_code in (200, 400)
    assert client.post(
        "/api/v2/workflows/p/event-ack", json={"consumer": "worker", "event_id": 1},
        headers={"Origin": "https://attacker.invalid"},
    ).status_code == 403


def test_v2_api_mission_deadline_returns_persisted_cutoff_not_budget(tmp_path, monkeypatch):
    client, core = _client(tmp_path, monkeypatch)
    core.create_mission("m", "controlled")
    response = client.post("/api/v2/missions/m/deadline", json={
        "deadline_at": 2000000000,
    })
    assert response.status_code == 200
    assert response.get_json() == {"mission_id": "m", "deadline_at": 2000000000}
    assert core.store.get_mission_deadline("m") == 2000000000
    assert client.post(
        "/api/v2/missions/m/deadline", json={"deadline_at": 2100000000},
    ).status_code == 400
    assert client.post(
        "/api/v2/missions/unknown/deadline", json={"deadline_at": 2000000000},
    ).status_code == 404
