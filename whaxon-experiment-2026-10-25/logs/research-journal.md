# Research Journal

**Record type:** contemporaneous narrative, appended as work happened (UTC timestamps).
**Relationship to other logs:** this file narrates; `logs/decision-log.md` records decision state;
`logs/experiment-index.md` indexes experiments and artefacts; `logs/trace-availability.md` states
what traces exist at all and what does not (no private chain-of-thought is available or claimed).

---

## 2026-10-25T11:38Z — Initialisation

Workspace `/workspace/chats/631d3594b40a92b083bca535` contained only a `.git` pointer into a
*shared bare repository* (`/workspace/repo.git`) with several chat branches. Nothing else existed:
no project files, no tools, no credentials. First action was therefore discovery, not assumption
(mission §3, operating principle 1).

`uname` → Linux 6.1.102 x86_64, Ubuntu 24.04.5. `id` → uid 104028665, non-root. `CapEff=0`.
`sudo -n true` → blocked by `no_new_privileges`. `docker info` → socket permission denied.

**Consequence recorded immediately:** no root, no containers, no system package installation.
Any plan requiring Nmap/Nikto/SQLmap or a local DVWA container must be replaced, not wished for
(D-001, B-001, B-001b).

## 11:39Z — Repository obtained

Public HTTPS clone of `andreipath26/WHAXON-AI-Forensics` succeeded (depth 50). To avoid touching
other chats' branches, the working tree was copied into this workspace (`.git` excluded) and
`origin` was set to the upstream URL; a research branch was created from the existing HEAD
(D-002). Local git identity set repository-locally only.

## 11:39Z — First contact with the target

`curl -sk https://pentest-ground.com:4280/` → 200, 5930 bytes, `Server: nginx/1.31.8`,
`X-Powered-By: PHP/8.5.12`, `Set-Cookie: security=low`, body title **DVWA**. The menu lists the
classic DVWA modules. `robots.txt` → `Disallow: /`.

Interpretation (kept separate from observation): a deliberately vulnerable training app published
for practice, behind an nginx reverse proxy. This is the basis for the scope decision (D-003), not
the mere existence of a URL.

## 11:41Z — Scope fixed before intrusive testing (D-004)

Wrote the ceiling before sending payloads: allowed = unauthenticated recon, login with the two
documented defaults, read-only SQLi reasoning, XSS markers, `id`-only command injection, `/etc/passwd`
LFI, observing `phpinfo`/`setup`; prohibited = DB reset, uploads, brute force, credential reads,
host privilege escalation, other hosts. Rationale: three risks are asymmetric on a *shared* host
and cannot be undone by me.

## 11:42Z — Reading the instrument

Read `core/scope.py` (249 lines), `core/validator.py` (369), `core/runner.py` (625),
`adapters/ffuf.py` (90), `docs/scope.md`, `docs/findings.md`, `docs/STATE.md`.

Two code facts stood out and reshaped the plan:

1. `FfufAdapter.parse`: `status = int(...) if m.group("status") else 200` — a default, not an
   observation.
2. `Validator` has **two** replay paths with *different* rules for timing evidence: the legacy
   query-parameter path returns `verified` on `delta ≥ 3.0 s`; the hardened `_replay_ctx` path
   returns `candidate`.

The second fact **falsified my initial H1** as stated ("the validator follows redirects off-scope"):
both paths install `NoRedirect` and the hardened path pins host+port. The hypothesis was narrowed to
destination binding for *tools* and DNS, and the validator's redirect defence became a negative
result to report (D-006).

## 11:45Z — Repository's own proof artefact

`data/proof-dvwa/engagement.json` (produced 2026-10-17 against a local DVWA container at
`172.17.0.3`) contains ffuf findings for `.htaccess`/`.htpasswd` with `status: 200` while the same
engagement's gobuster job records `403`. Every ffuf finding has `size: null`. This is an internal
contradiction inside the project's own published evidence, and it became the seed of E9 (D-005).

## 11:46Z — Tooling failure and fix (B-003, D-007)

`scripts/env_probe.sh` emitted invalid JSON twice: a helper produced `"k":v` pairs without braces
while the consumer called `json.loads`, and a stray `)` from a removed subshell made the script a
syntax error. Diagnosed as my own bug, not the environment's; rewrote JSON assembly around exported
environment variables and a quoted heredoc. `jq -e .` then passed and the file hash was logged.
The failure is preserved rather than hidden because the environment report depends on this script.

## 11:47Z — Baseline test suite

`pip install -e ".[dev]"` → 15 failed / 627 passed / 74 errors: missing `flask`, `textual`,
Playwright browser. After `.[dev,web,tui]`: **1 failed / 756 passed / 63 errors**, where the one
failure is `weasyprint` missing (PDF) and all 63 errors are the absent browser. Recorded as the
pre-change baseline so that any later regression is attributable.

## 11:52Z — The plan meets the target (H6, B-006)

Login POST redirected to `setup.php`; `setup.php` reported "Click on Create / Reset Database".
Then `GET /vulnerabilities/sqli/?id=1` (no session) returned a 461-byte PHP fatal error:
`Uncaught mysqli_sql_exception: Table 'dvwa.users' doesn't exist`.

Two things at once:

* **The database is uninitialised**, so stateful modules cannot be assessed.
* **The module executed for an anonymous client** — no login redirect, footer `Username: Unknown`.

The tempting fix — press *Create / Reset Database* — is exactly the action my own rules prohibit on
a shared host. So the live plan was re-scoped: assess what executes without a database, record the
DB-dependent hypotheses as blocked. This is the moment the study stopped being "a DVWA walkthrough"
and became "what does the deployment actually expose, and what does the instrument claim about it".

## 11:57Z — Unauthrated surface map (E5)

18 routes, one request each. Results: `phpinfo.php` **200 / 87 KB** to an anonymous client;
`setup.php` **200** including the reset control and DB host; `sqli`/`sqli_blind`/`xss_s` fatal errors;
`fi`, `xss_r`, `exec`, `upload`, `weak_id`, `csrf`, `security` all render normally.
`/config/` → 403 leaking `Apache/2.4.69 (Debian)` and `Port 80` (proxy chain visible).

First attempt at command injection used `GET` and produced nothing. Rather than conclude "not
vulnerable", the HTTP method was questioned — DVWA's exec module reads `POST`. That correction
matters: a lenient reading would have recorded a false negative (see E6).

## 12:03Z — Confirmation with controls (E6/E7)

Paired positives with matched negatives:

* **LFI**: `/etc/passwd` → 18 account lines; control `?page=include.php` returns the intended file.
* **XSS**: `<img src=x onerror=...>` reflected verbatim in `<pre>`; inert marker also reflected;
  non-reflecting page does not contain the payload.
* **Command injection**: `ip=127.0.0.1;id` → `uid=33(www-data) gid=33(www-data)`; benign IP → four
  ICMP replies, no `uid`.

The identity answered the privilege-boundary question: the application's own account (B2), not root.

## 12:10Z — Measuring the instrument (E8–E11)

Built a 12-case labelled local benchmark (DVWA low/medium/high semantics + two decoys + a POST-only
sink) and drove WHAXON's **own** `Validator` through both code paths.

**My own emulator had a bug first:** the shell emulation decoded the canary hex as bytes instead of
treating it as literal text, so `cmdi_get` came back `candidate` and would have been written up as a
WHAXON completeness failure. Caught by reading the generated payload format rather than trusting the
verdict; fixed; re-ran. A second bug (GET against a POST-only sink executed) was fixed the same way.
Both are exactly the failure mode this study is about — an instrument reporting a plausible result
that is wrong — and are recorded rather than tidied away.

Clean results: legacy path TP2/FP2/FN4/TN4 (J = 0.000); hardened path TP2/FP1/FN4/TN5 (J = 0.167).
A page that merely prints `postgresql` is `verified` on **both** paths. A genuine UNION injection is
`refuted`. `PayloadLoader` index 0 for `sqli` is `` `+HERP ``, for `lfi` and `command_injection` it
is `<?php`.

Scope experiments: the string-level matrix is genuinely sound (decimal, hex, IPv4-mapped, userinfo,
fragment all denied). But `example.com` is authorised while both of its A records are denied, and a
permitted `127.0.0.1` host that 302s to explicitly-denied `127.0.0.2` caused the denied host to
record a request from `ToolRunner.run_tool` (the validator's own replay refused the redirect).

## 12:22Z — Independent verification (V1)

Wrote `scripts/verify_findings.py`: `curl`, no cookie jar, literal URLs, grep on bytes. All six
live findings re-confirmed, each with its negative control. The two clients share only the OS
resolver and TLS stack — a stated common-mode risk, partially mitigated by inspecting the chain with
`openssl s_client`.

## 12:27Z — Tests that keep the study honest

`tests/test_research_observations.py` (23 tests): benchmark labels are asserted by *behaviour*,
not by case name; the ffuf invention, the shipped artefact's contradiction, the validator's decoy
false positive, the `refuted` mislabel, the POST gap, the scope matrix and the redirect escape are
pinned. Full suite: **779 passed**, 1 environment failure (`weasyprint`), 63 browser errors — i.e.
baseline + 23, no regression, and no `src/` file modified.

## 12:33Z — Documentation and publication

Wrote the required document set. Publication to GitHub could not complete: the runner has no GitHub
credentials (no `gh` login, no SSH key, no credential helper, no token variable). The push attempt
and its exact failure are recorded in `logs/publication-log.md`; the branch, a bundle and
enablement instructions are provided so an authorised person can publish without re-running
anything.

## Retrospective note (written last, marked as retrospective)

The largest deviation from the mission's expected shape was forced by the target: an uninitialised
database removed the stateful half of a DVWA assessment. The response was to move the research
weight onto claims that *can* be measured offline and deterministically (adapter fidelity,
verification soundness, scope binding), which turned out to be the part of the engagement with a
defensible contribution. The live assessment still produced six verified findings, including
command execution as `www-data`.
