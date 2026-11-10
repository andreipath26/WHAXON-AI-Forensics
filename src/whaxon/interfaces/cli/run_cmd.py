"""whaxon run <tool> <target> — execute a catalog tool from the CLI.

Streams stdout/stderr live as the tool runs. Persists to the store the
same way the TUI and web UI do. Prints a findings summary on finish.

Usage:
    whaxon run <tool_id> <target> [options]

Options:
    --extra "..."          extra arguments passed to the tool
    --data DIR             data directory (default: ./data)
    --timeout SEC          hard timeout in seconds (default: 300)
    --allow-out-of-scope   unsupported: legacy scope override is disabled
    --quiet                suppress live output (just findings at the end)
    --verbose              print internal state, argv, and full untruncated findings
    --json                 emit findings as JSON to stdout at the end
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from whaxon.core import Core
from whaxon.core.events import JobFailed, JobFindings, JobFinished, JobOutput, JobStarted
from whaxon.core.scope import OutOfScopeError

EXIT_OK = 0
EXIT_TOOL_ERROR = 1
EXIT_OUT_OF_SCOPE = 2
EXIT_UNKNOWN_TOOL = 3
EXIT_USAGE = 64


def _usage() -> None:
    print("Usage: whaxon run <tool_id> <target> [--extra \"...\"] [--data DIR] "
          "[--timeout SEC] [--allow-out-of-scope] [--quiet] [--verbose] [--json]")
    print()
    print("  Legacy direct execution is disabled; use whaxon workflow for V2 authorization.")
    print("  Examples:")
    print("    whaxon run nmap 10.0.0.5")
    print("    whaxon run nikto 10.0.0.5 --extra \"-p 80,443\"")
    print("    whaxon run nmap 10.0.0.5 --quiet --json")


def _print_findings(findings, as_json: bool, verbose: bool = False) -> None:
    if as_json:
        print(json.dumps(findings, indent=2, default=str))
        return
    if not findings:
        print()
        print("[no findings]")
        return
    print()
    print(f"[{len(findings)} findings]")
    for f in findings:
        if hasattr(f, "to_dict"):
            f = f.to_dict()
        sev = (f.get("severity") or "info").upper()
        kind = f.get("kind") or "?"
        raw = (f.get("raw_line") or "").strip().replace("\n", " ")
        if not verbose:
            raw = raw[:120]
        print(f"  [{sev:8s}] {kind:20s} {raw}")


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    if not args or args[0] in ("-h", "--help"):
        _usage()
        return

    # Positional: tool_id, target
    tool_id = args[0]
    if len(args) < 2 or args[1].startswith("--"):
        print("error: whaxon run requires a <tool_id> and a <target>", file=sys.stderr)
        _usage()
        sys.exit(EXIT_USAGE)
    target = args[1]

    extra_args = ""
    data_dir = Path("data")
    timeout_s = 300.0
    allow_out_of_scope = False
    quiet = False
    as_json = False
    verbose = False

    i = 2
    while i < len(args):
        a = args[i]
        if a == "--extra" and i + 1 < len(args):
            extra_args = args[i + 1]; i += 2
        elif a == "--data" and i + 1 < len(args):
            data_dir = Path(args[i + 1]); i += 2
        elif a == "--timeout" and i + 1 < len(args):
            try:
                timeout_s = float(args[i + 1])
            except ValueError:
                print(f"error: --timeout expects a number, got {args[i+1]!r}", file=sys.stderr)
                sys.exit(EXIT_USAGE)
            i += 2
        elif a == "--allow-out-of-scope":
            allow_out_of_scope = True; i += 1
        elif a == "--quiet":
            quiet = True; i += 1
        elif a == "--json":
            as_json = True; i += 1
        elif a == "--verbose":
            verbose = True; i += 1
        else:
            print(f"Unknown arg: {a}", file=sys.stderr)
            sys.exit(EXIT_USAGE)

    # The legacy runner cannot prove V2 plan identity, approval binding,
    # durable task ownership or recovery. Never dispatch it from this command.
    # Retain argument parsing for compatibility, but fail closed before Core
    # initialization (which may have unrelated side effects).
    print(
        "error: legacy direct execution is disabled; create an authorized "
        "Engine V2 plan with 'whaxon workflow' instead",
        file=sys.stderr,
    )
    sys.exit(EXIT_TOOL_ERROR)


if __name__ == "__main__":
    main()