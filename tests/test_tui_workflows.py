"""TUI workflow controls use persisted V2 plans and durable request services."""
from __future__ import annotations

from textual.widgets import Button, DataTable, Static

from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.tui.app import WhaxonApp
from whaxon.interfaces.tui.screens.workflows import WorkflowScreen


async def test_tui_reviews_approves_and_cancels_durable_v2_request(tmp_path, monkeypatch):
    app = WhaxonApp(data_dir=tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        core = app.core
        core.create_mission("mission-tui", "review an authorized lab")
        plan = WorkflowPlan("mission-tui", (
            WorkflowTask("scan", "tool.nmap", "192.0.2.10"),
        ))
        core.save_workflow_plan("plan-tui", plan)

        screen = WorkflowScreen()
        app.push_screen(screen)
        await pilot.pause()

        missions = screen.query_one("#workflow-missions", DataTable)
        assert missions.row_count == 1
        missions.focus()
        missions.move_cursor(row=0)
        await pilot.press("enter")
        await pilot.pause()

        plans = screen.query_one("#workflow-plans", DataTable)
        assert plans.row_count == 1
        plans.focus()
        plans.move_cursor(row=0)
        await pilot.press("enter")
        await pilot.pause()

        tasks = screen.query_one("#workflow-tasks", DataTable)
        assert tasks.row_count == 1
        details = screen.query_one("#workflow-details")
        assert any(plan.digest in str(line) for line in details.lines)
        tasks.focus()
        tasks.move_cursor(row=0)
        await pilot.press("enter")
        await pilot.pause()

        screen._approve_task()
        approvals = core.workflow_approvals("plan-tui")
        assert len(approvals) == 1
        assert approvals[0]["task_key"] == "scan"
        assert screen.query_one("#workflow-submit", Button).disabled is False

        monkeypatch.setattr(core, "authorize_workflow_task_for_plan", lambda *_: True)

        async def leave_queued(**_kwargs):
            return 0

        monkeypatch.setattr(core, "drain_workflow_run_requests", leave_queued)
        worker = screen._submit_plan()
        await worker.wait()

        assert screen.run_request_id
        queued = core.workflow_run_request(screen.run_request_id)
        assert queued["status"] == "queued"
        assert "not reported as completed" in screen.query_one(
            "#workflow-status", Static,
        ).content

        screen._cancel_request()
        assert core.workflow_run_request(screen.run_request_id)["status"] == "cancelled"
