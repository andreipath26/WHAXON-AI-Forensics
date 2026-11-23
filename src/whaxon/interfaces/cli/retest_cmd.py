"""whaxon retest <job_id> <seq> — re-propose a previously verified finding."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from whaxon.core import Core

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_USAGE = 2
EXIT_NOT_VERIFIED = 3
EXIT_SCOPE_BLOCKED = 4
EXIT_V2_WORKFLOW_REQUIRED = 5

_USAGE = (
    "Usage: whaxon retest <job_id> <seq> [--data DIR] [--verbose] "
    "[--mission-id MISSION --plan-id PLAN [--save]]"
)


def main(args: list[str] | None = None) -> int:
    args = list(args or [])
    data_dir = Path("data")
    positional: list[str] = []
    mission_id: str | None = None
    plan_id: str | None = None
    save = False
    seen_options: set[str] = set()
    i = 0
    while i < len(args):
        a = args[i]
        value_options = {"--data": "data", "--mission-id": "mission", "--plan-id": "plan", "--id": "plan"}
        if a in value_options:
            option_key = value_options[a]
            if (
                option_key in seen_options
                or i + 1 >= len(args)
                or args[i + 1].startswith("-")
            ):
                print(_USAGE, file=sys.stderr)
                return EXIT_USAGE
            seen_options.add(option_key)
            value = args[i + 1]
            if option_key == "data":
                data_dir = Path(value)
            elif option_key == "mission":
                mission_id = value
            else:
                plan_id = value
            i += 2
        elif a == "--save":
            save = True
            i += 1
        elif a == "--verbose":
            i += 1
        elif a in ("-h", "--help"):
            print(_USAGE, file=sys.stderr)
            return EXIT_OK
        elif a.startswith("-"):
            print(_USAGE, file=sys.stderr)
            return EXIT_USAGE
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
    if seq < 0:
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
            "Cannot retest: V2 evidence ownership could not be confirmed; "
            "no request was sent.",
            file=sys.stderr,
        )
        return EXIT_SCOPE_BLOCKED

    if is_v2_job:
        if not proposal_context:
            print(
                "This finding belongs to Engine V2 evidence. Use "
                "'whaxon retest <job_id> <seq> --mission-id MISSION "
                "--plan-id PLAN [--save]' or 'whaxon workflow plan "
                "propose-verification --mode retest'; approval and execution "
                "are separate.",
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
            mode="retest",
            save=save,
        )

    if proposal_context:
        print(
            "V2 proposal aliases require a persisted Engine V2 source finding; "
            "no request was sent.",
            file=sys.stderr,
        )
        return EXIT_V2_WORKFLOW_REQUIRED

    if target_f.get("verification_status") != "verified":
        print(
            f"Finding {job_id}:{seq} is not verified "
            f"(status={target_f.get('verification_status')}). "
            "Retest requires a previously verified finding.",
            file=sys.stderr,
        )
        return EXIT_NOT_VERIFIED

    job = core.store.get(job_id)
    raw_target = (job or {}).get("target", "")
    if raw_target.startswith(("http://", "https://")):
        target_url = raw_target
    elif raw_target:
        target_url = f"http://{raw_target}"
    else:
        target_url = None

    if not target_url:
        print("Cannot retest: finding has no target URL; no request was sent.", file=sys.stderr)
        return EXIT_SCOPE_BLOCKED
    try:
        scope_match = core.scope.check(target_url)
    except Exception as exc:
        print(f"Cannot retest: scope evaluation failed ({exc}); no request was sent.", file=sys.stderr)
        return EXIT_SCOPE_BLOCKED
    if not scope_match.allowed:
        print(
            f"Cannot retest: target is out of scope ({scope_match.reason}); no request was sent.",
            file=sys.stderr,
        )
        return EXIT_SCOPE_BLOCKED

    print(
        "Legacy finding retest is disabled in Engine V2 mode; no request was sent. "
        "Use a V2 workflow with sealed finding evidence and exact operator approval.",
        file=sys.stderr,
    )
    return EXIT_V2_WORKFLOW_REQUIRED
