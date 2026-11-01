"""Headless Engine v2 workflow commands."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="whaxon workflow")
    parser.add_argument(
        "--data-dir", default=os.environ.get("WHAXON_DATA", "data"),
        help="WHAXON state directory (default: WHAXON_DATA or ./data)",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("capabilities", help="list registered Engine v2 capabilities")

    mission = commands.add_parser("mission", help="manage missions")
    mission_commands = mission.add_subparsers(dest="mission_command", required=True)
    create = mission_commands.add_parser("create", help="create a mission")
    create.add_argument("--id", required=True)
    create.add_argument("--objective", required=True)

    plan = commands.add_parser("plan", help="manage persisted workflow plans")
    plan_commands = plan.add_subparsers(dest="plan_command", required=True)
    save = plan_commands.add_parser("save", help="validate and persist a JSON workflow plan")
    save.add_argument("--id", required=True, help="immutable persisted plan identifier")
    save.add_argument("--file", required=True, type=Path, help="JSON file containing a WorkflowPlan")
    show = plan_commands.add_parser("show", help="show a plan and its durable task states")
    show.add_argument("--id", required=True)
    run = plan_commands.add_parser("run", help="execute a plan through scoped Core providers")
    run.add_argument("--id", required=True)
    run.add_argument("--max-tasks", type=int, default=100)
    run.add_argument("--max-attempts", type=int, default=2)
    return parser


def main(args: list[str] | None = None) -> int:
    options = _parser().parse_args(args)
    core = Core(data_dir=Path(options.data_dir))
    try:
        if options.command == "capabilities":
            result = [manifest.to_dict() for manifest in core.capabilities.list()]
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        if options.command == "mission" and options.mission_command == "create":
            created = core.create_mission(options.id, options.objective)
            print(json.dumps({"mission_id": options.id, "created": bool(created)}))
            return 0
        if options.command == "plan" and options.plan_command == "save":
            raw = json.loads(options.file.read_text(encoding="utf-8"))
            workflow = WorkflowPlan.from_dict(raw)
            created = core.save_workflow_plan(options.id, workflow)
            print(json.dumps({
                "plan_id": options.id, "mission_id": workflow.mission_id,
                "digest": workflow.digest, "created": bool(created),
            }, sort_keys=True))
            return 0
        if options.command == "plan" and options.plan_command == "show":
            plan = core.store.get_workflow_plan(options.id)
            if plan is None:
                print(f"unknown workflow plan: {options.id}", file=sys.stderr)
                return 2
            print(json.dumps({
                "plan": plan["plan"],
                "tasks": core.store.list_workflow_tasks(options.id),
            }, indent=2, sort_keys=True))
            return 0
        if options.command == "plan" and options.plan_command == "run":
            if options.max_tasks < 1 or options.max_attempts < 1:
                print("--max-tasks and --max-attempts must be positive", file=sys.stderr)
                return 2

            async def execute():
                await core.initialize(drain=False)
                return await core.run_workflow_plan(
                    options.id, max_tasks=options.max_tasks,
                    max_attempts=options.max_attempts,
                )

            result = asyncio.run(execute())
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["complete"] and all(
                task["status"] == "succeeded" for task in result["tasks"]
            ) else 1
        return 2
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(f"workflow command failed: {exc}", file=sys.stderr)
        return 2
