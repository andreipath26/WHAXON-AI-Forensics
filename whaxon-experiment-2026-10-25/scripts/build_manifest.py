"""Build evidence/manifest.json — identifier, description, timestamp, SHA-256, class, experiment.

Re-run after any change to evidence. The manifest is derived data: it never modifies the artefacts
it describes.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"

DESCRIPTIONS = {
    "env/environment.json": ("Phase A runner environment, network reachability and git/GitHub auth state", "public-safe", "E0"),
    "env/probe.log": ("Environment probe log with hashes", "public-safe", "E0"),
    "env/target_root.headers": ("First-contact response headers from the assessment target", "public-safe", "E0"),
    "env/target_root.html": ("First-contact body from the assessment target (DVWA home)", "public-safe", "E0"),
    "scope/decision-matrix.json": ("14 target forms evaluated through ScopeManager, plus DNS binding probe", "public-safe", "E1"),
    "scope/redirect-escape.json": ("Two-address experiment: permitted host redirects to a denied host", "public-safe", "E7"),
    "adapters/fidelity.json": ("Adapter fidelity: synthetic ffuf shapes, shipped-artefact contradiction, live adjudication", "public-safe", "E2/E6"),
    "benchmark/results.json": ("Per-case validator verdicts and reasons on the labelled benchmark", "public-safe", "E3"),
    "benchmark/confusion.json": ("Confusion matrices, TPR/FPR/precision/Youden J for both replay paths", "public-safe", "E3"),
    "benchmark/access-log.jsonl": ("Requests the validator actually made to each benchmark case", "public-safe", "E3"),
    "live/routes.json": ("Unauthenticated route matrix with classifications and excerpts", "public-safe", "E4"),
    "live/request-log.jsonl": ("All live requests: method, path, status, timing, redacted cookie attribute names", "public-safe", "E4"),
    "live/confirm.json": ("Confirmed LFI / XSS / command-injection probes with matched negative controls", "public-safe", "E5"),
    "verification/verification.json": ("Independent curl re-test of F1-F6 with controls", "public-safe", "V1"),
}

PREFIX_CLASS = {
    "live/": "public-safe",
    "verification/": "public-safe",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    entries = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        rel = path.relative_to(EVIDENCE).as_posix()
        desc, cls, exp = DESCRIPTIONS.get(rel, ("raw observation captured by the study", "public-safe", "n/a"))
        entries.append({
            "id": rel.replace("/", "-").replace(".", "-"),
            "path": f"evidence/{rel}",
            "description": desc,
            "classification": cls,
            "experiment": exp,
            "bytes": path.stat().st_size,
            "captured_at_utc": datetime.fromtimestamp(
                path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sha256": sha256(path),
        })

    # Sanitisation assertions: no *values* that look like session ids or credentials.
    # Patterns are deliberately value-shaped so that the placeholder text produced by
    # scripts/redact_evidence.py and this script's own pattern list do not self-flag.
    import re as _re
    SECRET_PATTERNS = [
        ("session-id-value", _re.compile(r"PHPSESSID=[0-9a-zA-Z]{16,}")),
        ("github-token", _re.compile(r"ghp_[A-Za-z0-9]{20,}")),
        ("github-fine-grained-token", _re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
        ("private-key-block", _re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ]
    offenders = []
    for path in EVIDENCE.rglob("*"):
        if not path.is_file() or path.suffix in {".png", ".jpg"} or path.name == "manifest.json":
            continue
        text = path.read_text(errors="ignore")
        for name, rx in SECRET_PATTERNS:
            if rx.search(text):
                offenders.append({"path": str(path.relative_to(ROOT)), "pattern": name})

    manifest = {
        "engagement": "WHAXON AI Forensics — autonomous research, security testing, decision trace",
        "target": "https://pentest-ground.com:4280/",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hash_algorithm": "sha256",
        "classification_legend": {
            "public-safe": "publishable: no credentials, no session values, no personal data",
            "restricted": "kept local / access-controlled (none present in this study)",
            "secret": "never written to disk (none present)",
        },
        "sanitisation_check": {"patterns_checked": ["PHPSESSID=", "ghp_", "github_pat_",
                                                    "BEGIN RSA PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY"],
                               "offenders": offenders},
        "artefact_count": len(entries),
        "artefacts": entries,
    }
    out = EVIDENCE / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} with {len(entries)} artefacts")
    if offenders:
        print(f"WARNING: {len(offenders)} sanitisation hits — review before publication:")
        for o in offenders:
            print("  ", o)
        return 1
    print("sanitisation check: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
