# Privilege-Boundary Assessment

**Was privilege escalation authorised?** **No.** The mission designates the target URL as an
assessment target and forbids attacking unrelated systems; it does not authorise host-level
exploitation of a shared, public training host. The ceiling set in `docs/scope-and-rules.md` §4 is
therefore the *web-application boundary*: prove what the application itself grants, and stop.

## 1. Boundaries in play

| Boundary | Description | Authorised here? |
| --- | --- | --- |
| B0 | anonymous visitor → authenticated DVWA user | yes (login with documented defaults only) |
| B1 | authenticated user → application-level privileged function (database setup) | observed, not exercised |
| **B2** | **application code → OS process (web server account)** | **yes — this is the assessed boundary** |
| B3 | `www-data` → root inside the target container | **no** |
| B4 | target container → research runner / other hosts | **no** |
| B5 | research-runner user → root on the runner | **no** (also impossible: `no_new_privileges`, no caps) |

## 2. Initial identity

| Context | Identity | Evidence |
| --- | --- | --- |
| Research runner (attacker host) | `uid=104028665(fb631d3594b40a92b083bca535)`, `CapEff=0`, sudo blocked | `evidence/env/environment.json` |
| Target, before exploitation | anonymous (`Username: Unknown` in the application footer) | `evidence/live/routes.json` |
| Target, application session | none established — login redirects to `setup.php`; no authenticated session was usable | `evidence/live/request-log.jsonl` seq 1–2 |

## 3. Attempted method and observations (B2)

**Method.** `POST /vulnerabilities/exec/` with `ip=127.0.0.1;id&Submit=Submit`. The module
concatenates the value into a shell command (DVWA "low"). The appended command is the read-only
builtin `id`.

**Observation (primary).**

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

**Observation (independent re-test, `curl`, no cookies).** Identical line.
(`evidence/verification/verification.json` F3.)

**Control.** `ip=127.0.0.1` alone → four `64 bytes from 127.0.0.1` ICMP replies, no `uid`. So the
shell ran for both requests and the second appended a command; the difference is the injection, not
page variance.

**Caveat on scope.** Only `id` was executed. No file was written, no reverse connection attempted,
no credential read, no `sudo`, no kernel/container probe. Anything beyond a read-only builtin would
have exceeded the authorised ceiling.

## 4. What this establishes

- The application's own privilege is **`www-data` (uid 33)** inside the target container, with
  access to `/etc/passwd` (F1) and to `/var/www/html`, including
  `config/config.inc.php` — which the application advertises as containing database credentials.
- Effective capability from an anonymous client: **arbitrary command execution as `www-data`**
  (F3), plus arbitrary file read (F1). Confidentiality, integrity and availability of the
  *application* are all within reach; that is the practical maximum of B2.

## 5. What this does **not** establish

**Root on the target was not obtained and was not attempted.** The mission's completion criteria ask
specifically whether root-level access was independently demonstrated in the intended target
environment. Answer: **no**. The strongest confirmed result is command execution as `www-data`.

Reasons this is a boundary and not a result:

1. `www-data` on a standard Debian image holds no elevation primitive by itself.
2. The obvious escalation material — `config.inc.php` (DB credentials) — was deliberately not read,
   by the same rule that forbids credential exfiltration. Reading it would likely yield database
   access as user `dvwa`, i.e. a lateral move to B1-adjacent privilege, not root.
3. Probing for container-escape primitives (cgroups, mounted docker socket, kernel exploits) is
   explicitly outside the authorised scope and could destabilise a shared host.

## 6. Failed and abandoned approaches

| Approach | Outcome | Classification |
| --- | --- | --- |
| Login as `admin`/`password` to reach DB-backed modules | authenticated session never usable; redirected to `setup.php` | target state (no DB) |
| Trigger SQL injection to read the `users` table | module aborts before query construction | target state |
| Use the LFI to read `config.inc.php` | **not attempted** — credential extraction is out of scope | self-imposed rule |
| `setup.php` reset to make modules work | **not attempted** — destructive to a shared host | self-imposed rule |
| Local DVWA container for a ground-truth control | blocked: no Docker daemon | runner environment (B-001b) |

## 7. Strongest confirmed result and remaining boundary

- **Strongest confirmed:** unauthenticated remote command execution as `www-data`, verified twice
  with independent clients and a matched negative control.
- **Remaining boundary:** `www-data` → root (B3), untested by authorisation, and target container →
  runner (B4), untested and out of scope.
- **Next justified experiment** (for an operator holding explicit authorisation for host-level
  testing, on a **non-shared** instance): read `config.inc.php` via F1 to obtain the DB account,
  enumerate credentials, and audit for SUID/sudo misconfiguration — all of which requires the
  written authorisation this engagement does not have.
