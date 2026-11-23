"""Shared proposal-only CLI wiring for V2 finding verification and retest."""
from __future__ import annotations

import json
import sys

from whaxon.core.workflow import WorkflowPlan

EXIT_OK = 0
EXIT_BLOCKED = 4


def run_finding_proposal(
    core,
    *,
    mission_id: str,
    plan_id: str,
    source_job_id: str,
    finding_seq: int,
    mode: str,
    save: bool,
) -> int:
    """Print an inert V2 proposal and persist it only when explicitly requested."""
    from whaxon.core.workflow_proposals import propose_finding_verification_plan

    proposal = propose_finding_verification_plan(
        core,
        mission_id=mission_id,
        plan_id=plan_id,
        source_job_id=source_job_id,
        finding_seq=finding_seq,
        mode=mode,
    )
    created = False
    if save and proposal.get("status") == "proposed":
        try:
            plan_data = proposal.get("plan")
            if not isinstance(plan_data, dict):
                raise ValueError("proposal did not contain a workflow plan")
            created = bool(core.save_workflow_plan(
                plan_id, WorkflowPlan.from_dict(plan_data),
            ))
        except (AttributeError, KeyError, TypeError, ValueError, RuntimeError) as exc:
            print(json.dumps({
                "status": "blocked",
                "reason": f"proposal could not be persisted: {exc}",
                "created": False,
                "execution_submitted": False,
                "approval_granted": False,
            }, sort_keys=True))
            return EXIT_BLOCKED

    output = {**proposal, "created": created}
    print(json.dumps(output, indent=2, sort_keys=True))
    if proposal.get("status") != "proposed" or (save and not created):
        return EXIT_BLOCKED
    return EXIT_OK
