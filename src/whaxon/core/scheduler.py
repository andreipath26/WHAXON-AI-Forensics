"""Durable DAG scheduler for Engine v2 workflow plans."""
from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any
from collections.abc import Callable

from .workflow import WorkflowTask

_log = logging.getLogger(__name__)


class WorkflowScheduler:
    """Run persisted DAG nodes through injected policy and capability services.

    The scheduler never constructs shell commands. Authorization is mandatory
    and fail-closed; dispatch must resolve the task capability through the
    provider layer and execute only the approved typed inputs.
    """

    def __init__(self, store, *, authorize: Callable[[WorkflowTask], bool],
                 dispatch: Callable[[WorkflowTask], Any], worker_id: str = "workflow-worker"):
        if not callable(authorize) or not callable(dispatch):
            raise TypeError("authorize and dispatch callbacks are required")
        self.store = store
        self.authorize = authorize
        self.dispatch = dispatch
        self.worker_id = worker_id

    async def run(self, plan_id: str, *, max_tasks: int = 100,
                  max_attempts: int = 2) -> dict[str, Any]:
        if max_tasks < 1 or max_attempts < 1:
            raise ValueError("max_tasks and max_attempts must be positive")
        if self.store.get_workflow_plan(plan_id) is None:
            raise ValueError(f"unknown workflow plan: {plan_id}")
        completed = 0
        outcomes: list[dict[str, Any]] = []
        while completed < max_tasks:
            row = self.store.claim_ready_workflow_task(
                plan_id, self.worker_id, max_attempts=max_attempts,
            )
            if row is None:
                break
            completed += 1
            task = WorkflowTask(
                id=row["id"], capability_id=row["capability_id"], target=row["target"],
                inputs=row["inputs"], depends_on=tuple(row["depends_on"]),
                permissions=tuple(row["permissions"]), impact=row["impact"],
                timeout_s=row["timeout_s"], idempotency_key=row["idempotency_key"],
            )
            attempt_id = row["attempt_id"]
            try:
                try:
                    authorized = self.authorize(task)
                except Exception as exc:
                    self.store.finish_task_attempt(
                        attempt_id, "blocked",
                        error=f"policy authorization failed closed: {type(exc).__name__}",
                    )
                    outcomes.append({"task_id": task.id, "status": "blocked"})
                    continue
                if authorized is not True:
                    self.store.finish_task_attempt(
                        attempt_id, "blocked", error="deterministic policy denied task",
                    )
                    outcomes.append({"task_id": task.id, "status": "blocked"})
                    continue
                started = asyncio.get_running_loop().time()
                if inspect.iscoroutinefunction(self.dispatch):
                    result = self.dispatch(task)
                else:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(self.dispatch, task), timeout=task.timeout_s,
                    )
                if inspect.isawaitable(result):
                    remaining = task.timeout_s - (asyncio.get_running_loop().time() - started)
                    if remaining <= 0:
                        raise TimeoutError
                    result = await asyncio.wait_for(result, timeout=remaining)
                self.store.finish_task_attempt(attempt_id, "succeeded", result=result)
                outcomes.append({"task_id": task.id, "status": "succeeded"})
            except TimeoutError:
                self.store.finish_task_attempt(
                    attempt_id, "uncertain", error="task timed out; reconcile before retry",
                )
                outcomes.append({"task_id": task.id, "status": "uncertain"})
            except asyncio.CancelledError:
                self.store.finish_task_attempt(
                    attempt_id, "uncertain",
                    error="scheduler cancelled while task was active; reconcile before retry",
                )
                raise
            except Exception as exc:
                _log.exception("workflow task %s failed", task.id)
                self.store.finish_task_attempt(
                    attempt_id, "failed", error=f"{type(exc).__name__}: {exc}",
                )
                outcomes.append({"task_id": task.id, "status": "failed"})
        tasks = self.store.list_workflow_tasks(plan_id)
        return {
            "plan_id": plan_id, "attempts": completed, "outcomes": outcomes,
            "tasks": [{"id": task["id"], "status": task["status"]} for task in tasks],
            "complete": all(
                task["status"] in ("succeeded", "failed", "blocked", "cancelled", "uncertain")
                for task in tasks
            ),
        }
