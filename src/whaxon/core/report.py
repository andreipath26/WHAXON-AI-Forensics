"""Engagement report generation.

Reads from the WHAXON store and produces a Markdown or JSON report
covering every job and finding in an engagement.
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any

# Severities in report order.
_URL_RE = __import__("re").compile(r"https?://[^\s<>\"']+")


def _truncate_preserving_urls(text: str, limit: int = 200) -> str:
    """Truncate text to `limit` chars, but never cut a URL mid-string.

    A URL that starts before `limit` is kept whole even if it pushes
    the result past `limit`. Non-URL text is truncated normally.
    """
    if not text or len(text) <= limit:
        return text
    # find any URL that would be cut by a hard truncation
    for m in _URL_RE.finditer(text):
        if m.start() < limit < m.end():
            # keep up to end of this URL, plus a short tail marker
            return text[:m.end()] + "..."
    return text[:limit] + "..."


_SEV_ORDER = ["critical", "high", "medium", "low", "info"]

# Loot-kind findings get a dedicated section.
_SESSION_SOURCES = {"msf_sysinfo", "msf_getuid", "msf_hashdump"}

_LOOT_KINDS = {
    "env_var", "sysinfo", "platform", "ntlm_hash", "service",
    "msf_session", "network_iface", "system_section",
    "exploit_suggestion", "msf_loot", "msf_loot_file",
}


_TEST_TOOLS = {"echo"}
_TEST_TARGETS = {
    "evil.com", "hi", "hello", "persist-test", "kioo",
    "ww.google.com", "prod.example.com",
}


def _is_test_job(job: dict) -> bool:
    """True for fixture jobs that must not appear in a client report."""
    if (job.get("tool") or "").lower() in _TEST_TOOLS:
        return True
    t = (job.get("target") or "").strip().lower()
    if t in _TEST_TARGETS:
        return True
    return bool(t.startswith("prod.example.com"))


def _load(store, engagement: str | None, limit: int = 500) -> dict[str, Any]:
    """Collect all jobs + findings for an engagement into one dict."""
    from .store import _signature_for
    all_jobs = store.history(limit=limit)
    jobs = [j for j in all_jobs if not _is_test_job(j)]
    entries = []
    sev_counts = {s: 0 for s in _SEV_ORDER}
    loot_items = []
    session_findings = []
    # Deduped findings across all jobs. Key is (kind, signature) —
    # target is not part of the key because the report is per-engagement,
    # not per-target. Duplicates accumulate a count and a job list.
    unique_findings: list[dict] = []
    seen: dict[tuple, int] = {}
    for j in jobs:
        findings = store.get_findings(j["id"]) or []
        entries.append({
            "job": j,
            "findings": findings,
        })
        for f in findings:
            sev = (f.get("severity") or "info").lower()
            kind = f.get("kind") or ""
            data = f.get("data") or {}
            try:
                sig = _signature_for(kind, data)
            except Exception:
                sig = (f.get("raw_line") or "")[:120]
            key = (kind, sig)
            if key in seen:
                idx = seen[key]
                unique_findings[idx]["count"] += 1
                unique_findings[idx].setdefault("job_ids", []).append(j["id"])
                continue
            entry = dict(f)
            entry["count"] = 1
            entry["job_ids"] = [j["id"]]
            seen[key] = len(unique_findings)
            unique_findings.append(entry)
            if sev in sev_counts:
                sev_counts[sev] += 1
            if f.get("kind") in _LOOT_KINDS:
                loot_items.append({**f, "_job_id": j["id"]})
            if f.get("source") in _SESSION_SOURCES:
                session_findings.append({**f, "_job_id": j["id"]})
    ai_runs = _load_ai_runs(store)
    return {
        "unique_findings": unique_findings,
        "engagement": engagement or "default",
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "job_count": len(jobs),
        "finding_count": len(unique_findings),
        "raw_finding_count": sum(1 for e in entries for _ in e["findings"]),
        "severity_counts": sev_counts,
        "jobs": entries,
        "loot": loot_items,
        "session_findings": session_findings,
        "ai_runs": ai_runs,
    }


def _load_ai_runs(store, limit: int = 20) -> list[dict[str, Any]]:
    """Collect recent AI runs with their phase + phase_history."""
    try:
        summaries = store.list_ai_runs(limit=limit) or []
    except Exception:
        return []
    runs = []
    for summary in summaries:
        rid = summary.get("id")
        if not rid:
            continue
        try:
            full = store.get_ai_run(rid) or {}
        except Exception:
            full = {}
        runs.append({
            "id": rid,
            "goal": summary.get("goal", ""),
            "status": summary.get("status", ""),
            "phase": full.get("phase") or summary.get("phase") or "recon",
            "phase_history": full.get("phase_history") or "[]",
            "step_count": len(full.get("steps") or []),
        })
    return runs


def _md_ai_runs(md: list[str], runs: list[dict]) -> None:
    if not runs:
        return
    md.append("## AI Runs\n")
    md.append("| Run | Goal | Phase | Status | Steps |")
    md.append("|-----|------|-------|--------|-------|")
    for r in runs:
        goal = (r.get("goal") or "").replace("|", "/")[:60]
        rid = r["id"]
        phase = r["phase"]
        status = r["status"]
        steps = r["step_count"]
        md.append(f"| `{rid}` | {goal} | {phase} | {status} | {steps} |")
    md.append("")
    for r in runs:
        try:
            hist = json.loads(r.get("phase_history") or "[]")
        except Exception:
            hist = []
        if len(hist) > 1:
            path = " -> ".join(h.get("phase", "?") for h in hist)
            rid = r["id"]
            md.append(f"- `{rid}` phase history: {path}")
    md.append("")


def _md_session_findings(md: list[str], findings: list[dict]) -> None:
    if not findings:
        return
    md.append("## Session Findings")
    md.append("Findings collected by acting inside an established Metasploit session.")
    md.append("")
    md.append("| Source | Detail | Session | Job |")
    md.append("|--------|--------|---------|-----|")
    for f in findings:
        d = f.get("data") or {}
        kind = f.get("kind") or ""
        if kind == "sysinfo":
            detail = str(d.get("field", "")) + ": " + str(d.get("value", ""))
        elif kind == "ntlm_hash":
            detail = str(d.get("user", "")) + " NT=" + str(d.get("nt_hash", ""))
        else:
            detail = (f.get("raw_line") or "")[:120]
        src = f.get("source", "")
        sid = d.get("session_id", "")
        job = f.get("_job_id", "")
        md.append("| " + str(src) + " | " + detail + " | " + str(sid) + " | " + str(job) + " |")
    md.append("")


def _md_exec_summary(md, report):
    """Write a short deterministic narrative executive summary."""
    counts = report.get("severity_counts") or {}
    unique = report.get("unique_findings") or []
    job_count = report.get("job_count", 0)
    targets = {e["job"].get("target") for e in report.get("jobs", []) if e["job"].get("target")}
    target_count = len(targets)

    md.append("## Executive Summary" + chr(10))


    for sev in _SEV_ORDER:
        n = counts.get(sev, 0)
        if n <= 0:
            continue
        if sev == "critical":
            md.append(f"This engagement found **{n} critical** findings across {target_count} targets ({job_count} jobs).")
        elif sev == "high":
            md.append(f"No critical findings. **{n} high**-severity findings were identified across {target_count} targets.")
        elif sev in ("medium", "low"):
            md.append(f"No critical or high findings. **{n} {sev}**-severity items require attention.")
        else:
            md.append(f"Only informational findings ({n}).")
        break
    md.append("")

    _sev_idx = {s: i for i, s in enumerate(_SEV_ORDER)}
    _bi_idx = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    top = sorted(
        [f for f in unique
         if (f.get("severity") or "").lower() in ("critical", "high")
         or (f.get("business_impact") or "").lower() in ("critical", "high")],
        key=lambda f: (
            _bi_idx.get((f.get("business_impact") or "").lower(), 99),
            _sev_idx.get((f.get("severity") or "info").lower(), 99),
        ),
    )[:3]
    if top:
        md.append("**Top findings:**" + chr(10))

        for f in top:
            raw = (f.get("raw_line") or "").strip().replace(chr(10), " ")[:140]
            count = f.get("count", 1)
            suffix = f" (seen {count}x)" if count > 1 else ""
            _sev_label = f.get('severity', '?')
            _bi = f.get("business_impact")
            if _bi:
                _sev_label = str(_sev_label) + " / Business: " + str(_bi)
            md.append(f"- [{_sev_label}] {raw}{suffix}")
        md.append("")

    if top:
        rem = (top[0].get("remediation") or "").strip()
        if rem:
            md.append(f"**Recommended action:** {rem}")
            md.append("")

    md.append("### Findings by severity" + chr(10))

    for sev in _SEV_ORDER:
        n = counts.get(sev, 0)
        if n:
            md.append(f"- **{sev.capitalize()}**: {n}")
    md.append("")


def _md_loot(md: list[str], loot: list[dict]) -> None:
    by_kind: dict[str, list[dict]] = {}
    for f in loot:
        by_kind.setdefault(f.get("kind", "loot"), []).append(f)
    if not by_kind:
        return
    md.append("## Loot Summary\n")
    for kind in sorted(by_kind):
        items = by_kind[kind]
        md.append(f"### {kind} ({len(items)})\n")
        md.append("| Detail | Job |")
        md.append("|--------|-----|")
        for f in items:
            d = f.get("data") or {}
            if kind == "env_var":
                detail = f"{d.get('name','')} = {d.get('value','')}"
            elif kind in ("sysinfo", "platform"):
                detail = f"{d.get('field','platform')}: {d.get('value') or d.get('platform','')}"
            elif kind == "ntlm_hash":
                detail = f"{d.get('user','')} NT={d.get('nt_hash','')}"
            elif kind == "service":
                detail = f"{d.get('port','')}/{d.get('proto','')} {d.get('state','')} {d.get('name','')}"
            elif kind == "msf_session":
                detail = f"session {d.get('session_id','')} on {d.get('host','')}"
            elif kind == "exploit_suggestion":
                detail = f"{d.get('module_type','')}/{d.get('module','')}"
            elif kind == "network_iface":
                detail = f"{d.get('ip','')}/{d.get('cidr','')}"
            else:
                detail = _truncate_preserving_urls(f.get("raw_line") or json.dumps(d), 200)
            # escape pipes
            detail = detail.replace("|", "\\|")
            md.append(f"| {detail} | {f.get('_job_id','')} |")
        md.append("")


def _md_coverage(md, report):
    """Render coverage gaps across jobs, grouped by PTES phase."""
    from collections import defaultdict
    by_phase: dict[str, list] = defaultdict(list)
    total = 0
    for entry in report.get("jobs", []):
        for c in entry.get("coverage") or []:
            phase = (c.get("phase") or "unphased").strip() or "unphased"
            by_phase[phase].append(c)
            total += 1
    if total == 0:
        return

    md.append("## Coverage Gaps\n")
    md.append("The following checks were skipped. They are not vulnerabilities; "
              "they are the parts of the target that were not tested. "
              "Grouped by PTES phase.\n")

    md.append("| PTES Phase | Count |")
    md.append("| --- | --- |")
    for phase in sorted(by_phase):
        md.append(f"| {phase} | {len(by_phase[phase])} |")
    md.append("")

    for phase in sorted(by_phase):
        md.append(f"### Phase: {phase} ({len(by_phase[phase])})\n")
        for c in by_phase[phase]:
            md.append(f"- **{c['kind']}** — {c['tool_id']} against `{c['target']}`: {c['detail']}")
        md.append("")


def to_markdown(report: dict[str, Any], chains: list | None = None,
                all_findings: bool = False, lookup: bool = True) -> str:
    md: list[str] = []
    md.append("# WHAXON Engagement Report\n")
    md.append(f"Scope: **{report['engagement']}**  ")
    md.append(f"Generated: {report['generated']}  ")
    md.append(f"Jobs: {report['job_count']}  Findings: {report['finding_count']}\n")

    _md_exec_summary(md, report)
    _md_remediation_roadmap(md, report)

    _md_loot(md, report["loot"])
    _md_session_findings(md, report.get("session_findings") or [])
    _md_chains(md, chains or [], heading="## Attack Surface")
    if lookup:
        _md_lookup(md, report)
    _md_coverage(md, report)
    _md_ai_runs(md, report.get("ai_runs") or [])

    _md_findings_appendix(md, report, all_findings)
    _md_job_history_appendix(md, report)

    return "\n".join(md)



# Cache searchsploit results within a single report render.
_LOOKUP_CACHE: dict = {}


def _searchsploit_json(hint, timeout=10.0):
    """Run searchsploit --json <hint>. Returns parsed dict or None."""
    if hint in _LOOKUP_CACHE:
        return _LOOKUP_CACHE[hint]
    import json as _json
    import shutil
    import subprocess
    if shutil.which("searchsploit") is None:
        _LOOKUP_CACHE[hint] = None
        return None
    try:
        r = subprocess.run(
            ["searchsploit", "--json", hint],
            capture_output=True, text=True, timeout=timeout,
        )
        if not r.stdout.strip():
            _LOOKUP_CACHE[hint] = None
            return None
        data = _json.loads(r.stdout)
        _LOOKUP_CACHE[hint] = data
        return data
    except Exception:
        _LOOKUP_CACHE[hint] = None
        return None


def _md_lookup(md, report, per_hint_limit=5):
    """Render a Known Vulnerabilities section for findings with hints."""
    hints = set()
    for entry in report.get("jobs") or []:
        for f in entry.get("findings") or []:
            h = (f.get("lookup_hint") or "").strip()
            if h:
                hints.add(h)
    if not hints:
        return

    md.append("## Known Vulnerabilities\n")
    md.append(
        "Service versions detected during the engagement, cross-referenced "
        "against the local Exploit-DB mirror. This is a starting point for "
        "manual review, not a definitive list.\n"
    )

    for hint in sorted(hints):
        data = _searchsploit_json(hint)
        md.append("### " + hint + "\n")
        if not data:
            md.append("_No local searchsploit results (mirror may be stale)._")
            md.append("")
            continue
        rows = data.get("RESULTS_EXPLOIT") or []
        if not rows:
            md.append("_No results._")
            md.append("")
            continue
        md.append("Matches: " + str(len(rows)))
        md.append("")
        md.append("| EDB-ID | Title | CVEs |")
        md.append("|--------|-------|------|")
        for row in rows[:per_hint_limit]:
            eid = row.get("EDB-ID", "?")
            title = (row.get("Title") or "")[:70].replace("|", "\\|")
            codes = row.get("Codes") or ""
            cves = ",".join(
                c.strip() for c in codes.split(";")
                if c.strip().upper().startswith("CVE-")
            )
            md.append("| " + eid + " | " + title + " | " + cves + " |")
        if len(rows) > per_hint_limit:
            md.append("")
            md.append("_" + str(len(rows) - per_hint_limit) + " more results not shown._")
        md.append("")


def _md_chains(md, chains, heading="## Pivot Chains"):
    """Render the pivot chain tree into the report."""
    if not chains:
        return
    md.append(heading + "\n")
    for c in chains:
        root = c.get("root", {})
        md.append(f"- **{root.get('kind','?')} `{root.get('id','?')}`**"
                  + (f" — {root.get('evidence','')}" if root.get("evidence") else ""))
        for d in c.get("descendants", []):
            rel = d.get("relation", "?")
            arrow = "→" if rel == "from_exploit" else "↳"
            child = d.get("child", {})
            ev = d.get("evidence", "")
            line = f"  {arrow} {child.get('kind','?')} `{child.get('id','?')}`"
            if ev:
                line += f"  ({ev})"
            md.append(line)
    md.append("")

def to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, default=str)



# ─── CLI entrypoints (per-job reports) ──────────────────────────────

def _md_next_steps(md: list, findings: list) -> None:
    """Render suggestion-kind findings as a Next steps section."""
    suggestions = [f for f in findings if f.get('kind') == 'suggestion']
    if not suggestions:
        return
    md.append('## Next steps\n')
    for f in suggestions:
        d = f.get('data') or {}
        label = d.get('label') or f.get('raw_line') or 'unspecified'
        tool = d.get('tool') or ''
        extra = d.get('extra_args') or ''
        line = '- ' + label
        if tool:
            line += '  (tool: `' + tool + '`'
            if extra:
                line += ', args: `' + extra + '`'
            line += ')'
        md.append(line)
    md.append('')


def render_markdown(job: dict, findings: list[dict]) -> str:
    """Render a single job + its findings as Markdown. Used by whaxon report."""
    md: list[str] = []
    md.append(f"# Job {job.get('id','')}\n")
    md.append(f"- **Tool**: {job.get('tool','')}")
    md.append(f"- **Target**: {job.get('target','')}")
    md.append(f"- **Status**: {job.get('status','')}  exit={job.get('exit_code','')}")
    md.append(f"- **Started**: {job.get('started_at','')}")
    md.append("")
    if findings:
        md.append(f"## Findings ({len(findings)})\n")
        for f in findings:
            sev = (f.get('severity') or 'info').upper()
            raw = (f.get('raw_line') or '').strip().replace('\n', ' ')
            raw = ' '.join(raw.split())[:500]
            md.append(f"- **[{sev}]** `{f.get('kind','')}` — {raw}")
        md.append("")
        _md_next_steps(md, findings)
    else:
        md.append("_No findings recorded._\n")
    return "\n".join(md)


def render_html(job: dict, findings: list[dict]) -> str:
    """Same as render_markdown but wrapped in a <pre> so a browser renders it.

    The markdown (including raw_line, which may contain attacker-controlled
    text from tool output) is HTML-escaped before wrapping. Without this,
    a raw_line containing "<script>" would be interpreted by the browser.
    """
    import html as _html
    md = render_markdown(job, findings)
    return (
        "<pre style=\"font-family:ui-monospace,monospace\">"
        + _html.escape(md)
        + "</pre>"
    )


_TEMPLATE_DIR = Path(__file__).parent


def _load_config_meta(overrides=None):
    import os

    from whaxon.core.scope import ScopeManager
    ov = overrides or {}
    client = ov.get("client") or ""
    classification = ov.get("classification") or "Confidential"
    prepared_by = ov.get("prepared_by") or os.environ.get("WHAXON_REPORT_PREPARED_BY", "")
    try:
        sm = ScopeManager(Path("data") / "scope.json")
        sm.load()
        data = sm.summary() if hasattr(sm, "summary") else {}
        client = ov.get("client") or data.get("client") or client
        classification = ov.get("classification") or data.get("classification") or classification
    except Exception:
        pass
    return {"client": client, "classification": classification, "prepared_by": prepared_by}


def _escape_html(s):
    import html as _h
    return _h.escape(str(s if s is not None else ""))

def _safe_count(value, fallback=0):
    """Convert report counters to bounded non-negative integers."""
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        try:
            return max(0, int(fallback))
        except (TypeError, ValueError, OverflowError):
            return 0


def _md_to_text_exec(report):
    md = []
    _md_exec_summary(md, report)
    return chr(10).join(md)


def _md_to_text_roadmap(report):
    md = []
    _md_remediation_roadmap(md, report)
    return chr(10).join(md)


def _md_to_text_appendix(report):
    md = []
    _md_findings_appendix(md, report, all_findings=True)
    return chr(10).join(md)


def _html_finding_card(f: dict[str, Any], index: int) -> str:
    severity = str(f.get("severity") or "info").lower()
    if severity not in _SEV_ORDER:
        severity = "info"
    verification = str(f.get("verification_status") or "candidate").lower()
    if verification not in {"verified", "refuted", "candidate", "inconclusive"}:
        verification = "candidate"

    title = f.get("kind") or "Finding"
    target = f.get("target") or "Target not recorded"
    source = f.get("source") or "Source not recorded"
    evidence = f.get("raw_line") or "No raw observation was recorded."
    remediation = f.get("remediation") or ""
    proof = f.get("proof") or ""
    job_ids = [str(value) for value in (f.get("job_ids") or [])]
    count = _safe_count(f.get("count"), 1)
    search = _escape_html(" ".join(
        str(value) for value in (title, target, source, evidence, remediation)
    ).lower())

    tags = [
        f'<span class="tag tag-severity {severity}">{severity.upper()}</span>',
        f'<span class="tag tag-verification {verification}">{_escape_html(verification)}</span>',
        f'<span class="tag">Target: {_escape_html(target)}</span>',
        f'<span class="tag">Source: {_escape_html(source)}</span>',
    ]
    for key, label in (("cve", None), ("cvss", "CVSS"), ("epss", "EPSS")):
        value = f.get(key)
        if value is not None:
            text = _escape_html(value if label is None else f"{label} {value}")
            tags.append(f'<span class="tag">{text}</span>')
    if f.get("kev"):
        tags.append('<span class="tag tag-kev">Known exploited</span>')
    if f.get("business_impact"):
        tags.append(
            f'<span class="tag">Business impact: '
            f'{_escape_html(f.get("business_impact"))}</span>'
        )
    if count > 1:
        tags.append(f'<span class="tag">Observed {count} times</span>')

    attributed = (
        ", ".join(f"<code>{_escape_html(value)}</code>" for value in job_ids)
        if job_ids else "Job attribution unavailable"
    )
    priority = _BAND_LABELS[_priority_band(f)]
    parts = [
        f'<article class="finding-card severity-{severity}" data-report-search="{search}">',
        f'<div class="finding-number">F{index:03d}</div>',
        '<div class="finding-content">',
        '<div class="finding-title-row"><div><p class="eyebrow">Recorded finding</p>',
        f'<h3>{_escape_html(title)}</h3></div>',
        f'<span class="priority">{_escape_html(priority)} priority</span></div>',
        '<div class="finding-meta">' + "".join(tags) + "</div>",
        '<div class="finding-columns">',
        '<section><h4>Evidence recorded</h4>',
        f"<pre>{_escape_html(evidence)}</pre>",
        f'<p class="muted">Verification: <strong>{_escape_html(verification)}</strong>'
        f' by {_escape_html(f.get("verified_by") or "engine")}.</p>',
    ]
    reason = f.get("verification_reason")
    if reason:
        parts.append(f'<p class="muted">{_escape_html(reason)}</p>')
    parts.extend([
        "</section>",
        "<section><h4>Recommended remediation</h4>",
        f"<p>{_escape_html(remediation) if remediation else 'No remediation guidance was recorded.'}</p>",
        f'<p class="muted">Recorded in: {attributed}</p>',
    ])
    if proof:
        parts.extend([
            '<h4 class="subheading">Reproduction material</h4>',
            '<p class="muted">Review scope and safety before running recorded material.</p>',
            f"<pre>{_escape_html(proof)}</pre>",
        ])
    parts.extend(["</section>", "</div>", "</div>", "</article>"])
    return "".join(parts)


def _html_findings(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return (
            '<div class="empty-state"><h3>No findings are available in this snapshot</h3>'
            "<p>Review the recorded job history and coverage section. An empty finding "
            "list does not establish that the targets are free of vulnerabilities.</p></div>"
        )
    ranks = {severity: index for index, severity in enumerate(_SEV_ORDER)}
    ordered = sorted(findings, key=lambda f: (
        _BAND_ORDER.index(_priority_band(f)),
        ranks.get(str(f.get("severity") or "info").lower(), 99),
        str(f.get("kind") or "").casefold(),
        str(f.get("target") or "").casefold(),
    ))
    return "".join(
        _html_finding_card(finding, index)
        for index, finding in enumerate(ordered, start=1)
    )


def _html_report_entries(report: dict[str, Any]) -> list[dict[str, Any]]:
    raw_entries: Any = report.get("jobs") or []
    if not isinstance(raw_entries, list):
        return []
    entries: list[dict[str, Any]] = []
    for entry in raw_entries:
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def _html_job_record(entry: dict[str, Any]) -> dict[str, Any]:
    job = entry.get("job")
    if isinstance(job, dict):
        return job
    return entry


def _html_coverage(report: dict[str, Any]) -> str:
    gaps: list[dict[str, Any]] = []
    for entry in _html_report_entries(report):
        job = _html_job_record(entry)
        coverage: Any = entry.get("coverage") or job.get("coverage") or []
        if isinstance(coverage, list):
            gaps.extend(gap for gap in coverage if isinstance(gap, dict))
    if not gaps:
        return (
            '<div class="empty-state"><p>No coverage gaps were recorded for this report.</p>'
            '<p class="muted">This does not prove that every relevant check was performed.</p></div>'
        )
    rows: list[str] = []
    for gap in gaps:
        values = (
            gap.get("phase") or "Unphased",
            gap.get("kind") or "Unknown",
            gap.get("tool_id") or "Unknown",
            gap.get("target") or "Unknown",
            gap.get("detail") or "",
        )
        rows.append(
            "<tr>" + "".join(f"<td>{_escape_html(value)}</td>" for value in values) + "</tr>"
        )
    return (
        '<p class="section-intro">These are persisted records of checks that were skipped '
        "or otherwise not completed. They are not vulnerability findings.</p>"
        '<div class="table-scroll"><table><thead><tr><th>Phase</th><th>Result</th>'
        "<th>Check</th><th>Target</th><th>Reason</th></tr></thead><tbody>"
        + "".join(rows) + "</tbody></table></div>"
    )


def _html_activity(report: dict[str, Any]) -> str:
    rows: list[str] = []
    for entry in _html_report_entries(report):
        job = _html_job_record(entry)
        exit_code = job.get("exit_code")
        rows.append(
            "<tr>"
            f"<td><code>{_escape_html(job.get('id') or 'Unknown')}</code></td>"
            f"<td>{_escape_html(job.get('tool') or 'Unknown')}</td>"
            f"<td>{_escape_html(job.get('target') or 'Unknown')}</td>"
            f"<td>{_escape_html(job.get('status') or 'Unknown')}</td>"
            f"<td>{_escape_html(job.get('started_at') or 'Not recorded')}</td>"
            f"<td>{_escape_html(exit_code if exit_code is not None else '—')}</td>"
            "</tr>"
        )
    if not rows:
        return '<div class="empty-state"><p>No job history was recorded.</p></div>'
    return (
        '<div class="table-scroll"><table><thead><tr><th>Job ID</th><th>Tool</th>'
        "<th>Target</th><th>Status</th><th>Started</th><th>Exit</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _html_overview(report: dict[str, Any], findings: list[dict[str, Any]]) -> tuple[str, str]:
    entries = _html_report_entries(report)
    targets: set[str] = set()
    for entry in entries:
        job = _html_job_record(entry)
        if job.get("target"):
            targets.add(str(job["target"]))

    finding_count = _safe_count(report.get("finding_count"), len(findings))
    job_count = _safe_count(report.get("job_count"), len(entries))
    raw_count = _safe_count(
        report.get("raw_finding_count"),
        sum(_safe_count(f.get("count"), 1) for f in findings),
    )
    verification = {
        "verified": sum(1 for f in findings if f.get("verification_status") == "verified"),
        "candidate": sum(
            1 for f in findings
            if f.get("verification_status") in (None, "", "candidate", "inconclusive")
        ),
        "refuted": sum(1 for f in findings if f.get("verification_status") == "refuted"),
    }
    counts = report.get("severity_counts")
    if not isinstance(counts, dict):
        counts = {}
        for finding in findings:
            severity = str(finding.get("severity") or "info").lower()
            if severity in _SEV_ORDER:
                counts[severity] = counts.get(severity, 0) + 1
    counts = {severity: _safe_count(counts.get(severity)) for severity in _SEV_ORDER}
    highest = next((severity for severity in _SEV_ORDER if counts[severity]), None)

    if finding_count:
        summary = (
            f"WHAXON recorded {finding_count} unique finding(s) across {job_count} "
            f"recorded job(s) and {len(targets)} distinct target(s)."
        )
        if highest:
            summary += f" Highest recorded severity: {highest}."
        summary += (
            f" {verification['verified']} are marked verified, "
            f"{verification['candidate']} remain candidate or inconclusive, and "
            f"{verification['refuted']} are marked refuted."
        )
    else:
        summary = (
            f"No findings were recorded across {job_count} recorded job(s) and "
            f"{len(targets)} distinct target(s). This is a snapshot of recorded work, "
            "not proof that the targets are free of vulnerabilities."
        )

    metrics = [
        ("Unique findings", finding_count, "Deduplicated records"),
        ("Recorded observations", raw_count, "Before report-level deduplication"),
        ("Jobs", job_count, "Included in this snapshot"),
        ("Targets", len(targets), "Represented in recorded jobs"),
    ]
    cards = "".join(
        '<div class="metric-card"><span class="metric-label">'
        + _escape_html(label)
        + '</span><strong class="metric-value">'
        + str(value)
        + '</strong><span class="metric-note">'
        + _escape_html(note)
        + "</span></div>"
        for label, value, note in metrics
    )
    severities = "".join(
        '<div class="severity-row"><span class="severity-name">'
        f'<span class="severity-dot {severity}"></span>{severity.capitalize()}</span>'
        f"<strong>{counts[severity]}</strong></div>"
        for severity in _SEV_ORDER
    )
    overview = (
        f'<p class="executive-summary">{_escape_html(summary)}</p>'
        f'<div class="metric-grid">{cards}</div>'
        '<div class="severity-panel"><h3>Severity distribution</h3>'
        f'<div class="severity-list">{severities}</div>'
        '<p class="muted">Severity values reproduce recorded labels; they are not '
        "independent validation results.</p></div>"
    )
    label = (
        f"{finding_count} unique finding from {job_count} recorded job"
        if finding_count == 1 and job_count == 1
        else f"{finding_count} unique findings from {job_count} recorded jobs"
    )
    return overview, label


def to_html(report, overrides=None, static=False):
    """Render a complete server-filled report for screen and PDF output.

    The static parameter remains accepted for compatibility. Rendering is
    server-side so PDF generation contains the same substantive content.
    """
    import json
    import os
    from pathlib import Path

    from whaxon.core.business_impact import cost_range

    findings = []
    for finding in (report.get("unique_findings") or []):
        if not isinstance(finding, dict):
            continue
        item = dict(finding)
        estimate = cost_range(item)
        if estimate:
            item["cost_range"] = estimate
        findings.append(item)

    overview, finding_summary = _html_overview(report, findings)
    options = overrides if isinstance(overrides, dict) else {}
    engagement = report.get("engagement") or "default"
    metadata = {
        "client": options.get("client") or report.get("client") or "Not specified",
        "classification": options.get("classification")
        or report.get("classification")
        or "Confidential",
        "prepared_by": options.get("prepared_by")
        or report.get("prepared_by")
        or os.environ.get("WHAXON_REPORT_PREPARED_BY")
        or "Not specified",
        "generated": report.get("generated") or "Not recorded",
    }
    payload = dict(report)
    payload["unique_findings"] = findings
    safe_json = (
        json.dumps(payload, default=str)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
    template = (Path(__file__).parent / "report.html").read_text(encoding="utf-8")
    values = {
        "TITLE": _escape_html(engagement),
        "CLIENT": _escape_html(metadata["client"]),
        "CLASSIFICATION": _escape_html(metadata["classification"]),
        "PREPARED_BY": _escape_html(metadata["prepared_by"]),
        "GENERATED": _escape_html(metadata["generated"]),
        "FINDING_SUMMARY": _escape_html(finding_summary),
        "OVERVIEW": overview,
        "FINDINGS": _html_findings(findings),
        "COVERAGE": _html_coverage(report),
        "ACTIVITY": _html_activity(report),
        "REPORT_JSON": safe_json,
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def _build_job_report(job, findings):
    counts = {}
    for f in findings:
        sev = (f.get("severity") or "info").lower()
        counts[sev] = counts.get(sev, 0) + 1
    return {
        "engagement": job.get("id", ""),
        "generated": job.get("started_at", ""),
        "job_count": 1,
        "finding_count": len(findings),
        "severity_counts": counts,
        "unique_findings": findings,
        "jobs": [{"job": job, "findings": findings}],
        "loot": [],
        "session_findings": [],
        "ai_runs": [],
        "chains": [],
    }


def render_pdf(job, findings, overrides=None):
    return to_pdf_bytes(_build_job_report(job, findings), overrides)


def to_pdf_bytes(report, overrides=None):
    """Render a standalone ui-v4 engagement report to PDF via weasyprint."""
    import shutil
    import subprocess
    import tempfile
    weasy = shutil.which("weasyprint")
    if not weasy:
        raise RuntimeError("PDF export requires weasyprint on PATH")
    
    # Use the exact same self-contained HTML generator
    html_text = to_html(report, overrides, static=True)
    
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / "r.html"
        pp = Path(td) / "r.pdf"
        hp.write_text(html_text, encoding="utf-8")
        subprocess.run([weasy, str(hp), str(pp)], check=True, capture_output=True)
        return pp.read_bytes()


def attach_chains(store):
    """Collect pivot chains. Returns [] on any failure."""
    try:
        from whaxon.core import pivot as _pivot
        conn = store._conn()
        try:
            edges = _pivot.list_edges(conn)
        finally:
            try: conn.close()
            except Exception: pass
        sessions = sorted({e["child"]["id"] for e in edges
                           if e["child"]["kind"] == "session"
                           and e["relation"] == "from_exploit"})
        chains = []
        for sid in sessions:
            try:
                conn = store._conn()
                try:
                    chain = _pivot.chain_for_session(conn, sid)
                finally:
                    try: conn.close()
                    except Exception: pass
                for root in chain.get("root_exploits", []):
                    chains.append({
                        "root": root["parent"],
                        "descendants": chain.get("descendants", []),
                    })
            except Exception:
                pass
        return chains
    except Exception:
        return []


def _technical_band(f: dict) -> str:
    """Map a finding to a remediation urgency band.

    Uses CVSS + EPSS + KEV when available (from the severity resolver).
    Falls back to adapter-assigned severity when no CVSS is on record.
    Deterministic. No LLM.
    """
    if f.get("kev"):
        return "immediate"
    epss = f.get("epss")
    cvss = f.get("cvss")
    if epss is not None and epss > 0.2:
        return "immediate"
    if cvss is not None and cvss >= 9.0:
        return "immediate"
    if epss is not None and epss > 0.05:
        return "short-term"
    if cvss is not None and cvss >= 7.0:
        return "short-term"
    if cvss is not None and cvss >= 4.0:
        return "medium-term"
    sev = (f.get("severity") or "").lower()
    if sev in ("critical", "high"):
        return "immediate"
    if sev == "medium":
        return "short-term"
    if sev == "low":
        return "medium-term"
    return "backlog"


_BI_TO_BAND = {
    "critical": "immediate",
    "high": "short-term",
    "medium": "medium-term",
    "low": "backlog",
}


def _priority_band(f: dict) -> str:
    """Technical band, shifted up (never down) by business impact."""
    tech = _technical_band(f)
    bi = (f.get("business_impact") or "").lower()
    bi_band = _BI_TO_BAND.get(bi)
    if bi_band is None:
        return tech
    ti = _BAND_ORDER.index(tech)
    bi_i = _BAND_ORDER.index(bi_band)
    return _BAND_ORDER[min(ti, bi_i)]


_BAND_LABELS = {
    "immediate": "Immediate",
    "short-term": "Short-term",
    "medium-term": "Medium-term",
    "backlog": "Backlog",
}

_BAND_ORDER = ["immediate", "short-term", "medium-term", "backlog"]


def _md_remediation_roadmap(md: list, report: dict) -> None:
    """Render a prioritized remediation roadmap grouped by urgency."""
    unique = report.get("unique_findings") or []
    if not unique:
        return

    bands: dict = {b: [] for b in _BAND_ORDER}
    for f in unique:
        band = _priority_band(f)
        bands[band].append(f)

    md.append("## Remediation Roadmap\n")
    md.append(
        "Findings grouped by urgency. Immediate items have a known-exploited "
        "CVE, high EPSS, or CVSS 9.0+. Backlog items are informational. "
        "Each item is shown once; counts indicate how many jobs produced it.\n"
    )

    for band in _BAND_ORDER:
        items = bands[band]
        if not items:
            continue
        md.append("### " + _BAND_LABELS[band] + " (" + str(len(items)) + ")\n")
        for f in items:
            raw = (f.get("raw_line") or "").strip().replace(chr(10), " ")[:160]
            proof = f.get("proof") or ""
            count = f.get("count", 1)
            cve = f.get("cve")
            cvss = f.get("cvss")
            epss = f.get("epss")
            tags = []
            if cve:
                tags.append(cve)
            if cvss is not None:
                tags.append("CVSS " + str(cvss))
            if epss is not None:
                tags.append("EPSS " + str(round(epss, 3)))
            if f.get("kev"):
                tags.append("KEV")
            tag_str = (" _(" + ", ".join(tags) + ")_") if tags else ""
            count_str = (" (x" + str(count) + ")") if count > 1 else ""
            md.append("- " + raw + count_str + tag_str)
            if proof:
                md.append("")
                md.append("  **Verified. Reproduce with:**")
                md.append("  ```bash")
                md.append("  " + proof)
                md.append("  ```")
        md.append("")

    # Choke points: findings that recur across jobs and are high or critical
    choke = [f for f in unique
             if f.get("count", 1) > 1
             and (f.get("severity") or "").lower() in ("critical", "high")]
    if choke:
        md.append("### Choke points\n")
        md.append(
            "Findings that recur across multiple jobs. One fix removes them "
            "everywhere they appear.\n"
        )
        for f in choke[:10]:
            raw = (f.get("raw_line") or "").strip().replace(chr(10), " ")[:140]
            md.append("- " + raw + " (x" + str(f.get("count", 1)) + ")")
        md.append("")


def _md_findings_appendix(md, report, all_findings=False):
    unique = report.get("unique_findings") or []
    if not unique:
        return
    detail_sevs = list(_SEV_ORDER) if all_findings else ["critical", "high"]
    md.append("## Appendix: Technical Findings\n")
    for sev in detail_sevs:
        bucket = [f for f in unique if (f.get("severity") or "").lower() == sev]
        if not bucket:
            continue
        md.append("### " + sev.capitalize() + " (" + str(len(bucket)) + ")\n")
        for f in bucket:
            raw = _truncate_preserving_urls((f.get("raw_line") or "").strip().replace(chr(10), " "), 200)
            count = f.get("count", 1)
            jobs_seen = len(f.get("job_ids") or [])
            suffix = ""
            if count > 1:
                suffix = "  _(seen " + str(count) + " times across " + str(jobs_seen) + " jobs)_"
            _label = sev
            _bi = f.get("business_impact")
            if _bi:
                _label = sev + " / Business: " + str(_bi)
            md.append("- **[" + _label + "]** " + raw + suffix)
            _vstat = f.get("verification_status") or "candidate"
            _vby = f.get("verified_by") or "engine"
            _vreason = f.get("verification_reason") or ""
            _vline = "  _Verification: " + _vstat + " by " + _vby
            if _vreason:
                _vline += " \u2014 " + _vreason
            _vline += "_"
            md.append(_vline)
            if f.get("proof"):
                md.append("")
                md.append("  **Proof of Exploit:**")
                md.append("  ```bash")
                md.append("  " + f["proof"])
                md.append("  ```")
        md.append("")


def _md_job_history_appendix(md, report):
    md.append("## Appendix: Job History\n")
    md.append("| Job | Tool | Target | Status | Exit |")
    md.append("|-----|------|--------|--------|------|")
    for entry in report["jobs"]:
        j = entry["job"]
        md.append("| `" + j["id"] + "` | " + j.get("tool", "") + " | " + j.get("target", "") + " | " + j.get("status", "") + " | " + str(j.get("exit_code", "")) + " |")
    md.append("")
