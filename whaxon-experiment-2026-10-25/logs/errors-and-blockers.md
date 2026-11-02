# Errors and Blockers

Every material failure, with cause classification: **environment**, **tooling**, **hypothesis**,
**target**, or **unresolved**. Failures are preserved here even when a later attempt succeeds.

---

## B-001 — No root on the runner; system package installation impossible

- **Detected:** 2026-10-25T11:44Z
- **Attempted:** `sudo -n true`; scan of `/proc/self/status` capabilities.
- **Actual behaviour:**
  `sudo: The "no new privileges" flag is set, which prevents sudo from running as root.`
  `CapPrm: 0`, `CapEff: 0`; `ulimit` grants nothing unusual; user is `104028665(fb631d3594b40a92b083bca535)`.
- **Cause:** environment (container security policy).
- **Impact:** `apt-get install nmap nikto sqlmap ffuf` is impossible; no kernel-level
  experimentation is possible.
- **Alternatives considered:** (a) static binaries from GitHub releases — possible for Go tools but
  unnecessary; (b) reimplement the minimum probing I need in Python — chosen; (c) container escape —
  never considered, explicitly out of bounds.
- **Resolution:** accepted. Third-party scanner *verdicts* are not required for any hypothesis;
  scanner *output formats* are, and those are reproduced as fixtures.
- **Still blocking?** No.

## B-001b — No Docker daemon (no local DVWA control instance)

- **Detected:** 2026-10-25T11:44Z
- **Attempted:** `docker info` (client 29.1.3 present).
- **Actual:** `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`.
- **Cause:** environment.
- **Impact:** the plan's fallback to run a local DVWA container as a *ground-truth control* is
  unavailable. Ground truth must therefore come from (i) DVWA's documented behaviour, (ii) the
  target's own responses, (iii) purpose-built local test servers where the expected result is
  defined by construction.
- **Resolution:** local stub servers on `127.0.0.1` / `127.0.0.2` implement exactly the response
  semantics needed for the scope and validator experiments.
- **Still blocking?** No.

## B-002 — WHAXON's native scanners absent, so end-to-end orchestration cannot run

- **Detected:** 2026-10-25T11:47Z
- **Attempted:** tool sweep (`nmap`, `nikto`, `nuclei`, `sqlmap`, `whatweb`, `gobuster`, `ffuf`,
  `wpscan`, `hydra` — all missing); see `logs/tool-inventory.md`.
- **Cause:** environment (inherits B-001).
- **Impact:** `whaxon run nmap …` against the target would fail at process spawn
  (`FileNotFoundError`), producing no scan evidence. The tool-orchestration *layer* therefore cannot
  be validated against a live target in this runner.
- **Alternative taken:** (1) drive WHAXON's adapters with the repository's own recorded scanner
  output (adapter fidelity, E2); (2) drive WHAXON's validator against live findings produced by this
  study's audited client (E4); (3) register a trivial local "tool" in a private catalog to exercise
  `Runner.run_tool` dispatch and scope gating (E3) — this uses WHAXON's real code path without
  pretending an external scanner ran.
- **Still blocking?** Partially: no claim in this study depends on a real Nmap/Nikto run, but the
  limitation is recorded in `docs/limitations.md`.

## B-003 — `scripts/env_probe.sh` produced invalid JSON (fixed)

- **Detected:** 2026-10-25T11:46Z
- **Attempted:** `bash scripts/env_probe.sh`.
- **Actual:** `json.decoder.JSONDecodeError: Extra data: line 1 column 7 (char 6)` and
  `scripts/env_probe.sh: line 130: syntax error near unexpected token ')'`.
- **Cause:** tooling (my script). Two defects: `tools_json()` emitted `"k":v` pairs without the
  enclosing braces while the consumer called `json.loads()` on the fragment; and a removed command
  substitution left an unmatched `)`.
- **Alternative explanations considered:** (a) shell version incompatibility — rejected, the error is
  a plain syntax error; (b) `jq`/Python JSON library bug — rejected, the failing string was `nmap"`
  at char 6, i.e. the missing brace.
- **Fix:** brace the fragment at load time; assemble JSON from exported environment variables inside a
  quoted heredoc so no nested quoting survives shell expansion.
- **Verification:** `jq -e . evidence/env/environment.json` exits 0; spot values match terminal output;
  SHA-256 recorded in `evidence/env/probe.log`.
- **Preserved because:** the environment report is only trustworthy if its generator is public.

## B-004 — GitHub write/read authentication unavailable (publication blocker)

- **Detected:** 2026-10-25T11:40Z (initial) and re-confirmed by every `scripts/env_probe.sh` run.
- **Attempted:** `gh auth status`; inspection of `~/.ssh`, `~/.gitconfig`, `~/.git-credentials`;
  `git config --global --get credential.helper`; `env | grep -E '^(GITHUB_TOKEN|GH_TOKEN|...)'`.
- **Actual:** `You are not logged into any GitHub hosts.`; no SSH directory; no credential file; no
  helper; **0** token environment variables.
- **Cause:** environment (no credentials provisioned for this runner).
- **Impact:** the requirement to publish checkpoints to `andreipath26/WHAXON-AI-Forensics` cannot be
  fulfilled by the agent. Cloning (public read) works; pushing does not.
- **Mitigation:** (1) every checkpoint is committed locally on `research/forensics-2026-10-25`; (2) a
  push is attempted and the exact error captured in `logs/publication-log.md`; (3) the branch tip hash
  and a `git bundle` are produced so an authorised person can transfer the work with one command;
  (4) precise enablement instructions are recorded in `docs/limitations.md` §Publication.
- **Still blocking?** Yes — external to the runner. Explicitly reported in the final report rather
  than claimed as success.

## B-005 — `robots.txt` disallows all agents (scope ambiguity, resolved by decision)

- **Detected:** 2026-10-25T11:44Z
- **Observation:** `https://pentest-ground.com:4280/robots.txt` →
  `User-agent: *` / `Disallow: /`.
- **Cause:** target policy artefact.
- **Analysis:** `robots.txt` governs crawler indexing, not an authorised assessment of an
  intentionally vulnerable training application; a target whose only content is DVWA cannot be
  "crawled" in the indexing sense without exercising its vulnerabilities by accident. Nevertheless the
  directive signals "do not automate against me", which sharpens the obligation to keep volume low and
  payloads non-destructive.
- **Decision:** proceed under the mission's explicit designation, with a hard request budget, a single
  sequential session, no directory brute force with large wordlists, and the D-004 ceiling.
  Residual uncertainty is documented rather than erased (`docs/scope-and-rules.md` §3.3).
- **Still blocking?** Not blocking, but it is an ethical caveat attached to the whole live phase.

## B-006 — Target DVWA database is uninitialised (blocks all stateful modules)

- **Detected:** 2026-10-25T11:52Z
- **Attempted:** `POST /login.php` with DVWA's documented defaults, then `GET /vulnerabilities/sqli/?id=1`.
- **Actual:** the login POST returns `302 -> setup.php`; `setup.php` renders "Click on the 'Create /
  Reset Database' button"; `sqli` returns a 461-byte body:
  `Fatal error: Uncaught mysqli_sql_exception: Table 'dvwa.users' doesn't exist in
  /var/www/html/vulnerabilities/sqli/source/low.php:11`.
- **Cause:** target state. The database was never created, or was dropped.
- **Impact:** SQL injection, blind SQLi, brute force, stored XSS, CSRF, insecure CAPTCHA and weak
  session-ID testing are all unreachable. `docs/research-hypotheses.md` H7 stays unresolved.
- **Alternative considered and rejected:** submit the "Create / Reset Database" form. Rejected —
  it destroys the schema for every concurrent user of a shared public host, which the scope rules
  in `docs/scope-and-rules.md` §4 prohibit. The prohibited action was not performed.
- **Workarounds taken:** (1) assess what executes without a database (LFI, reflected XSS, command
  injection, phpinfo, setup page) — which turned out to be five of eight findings; (2) move the
  quantitative instrument work to a labelled local benchmark whose semantics are defined by
  construction.
- **Still blocking?** Yes for the stateful half of DVWA. Recorded, not worked around.

## B-007 — Two bugs in the study's own benchmark emulator (fixed before reporting)

- **Detected:** 2026-10-25T12:12Z and 12:16Z
- **Symptom 1:** `cmdi_get` was reported `candidate` on both validator paths.
  **Cause:** `experiments/benchmark/server.py` decoded the canary's `$(printf <hex>)` argument as
  hex *bytes*, whereas the shell prints the argument literally. The emulator therefore never emitted
  the marker, and WHAXON was about to be credited with a completeness failure it did not have.
  **Fix:** use the hex token literally; `cmdi_get` then verified as it should.
- **Symptom 2:** `cmdi_post` (a POST-only sink) verified via a GET.
  **Cause:** the emulator's `restricted` flag was inverted for that case, so a GET executed the
  simulated command. **Fix:** restrict by (case, method) pair; the legacy path now correctly returns
  `candidate` because it cannot reach a POST sink.
- **Cause classification:** tooling (this study's own code). Not environment, not target, not
  hypothesis.
- **Why it is recorded prominently:** this is precisely the failure mode the study is about — a
  plausible verdict that is wrong because the instrument, not the target, is at fault. The numbers
  in `evidence/benchmark/confusion.json` are from the corrected emulator; earlier runs (uncorrected)
  are not reported as results.
- **Secondary check that would have caught it faster:** reading the *generated payload string*
  before trusting the verdict. That is now the first thing a reader should do with any
  `candidate` result.
