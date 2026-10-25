"""E4 — unauthrated attack-surface probe of the authorised target.

Research question
-----------------
Which routes of the deployed DVWA instance respond to an *unauthenticated*
client, and what do they disclose? The instance's database is absent (login
redirects to setup.php), so this probe deliberately uses only benign markers
and one non-destructive command payload.

Safety
------
* No database reset, no upload, no brute force, no destructive command.
* Every request is a GET with a fixed, short parameter value or a benign marker.
* Total budget <= 20 requests, sequential, 0.5 s apart.
* The command-injection payload is `;id` — read-only, single shell builtin call.

Output
------
evidence/live/routes.json      one record per route: status, length, sha256,
                               classification, and a bounded excerpt
evidence/live/<route>.html     raw bodies for the routes that matter
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.dvwa_client import DvwaClient, utc_now  # noqa: E402

MARKER = "whaxon_probe_7f3a9c"

ROUTES = [
    # (label, path, params, experiment, intent)
    ("home", "/index.php", None, "E4-surface", "is the app reachable at all"),
    ("login", "/login.php", None, "E4-surface", "login form + CSRF token presence"),
    ("setup", "/setup.php", None, "E4-surface", "database setup page exposure"),
    ("phpinfo", "/phpinfo.php", None, "E4-surface", "PHP configuration exposure"),
    ("instructions", "/instructions.php", None, "E4-surface", "static help page"),
    ("about", "/about.php", None, "E4-surface", "static about page"),
    ("sqli", "/vulnerabilities/sqli/", {"id": "1", "Submit": "Submit"},
     "E4-surface", "SQL module without a database"),
    ("sqli_blind", "/vulnerabilities/sqli_blind/", {"id": "1", "Submit": "Submit"},
     "E4-surface", "blind SQL module without a database"),
    ("xss_r_marker", "/vulnerabilities/xss_r/", {"name": MARKER},
     "E4-surface", "reflected-XSS module, benign marker (negative control)"),
    ("xss_r_payload", "/vulnerabilities/xss_r/", {"name": f"<script>{MARKER}</script>"},
     "E5-xss", "reflected-XSS module, script payload"),
    ("exec_benign", "/vulnerabilities/exec/", {"ip": "127.0.0.1", "Submit": "Submit"},
     "E4-surface", "command module with a benign, well-formed IP"),
    ("exec_inject", "/vulnerabilities/exec/", {"ip": "127.0.0.1;id", "Submit": "Submit"},
     "E6-command-injection", "command-separator payload executing read-only `id`"),
    ("fi_lfi", "/vulnerabilities/fi/", {"page": "/etc/passwd"},
     "E4-surface", "file-inclusion probe for a world-readable OS file"),
    ("upload", "/vulnerabilities/upload/", None, "E4-surface", "upload form exposure"),
    ("weak_id", "/vulnerabilities/weak_id/", None, "E4-surface", "weak session id module"),
    ("xss_s", "/vulnerabilities/xss_s/", None, "E4-surface", "stored XSS module (needs DB)"),
    ("csrf", "/vulnerabilities/csrf/", None, "E4-surface", "CSRF module"),
    ("security", "/security.php", None, "E4-surface", "security-level selector"),
]

CLASSIFIERS = [
    ("fatal_error", re.compile(r"Fatal error|Uncaught \w+_exception|Warning: |Notice: ", re.I)),
    ("login_required", re.compile(r"login\.php|You have not logged in|not logged in", re.I)),
    ("phpinfo", re.compile(r"phpinfo\(\)|PHP Version|Configuration File \(php\.ini\)", re.I)),
    ("setup_page", re.compile(r"Create / Reset Database|Database Setup", re.I)),
    ("upstream_error", re.compile(r"not found|doesn't exist", re.I)),
]


def classify(body: str, status: int) -> list[str]:
    tags = []
    for name, rx in CLASSIFIERS:
        if rx.search(body or ""):
            tags.append(name)
    if status >= 500:
        tags.append("http_5xx")
    return tags


def excerpt(body: str, limit: int = 600) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", body or "", flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def main() -> int:
    client = DvwaClient()
    results = []
    for label, path, params, experiment, intent in ROUTES:
        try:
            resp = client.get(path, params=params, experiment=experiment,
                              note=f"{label}: {intent}")
            body = resp.text or ""
            tags = classify(body, resp.status_code)
            rec = {
                "label": label, "path": path, "params": params, "experiment": experiment,
                "intent": intent, "status": resp.status_code, "bytes": len(body),
                "content_type": resp.headers.get("Content-Type", ""),
                "location": resp.headers.get("Location", ""),
                "classifications": tags,
                "marker_reflected": MARKER in body,
                "contains_id_output": bool(re.search(r"uid=\d+\([^)]+\)", body)),
                "excerpt": excerpt(body),
                "sha256_body": __import__("hashlib").sha256(body.encode()).hexdigest(),
                "timestamp_utc": utc_now(),
            }
            if any(t in tags for t in ("fatal_error", "phpinfo", "setup_page")) or "xss" in label \
               or "exec" in label:
                client.save_html(f"{label}.html", body)
        except Exception as exc:                              # recorded, not swallowed
            rec = {"label": label, "path": path, "params": params, "experiment": experiment,
                   "status": None, "error": f"{type(exc).__name__}: {exc}",
                   "timestamp_utc": utc_now()}
        results.append(rec)
        print(f"{label:16s} {str(rec.get('status')):>4s} "
              f"{str(rec.get('bytes', '-')):>7s} {','.join(rec.get('classifications', [])) or '-'}"
              f"{' REFLECTED' if rec.get('marker_reflected') else ''}"
              f"{' ID_OUTPUT' if rec.get('contains_id_output') else ''}")

    out = client.evidence_dir / "routes.json"
    out.write_text(json.dumps({
        "experiment": "E4/E5/E6",
        "target": client.base,
        "authenticated": client.authenticated,
        "timestamp_utc": utc_now(),
        "marker": MARKER,
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")
    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
