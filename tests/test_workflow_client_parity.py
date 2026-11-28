"""Cross-client Engine V2 lifecycle through the actual TUI controls."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest
from textual.widgets import Button, DataTable, Input, Static

from whaxon.core import Core
from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.tui.app import WhaxonApp
from whaxon.interfaces.tui.screens.workflows import WorkflowScreen
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


@pytest.mark.asyncio
async def test_tui_controls_share_approved_request_with_api_and_headless_cli(
    tmp_path, monkeypatch,
):
    """Exercise UI controls, persisted API observation, CLI cancellation, and TUI refresh.

    The only injected component is the inert plan proposal. A local policy manifest
    and the default loopback scope exercise the real Core authorization path. The
    supervised provider worker is forbidden so this scenario cannot launch a tool.
    """
    app = WhaxonApp(data_dir=tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        tui_core = app.core

        # Use the real plan-bound authorization path with a deterministic local
        # manifest. The run request remains queued and no provider is dispatched.
        tui_core.providers = None
        capabilities = CapabilityRegistry()
        capabilities.register(CapabilityManifest(
            capability_id="tool.nmap",
            provider_id="whaxon.adapter.nmap",
            provider_version="catalog-v1",
            transports=("local_process",),
            target_types=("ip",),
            permissions=("network.scan",),
            impact="moderate",
            readiness="registered",
        ))
        tui_core.capabilities = capabilities

        screen = WorkflowScreen()
        app.push_screen(screen)
        await pilot.pause()

        screen.query_one("#workflow-mission-id", Input).value = "mission-parity"
        screen.query_one("#workflow-objective", Input).value = "review authorized loopback fixture"
        await pilot.click("#workflow-create-mission")
        await pilot.pause()
        assert tui_core.missions(limit=100)[0]["id"] == "mission-parity"

        task = WorkflowTask(
            "scan", "tool.nmap", "127.0.0.1",
            permissions=("network.scan",), impact="moderate",
        )
        plan = WorkflowPlan("mission-parity", (task,))

        from whaxon.core import workflow_proposals

        monkeypatch.setattr(
            workflow_proposals,
            "propose_tool_workflow_plan",
            lambda *_args, **_kwargs: {
                "status": "proposed",
                "plan": plan.to_dict(),
                "capability_id": "tool.nmap",
            },
        )
        screen.query_one("#workflow-new-plan-id", Input).value = "plan-parity"
        screen.query_one("#workflow-tool-id", Input).value = "nmap"
        screen.query_one("#workflow-target", Input).value = "127.0.0.1"
        await pilot.click("#workflow-propose-tool")
        await pilot.pause()
        assert tui_core.workflow_plan_details("plan-parity")["plan"]["mission_id"] == "mission-parity"
        assert tui_core.workflow_approvals("plan-parity") == []

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

        assert tui_core.authorize_workflow_task_for_plan("plan-parity", task) is False
        await pilot.click("#workflow-approve")
        await pilot.pause()
        assert tui_core.authorize_workflow_task_for_plan("plan-parity", task) is True
        assert len(tui_core.workflow_approvals("plan-parity")) == 1
        assert screen.query_one("#workflow-submit", Button).disabled is False

        async def forbidden_drain(**_kwargs):
            raise AssertionError("TUI must not drain provider work inline")

        monkeypatch.setattr(tui_core, "drain_workflow_run_requests", forbidden_drain)
        await pilot.click("#workflow-submit")
        await pilot.pause()
        run_id = screen.run_request_id
        assert run_id
        assert tui_core.workflow_run_request(run_id)["status"] == "queued"

        # A separate API Core sees the same persisted request and exposes no lease.
        api_core = Core(data_dir=tmp_path)
        api_app = create_app(api_core, JobRegistry(api_core), AsyncRunner(api_core))
        api_app.config["TESTING"] = True
        client = api_app.test_client()
        response = client.get(f"/api/v2/workflow-runs/{run_id}/snapshot")
        assert response.status_code == 200
        snapshot = response.get_json()
        assert snapshot["request"]["id"] == run_id
        assert snapshot["request"]["status"] == "queued"
        assert snapshot["automatic_uncertain_replay"] is False
        assert "lease_token" not in snapshot["request"]

        # A distinct headless CLI process cancels through the persisted service.
        cli_args = [
            "--data-dir", str(tmp_path), "plan", "cancel-request", "--id", run_id,
        ]
        cli_process = subprocess.run(
            [
                sys.executable, "-c",
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

        after_cancel = client.get(f"/api/v2/workflow-runs/{run_id}/snapshot")
        assert after_cancel.status_code == 200
        assert after_cancel.get_json()["request"]["status"] == "cancelled"

        # Refresh through the real TUI control; no worker attempt was created.
        await pilot.click("#workflow-request-refresh")
        await pilot.pause()
        status_text = str(screen.query_one("#workflow-status", Static).content)
        assert f"Request {run_id}: cancelled" in status_text
        assert screen.query_one("#workflow-cancel", Button).disabled is True
        assert tui_core.store.list_workflow_attempts("plan-parity") == []
