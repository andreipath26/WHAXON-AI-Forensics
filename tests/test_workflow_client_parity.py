"""Cross-client V2 request state is shared and remains worker-owned."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
import sys

from textual.widgets import Button, DataTable, Static

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.tui.app import WhaxonApp
from whaxon.interfaces.tui.screens.workflows import WorkflowScreen
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


def test_tui_approved_run_is_observed_by_api_and_cancelled_by_cli(
    tmp_path, monkeypatch,
):
    async def run_scenario():
        """Exercise TUI create/approve/submit, API observation, CLI cancel, TUI refresh."""
        app = WhaxonApp(data_dir=tmp_path)
        async with app.run_test() as pilot:
            await pilot.pause()
            tui_core = app.core
            tui_core.create_mission("mission-parity", "review authorized fixture")
            plan = WorkflowPlan("mission-parity", (
                WorkflowTask("scan", "tool.nmap", "192.0.2.10"),
            ))
            tui_core.save_workflow_plan("plan-parity", plan)

            screen = WorkflowScreen()
            app.push_screen(screen)
            await pilot.pause()

            missions = screen.query_one("#workflow-missions", DataTable)
            missions.focus()
            missions.move_cursor(row=0)
            await pilot.press("enter")
            await pilot.pause()

            plans = screen.query_one("#workflow-plans", DataTable)
            plans.focus()
            plans.move_cursor(row=0)
            await pilot.press("enter")
            await pilot.pause()

            tasks = screen.query_one("#workflow-tasks", DataTable)
            tasks.focus()
            tasks.move_cursor(row=0)
            await pilot.press("enter")
            await pilot.pause()

            screen._approve_task()
            assert tui_core.workflow_approvals("plan-parity")[0]["task_key"] == "scan"
            assert screen.query_one("#workflow-submit", Button).disabled is False
            monkeypatch.setattr(
                tui_core, "authorize_workflow_task_for_plan", lambda *_: True,
            )

            async def forbidden_drain(**_kwargs):
                raise AssertionError("TUI must not drain provider work inline")

            monkeypatch.setattr(tui_core, "drain_workflow_run_requests", forbidden_drain)
            await screen._submit_plan().wait()
            run_id = screen.run_request_id
            assert run_id
            assert tui_core.workflow_run_request(run_id)["status"] == "queued"

            # A separate API Core instance observes the same durable TUI intent.
            api_core = Core(data_dir=tmp_path)
            api_app = create_app(api_core, JobRegistry(api_core), AsyncRunner(api_core))
            api_app.config["TESTING"] = True
            client = api_app.test_client()
            snapshot_response = client.get(
                f"/api/v2/workflow-runs/{run_id}/snapshot",
            )
            assert snapshot_response.status_code == 200
            snapshot = snapshot_response.get_json()
            assert snapshot["request"]["id"] == run_id
            assert snapshot["request"]["status"] == "queued"
            assert snapshot["automatic_uncertain_replay"] is False
            assert "lease_token" not in snapshot["request"]

            # The headless CLI cancels the request through the same persisted service.
            cli_args = [
                "--data-dir", str(tmp_path), "plan", "cancel-request", "--id", run_id,
            ]
            cli_process = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import sys; "
                        "from whaxon.interfaces.cli import workflow_cmd; "
                        "raise SystemExit(workflow_cmd.main(sys.argv[1:]))"
                    ),
                    *cli_args,
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            assert cli_process.returncode == 0, cli_process.stderr
            cli_state = json.loads(cli_process.stdout)
            assert cli_state["id"] == run_id
            assert cli_state["status"] == "cancelled"

            # API and TUI reconnect/observe the terminal state without a worker effect.
            cancelled = client.get(
                f"/api/v2/workflow-runs/{run_id}/snapshot",
            )
            assert cancelled.status_code == 200
            assert cancelled.get_json()["request"]["status"] == "cancelled"
            screen._refresh_request_status()
            status_text = str(screen.query_one("#workflow-status", Static).content)
            assert f"Request {run_id}: cancelled" in status_text
            assert screen.query_one("#workflow-cancel", Button).disabled is True
            assert tui_core.workflow_run_request(run_id)["status"] == "cancelled"
            assert tui_core.store.list_workflow_attempts("plan-parity") == []

    def run_in_fresh_loop_thread():
        asyncio.run(run_scenario())

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(run_in_fresh_loop_thread).result()
