"""whaxon doctor --plan: print a read-only remediation preview."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from whaxon.core.dependencies import collect_dependency_report
from whaxon.core.remediation import build_remediation_plan


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="whaxon doctor",
        description="Read-only environment and dependency readiness report.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Print the versioned machine-readable report.")
    parser.add_argument("--check", metavar="DEPENDENCY_ID",
                        help="Show one dependency only (read-only).")
    parser.add_argument("--plan", action="store_true",
                        help="Generate a remediation preview; never executes commands.")
    parser.add_argument("--data", type=Path, default=Path("data"),
                        help="WHAXON data directory (default: ./data).")
    parser.add_argument("--core-only", action="store_true",
                        help="Skip optional Python extras and external tool checks.")
    ns = parser.parse_args(args)
    if ns.plan:
        plan = build_remediation_plan(
            dependency_ids=[ns.check] if ns.check else None,
            data_dir=ns.data,
        )
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 2 if plan["unknown_dependency_ids"] else 0
    report = collect_dependency_report(
        data_dir=ns.data,
        include_optional=not ns.core_only,
        include_external=not ns.core_only,
    )
    if ns.check:
        matches = [d for d in report["dependencies"] if d["id"] == ns.check]
        if not matches:
            print(f"Unknown dependency id: {ns.check}")
            return 2
        report["dependencies"] = matches
        report["summary"] = {"total": 1, "ready": sum(d["status"] == "READY" for d in matches)}
        report["overall_status"] = (
            "READY" if all(d["status"] == "READY" for d in matches) else "DEGRADED"
        )
    if ns.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        env = report["environment"]
        print(f"WHAXON environment readiness: {report['overall_status']}")
        print(f"Platform: {env['os']} {env['os_release']} ({env['architecture']})")
        print(f"Python:   {env['python']} — {env['python_executable']}")
        print(f"Venv:     {'yes' if env['virtual_environment'] else 'no'}")
        print()
        print(f"{'STATUS':14} {'ID':20} {'VERSION / PATH':34} REASON")
        for dep in report["dependencies"]:
            observed = dep.get("detected_version") or dep.get("detected_path") or "-"
            print(f"{dep['status']:14} {dep['id'][:20]:20} {observed[:34]:34} {dep['reason']}")
        print()
        print("This command is read-only. No packages were installed and no network was used.")
        print("Use --plan for a remediation preview; it also does not execute commands.")
    return 1 if report["overall_status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
