"""Shared identity rules for durable Engine V2 provider jobs."""
from __future__ import annotations

import uuid


def provider_execution_job_id(task) -> str:
    """Use a durable attempt ID for workflow jobs; keep direct calls random."""
    attempt_id = getattr(task, "_attempt_id", None)
    if attempt_id is None:
        return uuid.uuid4().hex[:12]
    if (
        not isinstance(attempt_id, str)
        or len(attempt_id) != 32
        or any(char not in "0123456789abcdef" for char in attempt_id)
        or getattr(task, "_provider_execution_id", None) != attempt_id
    ):
        raise ValueError("invalid durable V2 provider execution identity")
    return attempt_id
