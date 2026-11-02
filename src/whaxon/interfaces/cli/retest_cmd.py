"""whaxon retest <job_id> <seq> — re-run a previously verified finding."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from whaxon.core import Core
from whaxon.core.findings import Finding
from whaxon.core.validator import Validator

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_USAGE = 2
EXIT_NOT_VERIFIED = 3
EXIT_SCOPE_BLOCKED = 4


def main(args: list[str] | None = None) -> int:
    args = list(args or [])
    data_dir = Path("data")
    verbose = False
    positional: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--data" and i + 1 < len(args):
            data_dir = Path(args[i + 1]); i += 2
        elif a == "--verbose":
            verbose = True; i += 1
        elif a in ("-h", "--help"):
            print("Usage: whaxon retest <job_id> <seq> [--data DIR] [--verbose]", file=sys.stderr)
            return EXIT_OK
        else:
            positional.append(a); i += 1

    if len(positional) != 2:
        print("Usage: whaxon retest <job_id> <seq> [--data DIR] [--verbose]", file=sys.stderr)
        return EXIT_USAGE

    job_id, seq_str = positional
    try:
        seq = int(seq_str)
    except ValueError:
        print(f"Invalid seq: {seq_str}", file=sys.stderr)
        return EXIT_USAGE

    core = Core(data_dir)
    asyncio.run(core.initialize())

    findings = core.store.get_findings(job_id)
    if not findings:
        print(f"Job not found: {job_id}", file=sys.stderr)
        return EXIT_NOT_FOUND

    target_f = None
    for f in findings:
        if f["seq"] == seq:
            target_f = f
            break

    if not target_f:
        print(f"Finding not found: {job_id} seq {seq}", file=sys.stderr)
        return EXIT_NOT_FOUND

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

    f_obj = Finding(
        kind=target_f["kind"],
        severity=target_f["severity"],
        source=target_f["source"],
        data=target_f["data"],
        raw_line=target_f["raw_line"],
        request_context=target_f.get("request_context") or {},
    )

    if verbose:
        print(f"[verbose] target_url={target_url!r}", file=sys.stderr)
        print(f"[verbose] finding kind={f_obj.kind!r} data={f_obj.data!r}", file=sys.stderr)

    pkg_payloads = Path(__file__).resolve().parent.parent.parent / "data" / "payloads"
    validator = Validator(pkg_payloads)
    status, reason = validator.revalidate(f_obj, target_url=target_url)

    if verbose:
        print(f"[verbose] result status={status!r} reason={reason!r}", file=sys.stderr)

    core.store.update_verification(job_id, seq, status, reason=reason)
    print(f"[=] Retest status: {status.upper()}")
    print(f"    Reason: {reason}")
    return EXIT_OK
