"""Versioned, immutable contracts for Engine v2 mission plans.

AI may propose these objects; policy and the scheduler remain responsible for
authorizing and executing them.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

WORKFLOW_SCHEMA_VERSION = "whaxon.workflow.v1"
_ALLOWED_IMPACTS = {"read_only", "low", "moderate", "high", "critical"}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class WorkflowTask:
    """One typed node in a mission DAG; it contains no executable shell text."""

    id: str
    capability_id: str
    target: str
    inputs: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    impact: str = "read_only"
    timeout_s: float = 300.0
    idempotency_key: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.capability_id.strip() or not self.target.strip():
            raise ValueError("task id, capability_id and target are required")
        if self.impact not in _ALLOWED_IMPACTS:
            raise ValueError(f"unsupported task impact: {self.impact}")
        if self.timeout_s <= 0:
            raise ValueError("task timeout_s must be positive")
        if self.id in self.depends_on or len(set(self.depends_on)) != len(self.depends_on):
            raise ValueError("task dependencies must be unique and cannot include itself")
        if not isinstance(self.inputs, dict):
            raise TypeError("task inputs must be an object")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["depends_on"] = list(self.depends_on)
        value["permissions"] = list(self.permissions)
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WorkflowTask":
        return cls(
            id=value["id"],
            capability_id=value["capability_id"],
            target=value["target"],
            inputs=dict(value.get("inputs") or {}),
            depends_on=tuple(value.get("depends_on") or ()),
            permissions=tuple(value.get("permissions") or ()),
            impact=value.get("impact", "read_only"),
            timeout_s=float(value.get("timeout_s", 300.0)),
            idempotency_key=value.get("idempotency_key", ""),
        )


@dataclass(frozen=True)
class WorkflowPlan:
    """Immutable versioned DAG. Its digest binds approvals to exact task content."""

    mission_id: str
    tasks: tuple[WorkflowTask, ...]
    schema_version: str = WORKFLOW_SCHEMA_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schema_version != WORKFLOW_SCHEMA_VERSION:
            raise ValueError(f"unsupported workflow schema: {self.schema_version}")
        if not self.mission_id.strip():
            raise ValueError("mission_id is required")
        ids = [task.id for task in self.tasks]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("a plan requires uniquely identified tasks")
        known = set(ids)
        for task in self.tasks:
            missing = set(task.depends_on) - known
            if missing:
                raise ValueError(f"task {task.id} has unknown dependencies: {sorted(missing)}")
        # Kahn's algorithm rejects cycles before a plan can be persisted.
        remaining = {task.id: set(task.depends_on) for task in self.tasks}
        ready = [task_id for task_id, deps in remaining.items() if not deps]
        visited = 0
        while ready:
            current = ready.pop()
            visited += 1
            for task_id, deps in remaining.items():
                if current in deps:
                    deps.remove(current)
                    if not deps:
                        ready.append(task_id)
        if visited != len(remaining):
            raise ValueError("workflow plan contains a dependency cycle")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mission_id": self.mission_id,
            "metadata": self.metadata,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @property
    def digest(self) -> str:
        return hashlib.sha256(_canonical(self.to_dict()).encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WorkflowPlan":
        return cls(
            mission_id=value["mission_id"],
            schema_version=value.get("schema_version", WORKFLOW_SCHEMA_VERSION),
            metadata=dict(value.get("metadata") or {}),
            tasks=tuple(WorkflowTask.from_dict(task) for task in value["tasks"]),
        )


@dataclass(frozen=True)
class ApprovalBinding:
    """Approval is valid only for this exact plan/task/policy/expiry tuple."""

    plan_digest: str
    task_id: str
    target: str
    input_digest: str
    policy_version: str
    expires_at: float
    permissions: tuple[str, ...] = ()
    impact: str = "read_only"

    @staticmethod
    def digest_inputs(inputs: dict[str, Any]) -> str:
        return hashlib.sha256(_canonical(inputs).encode("utf-8")).hexdigest()

    def is_valid(self, *, plan_digest: str, task: WorkflowTask,
                 policy_version: str, now: float) -> bool:
        return (
            now < self.expires_at
            and self.plan_digest == plan_digest
            and self.task_id == task.id
            and self.target == task.target
            and self.input_digest == self.digest_inputs(task.inputs)
            and self.policy_version == policy_version
            and self.permissions == task.permissions
            and self.impact == task.impact
        )
