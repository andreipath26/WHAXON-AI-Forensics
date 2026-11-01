"""Durable, bounded-concurrency DAG scheduler for Engine v2 workflow plans."""
from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable
from typing import Any

from .workflow import WorkflowTask

_log = logging.getLogger(__name__)


class WorkflowScheduler:
    """Run persisted DAG nodes through injected policy and capability services.

    Claims are durable and atomic. Independent DAG nodes may run concurrently,
    while dependencies are only released by successful predecessor completion.
    The scheduler never constructs shell commands and authorization is fail-closed.
    """

    def __init__(self, store, *, authorize: Callable[[WorkflowTask], bool],
                 dispatch: Callable[[WorkflowTask], Any], worker_id: str = "workflow-worker"):
        if not callable(authorize) or not callable(dispatch):
            raise TypeError("authorize and dispatch callbacks are required")
        self.store = store
        self.authorize = authorize
        self.dispatch = dispatch
        self.worker_id = worker_id

    async def _execute(self, row: dict[str, Any]) -> dict[str, str]:
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
                if inspect.isawaitable(authorized):
                    authorized = await authorized
            except Exception as exc:
                self.store.finish_task_attempt(
                    attempt_id, "blocked",
                    error=f"policy authorization failed closed: {type(exc).__name__}",
                )
                return {"task_id": task.id, "status": "blocked"}
            if authorized is not True:
                self.store.finish_task_attempt(
                    attempt_id, "blocked", error="deterministic policy denied task",
                )
                return {"task_id": task.id, "status": "blocked"}

            loop = asyncio.get_running_loop()
            started = loop.time()
            if inspect.iscoroutinefunction(self.dispatch):
                result = self.dispatch(task)
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.dispatch, task), timeout=task.timeout_s,
                )
            if inspect.isawaitable(result):
                remaining = task.timeout_s - (loop.time() - started)
                if remaining <= 0:
                    raise TimeoutError
                result = await asyncio.wait_for(result, timeout=remaining)
            self.store.finish_task_attempt(attempt_id, "succeeded", result=result)
            return {"task_id": task.id, "status": "succeeded"}
        except TimeoutError:
            self.store.finish_task_attempt(
                attempt_id, "uncertain", error="task timed out; reconcile before retry",
            )
            return {"task_id": task.id, "status": "uncertain"}
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
            return {"task_id": task.id, "status": "failed"}

    async def run(self, plan_id: str, *, max_tasks: int = 100,
                  max_attempts: int = 2, max_concurrency: int = 4) -> dict[str, Any]:
        if max_tasks < 1 or max_attempts < 1 or max_concurrency < 1:
            raise ValueError("max_tasks, max_attempts and max_concurrency must be positive")
        if self.store.get_workflow_plan(plan_id) is None:
            raise ValueError(f"unknown workflow plan: {plan_id}")

        claimed = 0
        outcomes: list[dict[str, str]] = []
        claim_lock = asyncio.Lock()

        async def worker() -> None:
            nonlocal claimed
            while True:
                async with claim_lock:
                    if claimed >= max_tasks:
                        return
                    row = self.store.claim_ready_workflow_task(
                        plan_id, self.worker_id, max_attempts=max_attempts,
                    )
                    if row is None:
                        return
                    claimed += 1
                outcomes.append(await self._execute(row))

        await asyncio.gather(*(worker() for _ in range(min(max_concurrency, max_tasks))))
        tasks = self.store.list_workflow_tasks(plan_id)
        return {
            "plan_id": plan_id, "attempts": claimed, "outcomes": outcomes,
            "tasks": [{"id": task["id"], "status": task["status"]} for task in tasks],
            "complete": all(
                task["status"] in ("succeeded", "failed", "blocked", "cancelled", "uncertain")
                for task in tasks
            ),
        }
