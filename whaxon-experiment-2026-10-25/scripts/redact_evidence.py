"""Redact session identifiers from captured evidence, with a before/after audit trail.

Why: several artefacts (phpinfo output, response headers, verification JSON) quote a `Set-Cookie`
line containing this study's throwaway `PHPSESSID`. Publishing a session identifier is poor
practice even when the session is disposable, and the mission forbids unnecessary collection of
session tokens.

What it does: replaces the *value* with a fixed placeholder, records the file's SHA-256 before and
after, and writes `evidence/redactions.json`. It never touches request/response semantics, status
codes, timings or body content other than the identifier.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
PLACEHOLDER = "PHPSESSID=<REDACTED-SESSION-ID>"
PATTERNS = [
    (re.compile(r"PHPSESSID=[0-9a-zA-Z]{16,64}"), PLACEHOLDER),
    (re.compile(r"dvwaSession=[0-9]+"), "dvwaSession=<REDACTED>"),
]


def sha256_text(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    records = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name in {"manifest.json", "redactions.json"}:
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="surrogateescape")
        new = text
        hits: list[dict] = []
        for pattern, replacement in PATTERNS:
            new, count = pattern.subn(replacement, new)
            if count:
                hits.append({"pattern": pattern.pattern, "replacements": count})
        if not hits:
            continue
        path.write_text(new, encoding="utf-8", errors="surrogateescape")
        records.append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256_before": sha256_text(raw),
            "sha256_after": sha256_text(path.read_bytes()),
            "redactions": hits,
            "transformation": "value replaced with placeholder; no other content altered",
            "performed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    (EVIDENCE / "redactions.json").write_text(json.dumps({
        "policy": "session identifiers are redacted before publication; values are never stored",
        "placeholder": PLACEHOLDER,
        "files": records,
        "total_files": len(records),
    }, indent=2), encoding="utf-8")
    print(f"redacted {len(records)} files")
    for r in records:
        print("  ", r["path"], r["redactions"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
