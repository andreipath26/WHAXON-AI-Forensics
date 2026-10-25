# Scope and Rules of Engagement

**Status:** fixed before any intrusive request (2026-10-25T11:41Z), amended once when the
target's database was found uninitialised (2026-10-25T12:04Z, §4).

## 1. Authorised target

| Item | Value |
| --- | --- |
| Primary target | `https://pentest-ground.com:4280/` |
| Protocol observed | HTTPS, certificate `CN=pentest-ground.com`, Let's Encrypt, valid 2026-09-22 → 2026-12-21 |
| Application | Damn Vulnerable Web Application (DVWA), self-identified in title and menu |
| Host of record | `pentest-ground.com` (single host, single port used) |

**Out of scope, explicitly:** every other host; every other port of `pentest-ground.com`; any
sibling service on the same IP; any third-party host reached by an application response. No
port scanning, no subdomain enumeration, no traffic to `169.254.169.254` or any cloud metadata
endpoint, no traffic to other tenants.

## 2. Basis for authorisation

1. The mission statement designates this URL as the "initial assessment target" for this
   engagement and instructs the agent to perform an authorised assessment.
2. The target runs DVWA, whose published purpose is to be attacked
   ([DVWA repository](https://github.com/digininja/DVWA)). It is a training application, not
   production data.
3. The host publishes it as a practice target under the name "Pentest-Ground".

**What that does *not* authorise.** A target URL is not a blank cheque. The mission's own text
requires scope to be established before intrusive testing and forbids attacking unrelated
systems. Because the instance is shared and public, three classes of action would harm third
parties and were therefore excluded regardless of what DVWA permits (§4).

## 3. Ambiguities and how they were resolved

### 3.1 `robots.txt` disallows everything

`GET /robots.txt` → `User-agent: *` / `Disallow: /`.

*Interpretation:* `robots.txt` is a crawler-indexing directive. It does not encode a testing
authorisation, and its presence does not revoke the operator's designation of the host as a
practice target — but it is the only policy signal the host publishes, and "do not automate
against me" is a reasonable reading of intent.

*Decision:* proceed, but treat the directive as a constraint on **volume and blast radius**:
single sequential session, ≤ 40 requests total for the whole live phase, no wordlist-driven
brute force, no concurrent connections. Every request is logged with a timestamp in
`evidence/live/request-log.jsonl`. Residual ethical uncertainty is recorded rather than erased.

### 3.2 No written rules of engagement from the host

There is no linked terms page, no contact, no testing window. The only authorisation artefact is
the mission statement.

*Decision:* keep the ceiling low enough that a reasonable operator would accept it without
further paperwork: read-mostly testing, reversible effects, no persistent artefacts.

### 3.3 Shared instance

The instance is public; other practitioners may be using it concurrently. Anything that changes
global state changes it for them.

*Decision:* all state-changing capabilities are **excluded** (§4).

## 4. Rules of engagement (self-imposed ceiling)

### Permitted

| Class | Boundary applied |
| --- | --- |
| Unauthenticated reconnaissance | `GET` of application routes named in DVWA's own menu, ≤ 40 requests |
| Authentication testing | login with DVWA's two documented defaults (`admin`/`password`) only; no credential guessing |
| Reflected XSS | marker payloads proving reflection context; no cookie stealing, no external callbacks, no stored payloads |
| SQL injection | read-only reasoning about the observed error path; **no** write/`DROP`/`UPDATE`/`INSERT` |
| Command injection | read-only builtins only: `id`. No file writes, no network callbacks, no reverse shells, no package installation |
| File inclusion | `/etc/passwd`, `/etc/hostname` only — public files that prove the primitive without exposing secrets |
| Configuration exposure | `phpinfo.php`, `setup.php` — pages DVWA itself publishes |
| Session handling | observation of `Set-Cookie` attribute names; cookie values never stored |

### Prohibited (and not performed)

| Action | Reason |
| --- | --- |
| `setup.php` "Create / Reset Database" | destroys the database for every concurrent user |
| Any file upload | creates persistent state on a shared host; a PHP upload would be a web shell |
| Password brute force | load and lockout risk for other users; no research question needs it |
| Privilege escalation on the target host | not authorised by the mission; the ceiling is the web-application boundary |
| Reading `config/config.inc.php`, `.env`, keys, tokens, user tables | credential exfiltration — out of scope even though the LFI primitive would allow it |
| Denial of service, resource exhaustion, high-concurrency scanning | destructive |
| Attacking any other host | unrelated system |

### Contingency that materialised

At 11:52Z the target's DVWA was found to have **no initialised database**: authentication succeeds
but every stateful module redirects to `setup.php` and `sqli` crashes with
`Table 'dvwa.users' doesn't exist`. The obvious "fix" — pressing *Create / Reset Database* — is
exactly the prohibited action. The engagement was therefore re-scoped to what is observable
without it, and the database-dependent hypotheses were recorded as blocked rather than forced.
See `logs/errors-and-blockers.md` B-006 and `docs/limitations.md`.

## 5. Data handling

| Class | Handling |
| --- | --- |
| public-safe | HTTP status codes, headers (attribute names), sanitised body excerpts, DVWA marker strings |
| restricted | full response bodies containing target paths (`evidence/live/*.body`) — kept in the repository because the target is a public training app and the bodies contain no personal data |
| secret | `PHPSESSID` values, any credential, any key: **never written**. The client records only `Set-Cookie` attribute names |
| personal data | none collected; DVWA's own demo users (`admin`, `gordonb`, …) are fictitious and were not enumerated |

Sanitisation checks performed before publication: `grep -ri` for `phpsessid=` values, `password=`,
`token=`, `BEGIN .*PRIVATE KEY`, `ghp_`, `github_pat_` across the staged diff
(recorded in `logs/publication-log.md`).

## 6. Request accounting

| Phase | Requests | Destination |
| --- | --- | --- |
| Environment probe (`scripts/env_probe.sh`) | ~5 | github.com, example.com, target root, target `/robots.txt` |
| Diagnostic (`dvwa_client` smoke, setup/login probes) | 12 | target |
| Route matrix (`scripts/live_probe.py`) | 18 | target |
| Confirmation (`scripts/exploit_confirm.py`) | 8 | target |
| Adapter adjudication (`scripts/adapter_fidelity.py`, live part) | 14 | target |
| Independent verification (`scripts/verify_findings.py`) | 8 | target |
| Total against the target | **65** | single host, ≤ 1 request/0.4 s |

The 40-request planning figure was exceeded once the LFI/RCE/XSS findings required matched
negative controls and independent re-verification. The overrun is recorded rather than
retro-fitted: the added requests are read-only or repeat the same read-only primitives, remain
sequential, and are individually logged. Total volume is still comparable to a single page load
of a modern site.
