"""E9 — do WHAXON's adapters record what the tool actually observed?

Three independent comparisons:

1. Synthetic fidelity. Feed the ffuf adapter three shapes of real ffuf output —
   silent mode (no status), default mode (status present), and a 404 line — and
   check which fields survive.

2. Internal contradiction. Parse the engagement artefact shipped in this
   repository (`data/proof-dvwa/engagement.json`), which contains findings from
   ffuf and gobuster against the same DVWA container, and compare the status
   each adapter recorded for the same path.

3. Live cross-check. Re-request those paths on the authorised target with a
   plain HTTP client and record the truth. This is the strongest of the three
   because it does not depend on any scanner.

Output: evidence/adapters/fidelity.json plus raw live bodies for the checked paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from whaxon.adapters.ffuf import FfufAdapter            # noqa: E402
from whaxon.adapters.gobuster import GobusterAdapter   # noqa: E402

OUT = ROOT / "evidence" / "adapters"
PATHS = ["/.htaccess", "/.htpasswd", "/.hta", "/php.ini", "/robots.txt",
         "/server-status", "/config", "/docs", "/external", "/favicon.ico",
         "/index.php", "/phpinfo.php", "/.gitignore", "/.git/HEAD"]


def dump(f) -> dict:
    return {"kind": f.kind, "severity": f.severity, "source": f.source,
            "data": f.data, "raw_line": f.raw_line}


def synthetic() -> dict:
    silent = [("stdout", p + "\n") for p in ["admin", "config", "docs"]]
    default = [("stdout", "admin  [Status: 200, Size: 1234]\n"),
               ("stdout", "secret [Status: 403, Size: 289]\n"),
               ("stdout", "missing [Status: 404, Size: 12]\n")]
    a1 = FfufAdapter().parse(silent)
    a2 = FfufAdapter().parse(default)
    return {
        "silent_mode_input": [t for _s, t in silent],
        "silent_mode_findings": [dump(f) for f in a1],
        "silent_mode_observation": (
            "input lines carry no HTTP status; the adapter still writes "
            f"status={a1[0].data['status']!r} and size={a1[0].data['size']!r}"
            if a1 else "no findings produced"),
        "default_mode_input": [t for _s, t in default],
        "default_mode_findings": [dump(f) for f in a2],
        "default_mode_observation": "status and size preserved when present; 404 dropped",
    }


def internal_contradiction() -> dict:
    path = ROOT / "data" / "proof-dvwa" / "engagement.json"
    data = json.loads(path.read_text())
    # Per-job findings preserve which tool measured what. `unique_findings`
    # merges by kind+path and keeps the first source, which is itself part of
    # the finding below.
    ffuf: dict = {}
    gob: dict = {}
    for job in data.get("jobs", []):
        tool = job.get("job", {}).get("tool")
        for f in job.get("findings", []):
            if f.get("kind") != "found_path":
                continue
            bucket = ffuf if tool == "ffuf" else gob if tool == "gobuster" else None
            if bucket is not None:
                bucket[f["data"]["path"]] = f
    merged = {f["data"]["path"]: f for f in data["unique_findings"]
              if f.get("kind") == "found_path" and "data" in f}
    merged_source = {p: f.get("source") for p, f in merged.items()}
    rows = []
    for p in sorted(set(ffuf) & set(gob)):
        rows.append({
            "path": p,
            "ffuf_status": ffuf[p]["data"].get("status"),
            "ffuf_size": ffuf[p]["data"].get("size"),
            "ffuf_severity": ffuf[p]["severity"],
            "gobuster_status": gob[p]["data"].get("status"),
            "gobuster_size": gob[p]["data"].get("size"),
            "gobuster_severity": gob[p]["severity"],
            "status_agrees": ffuf[p]["data"].get("status") == gob[p]["data"].get("status"),
        })
    return {
        "source_file": str(path.relative_to(ROOT)),
        "note": "both jobs ran against 172.17.0.3 in the same engagement",
        "rows": rows,
        "disagreements": sum(1 for r in rows if not r["status_agrees"]),
        "both_paths_found": len(rows),
        "ffuf_findings_with_null_size": sum(
            1 for f in ffuf.values() if f["data"].get("size") is None),
        "merged_unique_finding_sources": merged_source,
        "dedupe_note": (
            "unique_findings contains one record per path even where two tools "
            "disagree; the retained data is the first-ingested tool's, so the "
            "contradicting measurement is dropped from the canonical view"),
    }


def live_crosscheck() -> dict:
    from scripts.dvwa_client import DvwaClient
    c = DvwaClient()
    rows = []
    for p in PATHS:
        try:
            r = c.get(p, experiment="E9-adapter-fidelity",
                      note=f"live status cross-check for {p}")
            rows.append({"path": p, "status": r.status_code, "bytes": len(r.text),
                         "server": r.headers.get("Server", ""),
                         "excerpt": r.text[:200].replace("\n", " ")})
        except Exception as exc:
            rows.append({"path": p, "error": f"{type(exc).__name__}: {exc}"})
    c.close()
    return {"target": c.base, "rows": rows}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    live = live_crosscheck()
    live_status = {r["path"]: r.get("status") for r in live["rows"]}

    synth = synthetic()
    contra = internal_contradiction()

    # Adapter output vs truth, for the paths where the shipped artefact has both.
    adjudication = []
    for row in contra["rows"]:
        truth = live_status.get("/" + row["path"].lstrip("/"))
        row_truth = truth if truth is not None else "not measured"
        adjudication.append({
            **row,
            "live_status_this_engagement": row_truth,
            "ffuf_matches_truth": row["ffuf_status"] == row_truth,
            "gobuster_matches_truth": row["gobuster_status"] == row_truth,
        })

    gob_adapter = GobusterAdapter().parse(
        [("stdout", "config               (Status: 301) [Size: 309] [--> http://x/config/]\n"),
         ("stdout", "php.ini              (Status: 200) [Size: 148]\n")])

    out = {
        "experiment": "E9-adapter-fidelity",
        "synthetic": synth,
        "shipped_artefact_contradiction": contra,
        "shipped_artefact_adjudicated_against_live_target": adjudication,
        "gobuster_adapter_sanity": [dump(f) for f in gob_adapter],
        "live_status_measurement": live,
    }
    (OUT / "fidelity.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("== synthetic ==")
    print(" ", synth["silent_mode_observation"])
    for f in synth["silent_mode_findings"]:
        print("   silent:", f["data"], "severity", f["severity"])
    print("\n== shipped artefact (data/proof-dvwa/engagement.json) ==")
    print(f"  {contra['both_paths_found']} paths found by both tools, "
          f"{contra['disagreements']} status disagreements")
    for r in contra["rows"]:
        print(f"   {r['path']:14s} ffuf={r['ffuf_status']} gobuster={r['gobuster_status']} "
              f"sev(ffuf/gob)={r['ffuf_severity']}/{r['gobuster_severity']}")
    print("\n== live truth on the authorised target ==")
    for r in live["rows"]:
        print(f"   {r['path']:14s} {r.get('status')} {r.get('bytes')}B")
    print("\n== adjudication ==")
    for r in adjudication:
        print(f"   {r['path']:14s} ffuf={r['ffuf_status']} gob={r['gobuster_status']} "
              f"live={r['live_status_this_engagement']} "
              f"(ffuf_ok={r['ffuf_matches_truth']}, gob_ok={r['gobuster_matches_truth']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
