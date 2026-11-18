"""Typed internal contracts for the existing HTTP API.

These models validate values at the Flask boundary without defining routes or
changing the public request and response representation.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRunRequest(BaseModel):
    """Execution limits accepted by the existing workflow-run endpoint."""

    model_config = ConfigDict(strict=True, extra="ignore")

    max_tasks: int = Field(default=100, ge=1, le=1000)
    max_attempts: int = Field(default=2, ge=1, le=1000)
    max_concurrency: int = Field(default=4, ge=1, le=1000)


class WorkflowToolProposalRequest(BaseModel):
    """Fixed catalog-tool proposal accepted by the existing V2 route."""

    model_config = ConfigDict(strict=True, extra="forbid")

    kind: Literal["tool"]
    mission_id: str
    id: str
    tool: str
    target: str
    save: bool = False


class WorkflowFindingProposalRequest(BaseModel):
    """Sealed-finding verification or retest proposal request."""

    model_config = ConfigDict(strict=True, extra="forbid")

    kind: Literal["verification"]
    mission_id: str
    id: str
    source_job_id: str
    finding_seq: int = Field(ge=0)
    mode: str
    save: bool = False


class WorkflowRunAccepted(BaseModel):
    """The unchanged 202 response returned by the workflow-run endpoint."""

    model_config = ConfigDict(strict=True, extra="forbid")

    plan_id: str
    run_request_id: str
    request_status: str
    execution_submitted: bool
    execution_completed: bool
    durable_progress_url: str
    run_request_url: str
    run_snapshot_url: str


class WorkflowEventAcknowledgement(BaseModel):
    """The existing durable-event acknowledgement request shape."""

    model_config = ConfigDict(strict=True, extra="ignore")

    consumer: str
    event_id: int


class WorkflowEventAcknowledgementResult(BaseModel):
    """The unchanged event acknowledgement response shape."""

    model_config = ConfigDict(strict=True, extra="forbid")

    plan_id: str
    consumer_id: str
    last_event_id: int
