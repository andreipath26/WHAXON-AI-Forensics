# Findings

All live findings were confirmed twice: once with the study's Python client
(`scripts/dvwa_client.py`, persistent session) and once with an unrelated `curl` process with no
cookie jar (`scripts/verify_findings.py`). Raw bodies are in `evidence/live/` and
`evidence/verification/`; each is hashed in `evidence/manifest.json`.

**Target:** `https://pentest-ground.com:4280/` — DVWA (PHP 8.5.12 behind nginx/1.31.8 + Apache
2.4.69), database **not initialised**.
**Assessment window:** 2026-10-25T11:39Z–12:31Z.

---

## Vulnerability findings

### F1 — Unauthenticated local file inclusion / arbitrary file read — **CONFIRMED**
- **Endpoint:** `GET /vulnerabilities/fi/?page=/etc/passwd`
- **Evidence:** full `/etc/passwd` returned to a client with no session; 18 account lines, incl.
  `root:x:0:0` and `www-data:x:33:33`. Traversal form `../../../../etc/hostname` also works.
- **Control:** `?page=include.php` returns the module's own intended file, so the endpoint is
  functioning and the positive is not a generic error page.
- **CWE-22 / CWE-98.** CVSS v3.1 assessment: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N → **7.5 High**.
- **Interpretation:** read-only disclosure of any file readable by `www-data`. That includes
  `/var/www/html/config/config.inc.php`, which the application itself advertises as holding database
  credentials. **That file was deliberately not read** (scope §4).

### F2 — Unauthenticated reflected XSS — **CONFIRMED**
- **Endpoint:** `GET /vulnerabilities/xss_r/?name=<svg/onload=...>` (and `<script>`, `<img onerror>`)
- **Evidence:** the payload appears verbatim inside `<pre>Hello PAYLOAD</pre>`; no HTML encoding.
- **Control:** an inert marker is reflected verbatim, and a non-reflecting page does not contain the
  payload — so the finding is reflection *in an executable context*, not merely echo.
- **CWE-79.** AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N → **6.1 Medium**.
- **Limitation:** no browser was available, so script execution was established by HTML context
  analysis, not by DOM execution.

### F3 — Unauthenticated OS command injection — **CONFIRMED**
- **Endpoint:** `POST /vulnerabilities/exec/` with `ip=127.0.0.1;id&Submit=Submit`
- **Evidence:** `uid=33(www-data) gid=33(www-data) groups=33(www-data)`.
- **Control:** `ip=127.0.0.1` produced four ICMP replies and no `uid`, proving the module ran and the
  injection added a command rather than the page merely differing.
- **CWE-78.** AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H → **9.8 Critical** (read-only commands used;
  the underlying capability is arbitrary command execution as `www-data`).
- **Note:** the request method matters — the earlier GET probe produced no output and was correctly
  *not* treated as evidence of absence.

### F4 — Unauthenticated `phpinfo()` disclosure — **CONFIRMED**
- **Endpoint:** `GET /phpinfo.php`, 87,787 bytes to an anonymous client.
- **Discloses:** PHP 8.5.12, `DOCUMENT_ROOT`, loaded extensions, `display_errors=On`,
  `allow_url_include=On`, `allow_url_fopen=On`, full `php.ini` path, server environment.
- **Control:** `/about.php` (static) contains no phpinfo markers.
- **CWE-200 / CWE-16.** AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N → **5.3 Medium**.
- **Why it matters here:** `display_errors=On` is the direct cause of F7 below, and
  `allow_url_include=On` widens F1 from file read to potential remote inclusion.

### F5 — Destructive database setup reachable unauthenticated — **CONFIRMED (presence only)**
- **Endpoint:** `GET /setup.php` renders "Create / Reset Database" to an anonymous client, and
  discloses the DB host (`db`), DB name (`dvwa`), DB user (`dvwa`, password masked) and the config
  path `/var/www/html/config/config.inc.php`.
- **Not exercised:** the reset was **not** submitted. The effect is therefore unproven by design;
  only the exposure is claimed. Any visitor could wipe the schema for every concurrent user.
- **CWE-306 / CWE-284.** Presence-only assessment; no CVSS asserted for the unproven effect.
- **Interpretation:** this is the single most damaging deployment issue found, and it is the one
  finding whose *impact* this study deliberately leaves untested.

### F6 — Session cookie lacks `Secure`, `HttpOnly`, `SameSite` — **CONFIRMED**
- **Evidence:** `Set-Cookie: PHPSESSID=<value>; expires=...; Max-Age=86400; path=/` — no
  `HttpOnly`, no `Secure`, no `SameSite`. Cookie value never stored.
- **CWE-1004 / CWE-614.** AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N → **4.8 Medium** (mitigated in
  practice because the site is HTTPS-only on :4280).
- **Interaction:** absent `HttpOnly` turns F2 from defacement into session theft.

### F7 — Error-based information disclosure — **CONFIRMED**
- **Endpoint:** `GET /vulnerabilities/sqli/?id=1`
- **Evidence:** `Fatal error: Uncaught mysqli_sql_exception: Table 'dvwa.users' doesn't exist in
  /var/www/html/vulnerabilities/sqli/source/low.php:11` plus a full stack trace naming
  `index.php(34)`, `low.php(11)`, and the partially-elided query text.
- **CWE-209.** AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N → **5.3 Medium**.
- **Interpretation:** absolute paths + schema + framework internals, unauthenticated. Also the
  evidence that H6 (uninitialised database) is true.

### F8 — Version and topology disclosure — **CONFIRMED**
- `Server: nginx/1.31.8`, `X-Powered-By: PHP/8.5.12` on every response; a 403 page leaks
  `Apache/2.4.69 (Debian) Server at pentest-ground.com Port 80`, revealing the proxy chain
  (nginx → Apache → PHP-FPM) and an internal listener.
- Missing on all responses checked: `Strict-Transport-Security`, `Content-Security-Policy`,
  `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`.
- **CWE-200 / CWE-693.** Informational-to-low.

## Observations about the application's authentication model

DVWA normally gates its modules behind `login.php`. On this deployment the modules execute for
anonymous clients, and every response footer reports `Username: Unknown`. The cause cannot be
determined from outside: it may be a modified `dvwaPageStartup()` guard, a PHP configuration where
the session bootstrap fails open, or a reverse-proxy rewrite. It is recorded as an observation with
its evidence, not as a diagnosis.

**Interaction with the tooling under study:** WHAXON's adapters would classify
`vulnerabilities/fi/`, `xss_r/`, `exec/` as `found_path` entries with status 200 — i.e. the same
`low`-severity bucket as `favicon.ico` — because path-discovery adapters have no concept of "this
path executed attacker input". The highest-impact findings on this target are invisible to the
adapter layer that produced the repository's own proof artefact.

## Findings about WHAXON (the instrument)

| ID | Claim | Status | Evidence |
| --- | --- | --- | --- |
| I1 | ffuf adapter invents `status: 200` for output that carries no status | confirmed | `evidence/adapters/fidelity.json` |
| I2 | The shipped DVWA proof artefact contains 9/12 cross-tool status contradictions; dedupe keeps the first tool's data | confirmed | same, `merged_unique_finding_sources` |
| I3 | Replay verification emits `verified` for a non-vulnerable page (marker and timing decoys) | confirmed | `evidence/benchmark/confusion.json` |
| I4 | Replay verification emits `refuted` for a genuinely exploitable UNION injection | confirmed | `evidence/benchmark/results.json` |
| I5 | First vendored payload per kind is documentation junk for 4 of 6 kinds tested | confirmed | `docs/research-hypotheses.md` H3.4 |
| I6 | LFI and POST-only vulnerabilities can never be verified | confirmed (code + benchmark) | `core/validator.py` `REPLAYABLE`, method allowlist |
| I7 | Scope authorises a name without binding its address; redirects move tool traffic off-scope | confirmed | `evidence/scope/*` |

## What was *not* found

- No SQL injection could be demonstrated: the `sqli` module aborts before query construction
  because the schema is absent. Absence of demonstration is not evidence of safety — the code path
  is the stock DVWA concatenation, visible in the stack trace.
- No evidence of other tenants' data or of any credential. Nothing sensitive was extracted.
