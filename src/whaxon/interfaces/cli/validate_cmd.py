"""whaxon validate <job_id> <seq> — deterministic validation of a finding."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from whaxon.core import Core

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_USAGE = 2
EXIT_SCOPE_BLOCKED = 4
EXIT_V2_WORKFLOW_REQUIRED = 5

_USAGE = (
    "Usage: whaxon validate <job_id> <seq> [--data DIR] [--verbose] "
    "[--mission-id MISSION --plan-id PLAN [--save]]"
)


def main(args: list[str] | None = None) -> int:
    args = list(args or [])
    data_dir = Path("data")
    positional: list[str] = []
    mission_id: str | None = None
    plan_id: str | None = None
    save = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--data" and i + 1 < len(args):
            data_dir = Path(args[i + 1])
            i += 2
        elif a == "--mission-id" and i + 1 < len(args):
            mission_id = args[i + 1]
            i += 2
        elif a in ("--plan-id", "--id") and i + 1 < len(args):
            plan_id = args[i + 1]
            i += 2
        elif a == "--save":
            save = True
            i += 1
        elif a == "--verbose":
            i += 1
        elif a in ("-h", "--help"):
            print(_USAGE, file=sys.stderr)
            return EXIT_OK
        else:
            positional.append(a)
            i += 1

    proposal_context = mission_id is not None or plan_id is not None or save
    if len(positional) != 2 or (proposal_context and (not mission_id or not plan_id)):
        print(_USAGE, file=sys.stderr)
        return EXIT_USAGE

    job_id, seq_str = positional
    try:
        seq = int(seq_str)
    except ValueError:
        print(f"Invalid seq: {seq_str}", file=sys.stderr)
        return EXIT_USAGE

    core = Core(data_dir)
    asyncio.run(core.initialize(drain=False))

    findings = core.store.get_findings(job_id)
    if not findings:
        print(f"Job not found: {job_id}", file=sys.stderr)
        return EXIT_NOT_FOUND
    target_f = next((finding for finding in findings if finding["seq"] == seq), None)
    if target_f is None:
        print(f"Finding not found: {job_id} seq {seq}", file=sys.stderr)
        return EXIT_NOT_FOUND

    try:
        is_v2_job = core.store.is_engine_v2_execution_job(job_id)
    except Exception:
        print(
            "Cannot validate: V2 evidence ownership could not be confirmed; "
            "no request was sent.",
            file=sys.stderr,
        )
        return EXIT_SCOPE_BLOCKED

    if is_v2_job:
        if not proposal_context:
            print(
                "This finding belongs to Engine V2 evidence. Use "
                "'whaxon validate <job_id> <seq> --mission-id MISSION "
                "--plan-id PLAN [--save]' to prepare a proposal; "
                "approval and execution are separate.",
                file=sys.stderr,
            )
            return EXIT_V2_WORKFLOW_REQUIRED
        from whaxon.interfaces.cli.finding_proposal_cli import run_finding_proposal

        return run_finding_proposal(
            core,
            mission_id=mission_id or "",
            plan_id=plan_id or "",
            source_job_id=job_id,
            finding_seq=seq,
            mode="verify",
            save=save,
        )

    if proposal_context:
        print(
            "V2 proposal aliases require a persisted Engine V2 source finding; "
            "no request was sent.",
            file=sys.stderr,
        )
        return EXIT_V2_WORKFLOW_REQUIRED

    job = core.store.get(job_id)
    raw_target = (job or {}).get("target", "")
    target_url = (
        raw_target
        if raw_target.startswith(("http://", "https://"))
        else f"http://{raw_target}" if raw_target else None
    )
    if not target_url:
        print("Cannot validate: finding has no target URL; no request was sent.", file=sys.stderr)
        return EXIT_SCOPE_BLOCKED
    try:
        scope_match = core.scope.check(target_url)
    except Exception as exc:
        print(f"Cannot validate: scope evaluation failed ({exc}); no request was sent.", file=sys.stderr)
        return EXIT_SCOPE_BLOCKED
    if not scope_match.allowed:
        print(
            f"Cannot validate: target is out of scope ({scope_match.reason}); no request was sent.",
            file=sys.stderr,
        )
        return EXIT_SCOPE_BLOCKED

    print(
        "Legacy finding validation is disabled in Engine V2 mode; no request was sent. "
        "Use a V2 workflow with sealed finding evidence and exact operator approval.",
        file=sys.stderr,
    )
    return EXIT_V2_WORKFLOW_REQUIRED
