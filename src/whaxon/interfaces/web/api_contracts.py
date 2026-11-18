"""Typed HTTP contracts and generated OpenAPI for the WHAXON V2 API.

These Pydantic models validate the public Flask boundary while leaving
authorization, lifecycle, and execution decisions in the shared Core.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRunRequest(BaseModel):
    """Bounded execution limits accepted when submitting a saved workflow."""

    model_config = ConfigDict(extra="ignore", strict=True)

    max_tasks: int = Field(default=100, ge=1, le=1000)
    max_attempts: int = Field(default=2, ge=1, le=1000)
    max_concurrency: int = Field(default=4, ge=1, le=1000)


class WorkflowRunAccepted(BaseModel):
    """Acknowledgement for a durable run request, not a completion result."""

    model_config = ConfigDict(extra="forbid", strict=True)

    plan_id: str
    run_request_id: str
    request_status: str
    execution_submitted: bool
    execution_completed: bool
    durable_progress_url: str
    run_request_url: str
    run_snapshot_url: str


def openapi_document() -> dict:
    """Build the OpenAPI document for the typed V2 run-submission contract."""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "WHAXON V2 API",
            "version": "0.11.16",
            "description": (
                "Typed contracts for durable V2 workflow submission. A 202 "
                "response confirms a persisted request, not execution completion."
            ),
        },
        "paths": {
            "/api/v2/workflows/{plan_id}/run": {
                "post": {
                    "operationId": "submitWorkflowRun",
                    "summary": "Submit a bounded workflow run request",
                    "parameters": [
                        {
                            "name": "plan_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WorkflowRunRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "202": {
                            "description": (
                                "Durable request accepted; execution is not complete."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/WorkflowRunAccepted"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Invalid request object or execution limits."
                        },
                        "404": {"description": "Workflow plan not found."},
                        "409": {
                            "description": "Workflow plan cannot be submitted."
                        },
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "WorkflowRunRequest": WorkflowRunRequest.model_json_schema(),
                "WorkflowRunAccepted": WorkflowRunAccepted.model_json_schema(),
            }
        },
    }
