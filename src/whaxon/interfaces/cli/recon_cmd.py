"""whaxon recon <target> — passive recon pass (DNS, SSL, headers, tech, etc.)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from whaxon.core import Core
from whaxon.core.dns_full_v2 import CAPABILITY_ID as DNS_FULL_CAPABILITY_ID
from whaxon.core.http_recon_v2 import CAPABILITY_ID as HTTPS_RECON_CAPABILITY_ID
from whaxon.core.recon_v2 import CAPABILITY_ID
from whaxon.core.tls_cert_v2 import CAPABILITY_ID as TLS_CERT_CAPABILITY_ID

EXIT_OK = 0
EXIT_OUT_OF_SCOPE = 1
EXIT_USAGE = 2
EXIT_ERROR = 3


def main(args: list[str] | None = None) -> int:
    args = list(args or [])
    data_dir = Path("data")
    checks: list[str] | None = None
    verbose = False
    engine = "legacy"
    plan_id: str | None = None
    positional: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--data" and i + 1 < len(args):
            data_dir = Path(args[i + 1]); i += 2
        elif a == "--checks" and i + 1 < len(args):
            checks = [c.strip() for c in args[i + 1].split(",") if c.strip()]
            i += 2
        elif a == "--engine" and i + 1 < len(args):
            engine = args[i + 1]; i += 2
        elif a == "--plan-id" and i + 1 < len(args):
            plan_id = args[i + 1]; i += 2
        elif a in ("-v", "--verbose"):
            verbose = True; i += 1
        elif a in ("-h", "--help"):
            _usage()
            return EXIT_OK
        else:
            positional.append(a); i += 1

    if len(positional) != 1 or engine not in {"legacy", "v2"}:
        _usage()
        return EXIT_USAGE
    if (engine == "v2" and (not plan_id or checks is not None)) or (
        engine == "legacy" and plan_id is not None
    ):
        _usage()
        return EXIT_USAGE

    target = positional[0]
    core = Core(data_dir)

    if verbose:
        print(f"[recon] target={target}", file=sys.stderr)
        print(f"[recon] data_dir={data_dir}", file=sys.stderr)
        print(f"[recon] checks={checks or 'all'}", file=sys.stderr)
        print(f"[recon] engine={engine}", file=sys.stderr)

    if engine == "v2":
        return _run_v2(core, target, plan_id or "", verbose=verbose)

    asyncio.run(core.initialize(drain=False))
    match = core.scope.check(target)
    if verbose:
        print(f"[recon] scope: allowed={match.allowed} reason={match.reason} rule={match.matched_rule}", file=sys.stderr)
    if not match.allowed:
        print(f"Out of scope: {target} ({match.reason})", file=sys.stderr)
        return EXIT_OUT_OF_SCOPE

    if verbose:
        print("[recon] running checks...", file=sys.stderr)
    job_id = core.recon.run(target, checks=checks)
    if verbose:
        print(f"[recon] job_id={job_id}", file=sys.stderr)
    if job_id is None:
        print(f"No findings for {target}", file=sys.stderr)
        return EXIT_OK

    findings = core.store.get_findings(job_id)
    print(f"recon: {target}  (job {job_id}, {len(findings)} findings)")
    for f in findings:
        print(f"  [{f['severity']:8s}] {f['kind']:28s} {f['raw_line'][:90]}")
        if verbose:
            print(f"    data: {f.get('data')}", file=sys.stderr)
            print(f"    remediation: {f.get('remediation', '')[:120]}", file=sys.stderr)
            print(f"    impact: {f.get('impact', '')[:120]}", file=sys.stderr)
    return EXIT_OK


def _run_v2(core: Core, target: str, plan_id: str, *, verbose: bool) -> int:
    """Run only a matching persisted DNS, TLS, or HTTPS task through Engine V2."""
    try:
        details = core.workflow_plan_details(plan_id)
    except (ValueError, TypeError, RuntimeError) as exc:
        print(f"V2 recon plan rejected: {exc}", file=sys.stderr)
        return EXIT_USAGE

    plan = details.get("plan")
    tasks = plan.get("tasks") if isinstance(plan, dict) else None
    if not isinstance(tasks, list) or len(tasks) != 1 or not isinstance(tasks[0], dict):
        print("V2 recon requires a persisted plan with exactly one task", file=sys.stderr)
        return EXIT_USAGE

    task = tasks[0]
    if (
        task.get("capability_id") not in {
            CAPABILITY_ID, DNS_FULL_CAPABILITY_ID, TLS_CERT_CAPABILITY_ID,
            HTTPS_RECON_CAPABILITY_ID,
        }
        or task.get("target") != target
        or task.get("inputs") != {}
        or task.get("depends_on", []) != []
    ):
        print(
            "V2 recon plan must contain one fixed DNS, TLS, or HTTPS task matching the target",
            file=sys.stderr,
        )
        return EXIT_USAGE

    try:
        async def execute():
            await core.initialize(drain=False)
            return await core.run_workflow_plan(plan_id)

        result = asyncio.run(execute())
        report = core.workflow_report(plan_id)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(f"V2 recon workflow failed: {exc}", file=sys.stderr)
        return EXIT_ERROR

    findings = report.get("findings", []) if isinstance(report, dict) else []
    result_tasks = result.get("tasks", [])
    status = (
        result_tasks[0].get("status", "unknown")
        if isinstance(result_tasks, list) and result_tasks
        and isinstance(result_tasks[0], dict)
        else "unknown"
    )
    print(f"recon: {target}  (plan {plan_id}, {status}, {len(findings)} findings)")
    for finding in findings:
        print(
            f"  [{finding.get('severity', 'info'):8s}] "
            f"{finding.get('kind', 'finding'):28s} "
            f"{finding.get('raw_line', '')[:90]}"
        )
    if verbose:
        print(f"V2 workflow complete={result.get('complete', False)}", file=sys.stderr)
    return (
        EXIT_OK
        if result.get("complete") and status == "succeeded"
        and report.get("status") == "complete"
        else EXIT_ERROR
    )


def _usage() -> None:
    print(
        "Usage: whaxon recon <target> [--data DIR] [--checks a,b,c]\n"
        "       whaxon recon <target> --engine v2 --plan-id ID [--data DIR]\n"
        "\n"
        "  Runs legacy passive checks or a fixed V2 DNS/TLS/HTTPS task against an in-scope target.\n"
        "  V2 requires one persisted DNS, TLS, or HTTPS plan with exact approval.\n"
        "\n"
        "  Available checks:\n"
        "    dns        A/AAAA/MX/NS/TXT/SOA records\n"
        "    ssl        TLS certificate, SANs, expiry\n"
        "    headers    missing security headers\n"
        "    tech       server framework / CMS detection\n"
        "    robots     /robots.txt and /sitemap.xml\n"
        "    security_txt  /.well-known/security.txt (RFC 9116)\n"
        "    cookies    Set-Cookie flag audit\n"
        "    redirects  redirect chain, HTTPS->HTTP downgrades\n"
        "    waf        WAF / CDN fingerprinting\n"
        "    dns_full   CAA, DMARC, SPF records\n"
        "\n"
        "  Default: all checks.",
        file=sys.stderr,
    )
