"""Audited HTTP client for the authorised DVWA assessment target.

Design goals
------------
* Every request is logged before the response is interpreted (JSONL), so the
  evidence file is a contemporaneous record rather than a summary.
* Session cookies are never written to disk. Only the fact that a session
  existed is recorded.
* Requests are strictly sequential with a small delay, deliberately bounding
  load on a shared target (see docs/scope-and-rules.md, request budget).
* TLS verification is disabled ONLY because the target presents a Let's
  Encrypt certificate that validates normally; verification is kept ON in
  fact (`verify=True`). If it ever fails, the client records the failure
  instead of silently downgrading.

Public evidence safety: target responses are stored because the target is a
published deliberately-vulnerable training application and its content is
generic DVWA data. No real user data is involved.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_BASE = os.environ.get("WHAXON_TARGET", "https://pentest-ground.com:4280").rstrip("/")
USER_AGENT = "whaxon-research/1.0 (authorised DVWA assessment; +research-trace)"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


@dataclass
class HttpRecord:
    seq: int
    ts: str
    experiment: str
    method: str
    path: str
    status: int | None
    content_type: str
    bytes: int | None
    duration_ms: float
    params: dict[str, str] = field(default_factory=dict)
    note: str = ""
    error: str = ""
    body_sha256: str = ""
    body_excerpt: str = ""
    redirect_to: str = ""
    set_cookie_flags: str = ""

    def to_public(self) -> dict[str, Any]:
        d = dict(self.__dict__)
        return d


class DvwaClient:
    """Minimal, logging DVWA client."""

    def __init__(self, base_url: str = DEFAULT_BASE, evidence_dir: Path | str = "evidence/live",
                 delay_s: float = 0.4) -> None:
        self.base = base_url.rstrip("/")
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.evidence_dir / "request-log.jsonl"
        self.delay_s = delay_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
        self.seq = 0
        self.authenticated = False
        self.security_level = "unknown"
        self.logfile = open(self.log_path, "a", encoding="utf-8")

    # -- internals ---------------------------------------------------------
    def _log(self, rec: HttpRecord) -> None:
        self.logfile.write(json.dumps(rec.to_public(), sort_keys=True) + "\n")
        self.logfile.flush()

    def _cookie_flags(self, resp: requests.Response) -> str:
        """Record Set-Cookie attribute names only — never the value."""
        flags: list[str] = []
        for raw in resp.raw.headers.getlist("Set-Cookie") if hasattr(resp.raw, "headers") else []:
            name = raw.split("=", 1)[0].strip()
            attrs = []
            low = raw.lower()
            for flag in ("httponly", "secure", "samesite", "domain", "path", "max-age"):
                if flag in low:
                    attrs.append(flag)
            flags.append(f"{name}[{','.join(attrs)}]")
        return "; ".join(flags)

    def request(self, method: str, path: str, experiment: str = "general",
                params: dict[str, str] | None = None, data: dict[str, str] | None = None,
                note: str = "", allow_redirects: bool = False,
                timeout: float = 25.0) -> requests.Response:
        self.seq += 1
        url = self.base + path
        t0 = time.monotonic()
        status: int | None = None
        body = ""
        ctype = ""
        err = ""
        redirect_to = ""
        flags = ""
        try:
            resp = self.session.request(method, url, params=params, data=data,
                                        timeout=timeout, allow_redirects=allow_redirects,
                                        verify=True)
            status = resp.status_code
            body = resp.text if len(resp.content) < 200_000 else resp.text[:200_000]
            ctype = resp.headers.get("Content-Type", "")
            redirect_to = resp.headers.get("Location", "")
            flags = self._cookie_flags(resp)
        except requests.RequestException as exc:      # recorded, never swallowed silently
            err = f"{type(exc).__name__}: {exc}"
            resp = None
        dur = (time.monotonic() - t0) * 1000.0

        rec = HttpRecord(
            seq=self.seq, ts=utc_now(), experiment=experiment, method=method, path=path,
            status=status, content_type=ctype, bytes=(len(body.encode()) if body else 0),
            duration_ms=round(dur, 1),
            params={k: (v if len(v) < 200 else v[:200] + "…") for k, v in (params or {}).items()},
            note=note, error=err, body_sha256=sha256_text(body) if body else "",
            body_excerpt=body[:1200].replace("\r", ""), redirect_to=redirect_to,
            set_cookie_flags=flags,
        )
        self._log(rec)
        time.sleep(self.delay_s)
        if resp is None:
            raise requests.RequestException(err)
        return resp

    def get(self, path: str, **kw) -> requests.Response:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> requests.Response:
        return self.request("POST", path, **kw)

    # -- DVWA specifics ----------------------------------------------------
    @staticmethod
    def token(html: str) -> str:
        m = re.search(r"name=['\"]user_token['\"]\s+value=['\"]([0-9a-fA-F]+)['\"]", html)
        if m:
            return m.group(1)
        m = re.search(r"user_token['\"]?\s*value=['\"]([0-9a-fA-F]+)['\"]", html)
        return m.group(1) if m else ""

    def login(self, username: str = "admin", password: str = "password") -> bool:
        page = self.get("/login.php", experiment="auth", note="fetch CSRF token")
        tok = self.token(page.text)
        resp = self.post("/login.php", experiment="auth",
                         data={"username": username, "password": password,
                               "Login": "Login", "user_token": tok},
                         note="login with DVWA documented default credentials")
        body = resp.text.lower()
        self.authenticated = ("logout" in body) or ("you have logged in" in body) or (
            "welcome to damn vulnerable" in body and "login.php" not in body)
        return self.authenticated

    def set_security(self, level: str) -> bool:
        assert level in ("low", "medium", "high", "impossible"), level
        page = self.get("/security.php", params={"phpids": "", "csrf": ""},
                        experiment="auth", note=f"fetch token for security={level}")
        tok = self.token(page.text)
        resp = self.post("/security.php", experiment="auth",
                         data={"security": level, "seclev_submit": "Submit", "user_token": tok},
                         note=f"set security level to {level}")
        # DVWA stores the level server-side and mirrors it in a cookie's display text.
        self.security_level = level
        return resp.status_code == 200

    def close(self) -> None:
        self.logfile.close()

    # -- helpers -----------------------------------------------------------
    def save_html(self, name: str, html: str) -> Path:
        p = self.evidence_dir / name
        p.write_text(html, encoding="utf-8")
        return p


def extract_between(html: str, start: str, end: str) -> str:
    i = html.find(start)
    if i < 0:
        return ""
    j = html.find(end, i + len(start))
    return html[i + len(start): j if j >= 0 else len(html)]


if __name__ == "__main__":      # smoke test: login + confirm authenticated identity
    c = DvwaClient()
    ok = c.login()
    print(json.dumps({"login_success": ok,
                      "home_authenticated": "Username: admin" in c.get("/index.php").text},
                     indent=2))
    c.close()
