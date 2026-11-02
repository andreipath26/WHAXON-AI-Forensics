# Decision Log

**Record type:** contemporaneous, written while acting. Timestamps UTC.
**Not** a transcript of private model computation — see `logs/trace-availability.md`.

Fields per decision: id, time, objective, established facts, hypotheses + evidence for/against,
assumptions, candidate approaches, trade-offs, selection + rationale, expected outcome /
falsification, invocation, observation, prediction confirmed?, assessment change, next decision.

---

## D-001 — How to discover the environment

- **Time:** 2026-10-25T11:38Z
- **Objective:** satisfy Phase A without assuming any tooling exists.
- **Established facts:** workspace `/workspace/chats/631d3594b40a92b083bca535` contains only `.git`
  (a worktree pointer to a shared bare repo). Host is Linux 6.1.102 x86_64, Ubuntu 24.04.5.
- **Hypotheses:** (a) the runner is a constrained non-root container; (b) security tools are
  preinstalled. 
- **Candidates:** (1) `apt install` a toolkit first; (2) probe first, install only what is proven
  necessary and permitted.
- **Trade-offs:** (1) risks wasted time on a blocked action and mutates the shared host;
  (2) slower start but no unauthorised system changes.
- **Selected:** (2). Rationale: installation rights are unknown and the mission forbids assuming
  availability; a probe also produces the Phase A artefact directly.
- **Expected outcome:** either `apt` works (then install nmap/ffuf) or it is blocked.
- **Falsification:** if installation succeeds cleanly, hypothesis (a) is weakened.
- **Invocation:** `id`, `/etc/os-release`, `capabilities`, `sudo -n true`, `docker info`, tool sweep.
- **Observation:** non-root, `CapEff=0`, sudo refused (`no new privileges`), docker socket denied,
  zero security tools present, Python 3.12 + pip + PyPI reachable, DNS + HTTPS functional.
- **Prediction confirmed?** Yes for (a), no for (b).
- **Assessment change:** the study must not depend on third-party scanner binaries; it must build
  its own audited HTTP tooling and exercise WHAXON's code paths directly.
- **Next decision:** D-002.

## D-002 — Which repository copy is authoritative, and which branch to publish on

- **Time:** 2026-10-25T11:39Z
- **Objective:** obtain the research repository without disturbing other chats.
- **Established facts:** `/workspace/repo.git` is a *bare* repo shared by several chat worktrees
  (`refs/heads/main` and another chat's branch both at `cc82ec5`); the current branch
  `freebuff/631d…` sits on an empty scaffolding commit.
- **Hypotheses:** (a) the upstream GitHub repo is public and clonable; (b) the workspace is meant to
  become the publication tree.
- **Candidates:** (1) `git clone` directly into the workspace — impossible, `.git` exists and the
  directory is a worktree; (2) clone to `/tmp`, copy the working tree (excluding `.git`) into the
  workspace, set `origin` to the upstream URL, create a research branch; (3) work only in `/tmp`.
- **Trade-offs:** (2) keeps one auditable tree, preserves the host's checkpointing and leaves the
  shared bare repo's other refs untouched. (3) risks losing work across restores.
- **Selected:** (2). Branch `research/forensics-2026-10-25` created from the current HEAD; local
  identity set repository-locally only.
- **Expected outcome:** clean tree equal to upstream `main`, plus my new branch.
- **Invocation:** `git clone --depth 50 … /tmp/whaxon-clone`; `rsync -a --exclude .git`;
  `git remote add origin …`; `git checkout -b research/forensics-2026-10-25`.
- **Observation:** clone succeeded (public read access works). 29 top-level entries staged as
  untracked in the worktree, matching upstream.
- **Assessment change:** publication path exists *locally*; remote write access still unverified.
- **Next:** verify GitHub write credentials (→ B-004 blocker expected).

## D-003 — Target identification

- **Time:** 2026-10-25T11:39Z
- **Objective:** discover what the supplied target actually is before testing it.
- **Established facts:** HTTP 200, 5930 bytes, `Server: nginx/1.31.8`, `X-Powered-By: PHP/8.5.12`,
  body title `Welcome :: Damn Vulnerable Web Application (DVWA)`, menu of DVWA modules, cookie
  `security=low`.
- **Interpretation (not observation):** the target is a DVWA installation published by
  pentest-ground.com as a deliberately vulnerable practice application, behind an nginx reverse
  proxy. `robots.txt` = `Disallow: /`.
- **Candidates:** (1) treat as a normal production app and limit to passive recon; (2) treat as an
  intentionally vulnerable lab and test the DVWA modules with non-destructive payloads;
  (3) cover only the two standard DVWA credentials and stop after login.
- **Selected:** (2) with a self-imposed non-destructive ceiling (D-004).
- **Why:** the mission designates this URL as the assessment target; the application's only purpose
  is to be attacked; DVWA's entire design is exploitable-by-construction. Denying that would leave
  the mission's experiments untestable, while unlimited exploitation would be irresponsible on a
  shared public host.
- **Falsification:** if the host published terms forbidding testing, or if the instance showed
  signs of other tenants' data, the scope would be reduced to passive observation.
- **Observation:** no terms page linked from the app; `robots.txt` is the only policy artefact.
  Full analysis in `docs/scope-and-rules.md` §3.

## D-004 — Authorised-scope ceiling (self-imposed)

- **Time:** 2026-10-25T11:41Z
- **Objective:** fix what may and may not be done to the target before any intrusive request.
- **Established facts:** shared public target; no operator-supplied rules of engagement beyond the
  mission statement; DVWA offers destructive features (`setup.php` DB reset/create, file upload,
  RCE).
- **Reasoning:** three risks are asymmetric — they cannot be undone by me and may affect other
  users: (i) database reset/destruction, (ii) persistent uploaded files/web shells,
  (iii) high-volume brute force. Everything else (read queries, reflected payloads, single
  non-destructive shell commands) is reversible or stateless.
- **Selected ceiling:** allowed — unauthenticated recon, login with the two documented default
  credentials, reading vulnerability pages at security levels low/medium/high, SQL injection
  (read-only `UNION`/error probes, no writes/drops), reflected XSS with marker payloads, command
  injection with **non-destructive read-only commands** (`id`, `uname`, `pwd`, `ls` of the web root
  only), file-inclusion probes for local files that DVWA itself serves, weak-session-ID observation.
  Prohibited — `setup.php` create/reset, any file upload, password brute force beyond 3 attempts,
  any privilege escalation on the host, any write/`DROP`/`INSERT`/`UPDATE` SQL, denial of service,
  scanning other hosts or ports of pentest-ground.com.
- **Consequence for Phase E:** the "privilege boundary" is the web-application → OS boundary. Root
  on the target is **not** authorised and **not** attempted; the assessment reports the strongest
  identity actually observed inside the application context.
- **Recorded in:** `docs/scope-and-rules.md`.

## D-005 — Research framing: audit the instrument, not just the target

- **Time:** 2026-10-25T11:45Z
- **Objective:** choose a research question that yields an auditable contribution rather than a
  DVWA walkthrough.
- **Established facts (from reading the repo):** WHAXON's README makes two strong, falsifiable
  claims: (i) scope is enforced fail-closed; (ii) findings are `candidate` until a payload is
  replayed and the response shows "the proof", with "no LLM decides if a finding is real".
  The repo also ships `data/proof-dvwa/engagement.json`, a prior DVWA run.
- **Observation from that shipped artefact:** it records `ffuf` findings `.htaccess`/`.htpasswd`
  with `"status": 200` while the *same engagement's* `gobuster` job records `403` for the same
  paths. `size` is `null` for all ffuf findings. This is an internal contradiction inside a
  published proof artefact.
- **Hypotheses:** H1 scope boundary is name-based and can be escaped by redirection/DNS;
  H2 ffuf adapter fabricates a 200 status when ffuf's output has none;
  H3 replay "verification" has systematic false-positive classes; H4 command injection gives
  web-server-level RCE but not root.
- **Candidates:** (1) produce a standard pentest report of DVWA; (2) evaluate WHAXON's evidence
  claims empirically on DVWA + offline fixtures, and measure the gaps.
- **Selected:** (2). Rationale: (1) reproduces well-documented DVWA behaviour and adds little
  auditable knowledge; (2) makes the *instrument* the object of study, which is what the mission's
  repository supplies, and produces measurements another researcher can re-run.
- **Expected outcome:** H2 likely confirmed by code reading; H1 partially falsified (validator has
  redirect hardening) but perhaps true for tool execution; H3 measurable; H4 likely confirmed.
- **Next:** read `scope.py`, `validator.py`, `runner.py`, `ffuf.py` (done for most), then build
  experiments.

## D-006 — Code-reading targets chosen by claim, not by size

- **Time:** 2026-10-25T11:46Z
- **Objective:** locate the code that implements the two headline claims.
- **Method:** `grep -rn "scope.check\|OutOfScopeError"`, `grep -rln verified`, read
  `docs/scope.md`, `docs/findings.md` claims in README.
- **Observation:** enforcement points are `runner.run_tool`, `runner` session paths (smb/wmi),
  `recon.py`, CLI/web/TUI/GUI entry points, `ai/executor.py`. Validation lives in
  `core/validator.py` with two replay paths (`_fetch` and `_replay_ctx`).
- **Key code facts (verbatim observations, see `docs/research-map.md`):**
  - `Validator._fetch` and `Validator._replay_ctx` both install a `NoRedirect` opener and the
    `_replay_ctx` path pins the host/port to the target and strips `Authorization`/`Cookie`.
  - `FfufAdapter.parse` sets `status = int(...) if m.group("status") else 200` — a default of 200
    when the line carries no status.
  - `Validator.validate` (non-context path) treats `delta >= 3.0s` as `verified` for *any*
    replayable kind, checking timing before markers; the `_replay_ctx` path deliberately downgrades
    a timing-only signal to `candidate`.
- **Assessment change:** H1 as originally stated ("validator follows redirects off-scope") is
  **contradicted for the validator**; it survives only for external tools and DNS. H3 is refined:
  the timing false-positive exists in one path and was already mitigated in the other — so the
  research question becomes *how much* the two paths disagree, not *whether* a flaw exists.
- **Next:** build the offline experiment suite (E1–E3) before touching the network again.

## D-007 — Record the failure rather than hide it

- **Time:** 2026-10-25T11:46Z
- **Observation:** the first version of `scripts/env_probe.sh` emitted invalid JSON: the helper
  `tools_json()` returned `"k":v` pairs without braces, and the assembly step called
  `json.loads()` on that fragment. Second bug: a stray `)` from a removed subshell made the script
  a syntax error at line 130.
- **Cause classification:** tooling (my own script), not environment, not target, not hypothesis.
- **Fix:** wrapped the fragment in `{...}` at load time; rewrote assembly to read exported
  environment variables inside a quoted heredoc, eliminating shell/JSON quoting interaction.
- **Verification:** `jq -e .` passes; `evidence/env/environment.json` validated; values spot-checked
  against the terminal observations.
- **Logged in:** `logs/errors-and-blockers.md` B-003. Preserved because a reader must be able to see
  that the environment report was produced by a script that had to be fixed.

---

# Phase W — WHAXON as the assessment engine (user correction, 2026-10-25T12:50Z)

## D-008 — Which repository is the instrument under test

- **Time:** 2026-10-25T12:52Z
- **Objective:** the correction names two repositories. Establish which one is the tool and whether
  it matches the research tree already in the workspace.
- **Observation:** `WHAXON` main = `5b61fa5` (2026-10-23); `WHAXON-AI-Forensics` main = `a577fc7`.
  Both declare `version = "0.11.16"`, yet `diff -rq` shows 6 source differences: the research tree
  contains a command-injection validator, a scope fix, `adapters/commix.py` and extra
  business-impact mappings that the tool tree lacks.
- **Hypotheses:** (a) they are mirrors and the difference is cosmetic; (b) they are the same product
  at different points in history; (c) the research tree is a *fork* shipped ahead of the public tool.
- **Selected:** measure against the **tool repo at `5b61fa5`** in its own venv (`.venv-whaxon`),
  because that is what users install; note the divergence wherever it changes a conclusion.
- **Falsification:** if the two trees were identical, the distinction would not matter. They are not.
- **Next:** D-009.

## D-009 — How WHAXON should be exercised without root and without shims

- **Time:** 2026-10-25T12:54Z
- **Objective:** run a real assessment through WHAXON, not a simulation, under B-001 (no root).
- **Established facts:** `whaxon recon` is a built-in passive engine (no external binary);
  `whaxon run <tool>` needs `data/tools.json`, which `whaxon init` does not create (defect D4);
  ffuf/nmap/nikto are absent and cannot be apt-installed.
- **Candidate approaches:** (1) abandon active scanning; (2) fake tool output; (3) install real
  binaries through permitted means and register them via WHAXON's documented catalog format.
- **Selected:** (3). ffuf from its official release with the published checksum verified; sqlmap from
  its upstream git commit; catalog entries written using `docs/tools.md`'s schema. No shims, no
  scope edits to force a pass, no `--allow-out-of-scope`.
- **Rationale:** (2) would fabricate results, which the correction forbids; (1) would leave the
  research question untested.
- **Next:** D-010.

## D-010 — The target for the active phase: live DVWA vs a ground-truth lab

- **Time:** 2026-10-25T13:06Z
- **Objective:** choose a target where WHAXON's *detection* and *validation* claims can both be
  scored against known truth.
- **Facts:** the live DVWA has no database (B-006), so its SQLi module cannot be exploited; the
  live target's real vulnerabilities (LFI/RCE/XSS) are of kinds WHAXON's scanners and validator do
  not cover.
- **Selected:** run **both** — live DVWA for discovery/surface (scope-authorized), and a local
  SQLite-backed lab with an injectable and a parameterized endpoint for vulnerability testing with
  ground truth by construction.
- **Falsification guard:** the first lab fixture was string-simulated; sqlmap rejected it (job
  `6f5b6e2a80f7`, "does not seem to be injectable"). Rather than accept that as a WHAXON negative,
  the fixture was replaced with a real database — a correction of *my* instrument, recorded as F4.
- **Next:** D-011.

## D-011 — Reaching a lab URL when the product's URL/CIDR defect blocks it

- **Time:** 2026-10-25T13:06Z
- **Problem:** `whaxon scope --check http://127.0.0.1:8099/…` is denied while `127.0.0.1` is allowed
  (defect D3), so the authorized lab was unreachable through WHAXON.
- **Candidates:** (1) disable scope (`--disable` or `--allow-out-of-scope`) — rejected, that
  circumvents the guardrail; (2) patch `scope.py` — rejected, the product must be measured as
  shipped; (3) add an **exact-host** in-scope rule `127.0.0.1`, which is narrower than the existing
  `127.0.0.0/8` CIDR rule the engagement already authorizes.
- **Selected:** (3), with the reason written into the scope file's `notes` field so the change is
  visible in the artefact, enforcement still enabled, and out-of-scope hosts still denied.
- **Next:** D-012.

## D-012 — Interpreting `candidate` on a genuine vulnerability

- **Time:** 2026-10-25T13:30Z
- **Observation:** WHAXON's sqlmap found 5 findings on the injectable endpoint (4 critical `sqli`)
  and none on the parameterized control; its own `validate` returned `candidate` for all four, and
  the engagement report labels every finding "candidate by engine" with a reason.
- **Competing explanations:** (a) the vulnerability is not real; (b) the validator is broken;
  (c) the validator replays an insufficient payload.
- **Discriminating test (independent, curl-only):** replay WHAXON's stored payload — no error, body
  identical to WHAXON's own baseline (V3); replay a minimal `id=1'` — real SQLite error containing
  WHAXON's own marker `sqlite` (V4).
- **Assessment:** (c). Root cause isolated to `PayloadLoader.get_payloads('sqli')[0] == '`+HERP'`
  (a MongoDB snippet harvested from a documentation fence) and `validate()` always using index 0.
  This is a **completeness** defect, not a soundness one: WHAXON declined to claim verification it
  could not obtain, which is the correct behaviour.
- **Next:** publish the evidence package (research/whaxon_execution_evidence.md).
