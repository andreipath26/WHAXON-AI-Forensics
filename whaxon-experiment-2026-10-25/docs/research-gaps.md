# Research Gaps

Each gap states what is known, what competing approaches claim, what remains unproven, and which
assumption the existing approaches rest on. Claims of novelty are limited to what was actually
checked (see §5).

## G1 — Evidence fidelity of tool-output adapters

**Known.** Scanner benchmarks (Bau 2010; Doupé 2010; Fonseca 2007; OWASP Benchmark) score whether a
tool *reported* a vulnerability. Adapters that convert tool output into structured findings are the
layer where "reported" becomes a record with fields: path, status code, response size, severity.

**What competing approaches claim.** Normalisation layers present themselves as faithful
transcriptions of tool output. WHAXON's `docs/findings.md` describes findings as "structured records
extracted from tool output by an adapter" — an extraction, implying fidelity.

**Unproven.** No published work measures whether normalised fields are *observed* or *inferred*.
The distinction matters because downstream severity (`200 → low`, `403 → info`), deduplication and
reporting all key off those fields.

**Assumption at risk.** That a tool's output contains everything the adapter writes. For ffuf's
silent mode it does not.

**Evidence that would settle it.** Feed recorded tool output whose fields are known; compare
adapter output field-by-field; where a field is absent from input but present in output, the adapter
has invented it. E9 does exactly this, and additionally adjudicates against the live target.

## G2 — Soundness and completeness of automatic replay verification

**Known.** Manual reproduction is the accepted false-positive filter (OWASP WSTG; PTES reporting).
Automated scanners are known to over-report. WHAXON adds a middle layer: replay the payload and
label the finding `verified` only if evidence appears.

**What competing approaches claim.** WHAXON's README: "No LLM decides if a finding is real. The
proof does." The claim is that an automatic, deterministic check is a sufficient condition for a
true finding.

**Unproven.** (a) Whether the marker/error/timing signals are *causally* tied to exploitability
rather than to response variance; (b) how much of the exploitable surface the replay path can even
address (it is GET-only and covers three kinds); (c) whether `refuted` — a positive claim that a
finding is false — is safe to emit from a single failed replay.

**Assumption at risk.** That a differential response feature is evidence of injection. A page that
merely prints the word `postgresql` for unrecognised input satisfies the check (E8 `marker_decoy`).

**Evidence that would settle it.** A labelled benchmark with matched negatives, scored with
TPR/FPR/J, distinguishing "cannot test" (`candidate`) from "tested and false" (`refuted`). E8.

## G3 — Scope enforcement as a security boundary, not a feature

**Known.** Fail-safe defaults (Saltzer & Schroeder 1975) and name-vs-destination hazards in
allow-lists (OWASP SSRF cheat sheet; GitLab DNS-rebinding notes). Pentest tooling documents scope as
a safety feature (WHAXON `docs/scope.md`; comparable commercial tools).

**What competing approaches claim.** WHAXON: "WHAXON enforces scope fail-closed." The word
*enforces* implies the network destination is bounded.

**Unproven.** Whether string-level authorisation survives (a) alternative encodings of the same
address, (b) names whose resolution changes, (c) server-directed redirection, (d) tool-generated
sub-requests (pivots, redirects, referrers).

**Assumption at risk.** That the authorised name and the contacted address are the same object.

**Evidence that would settle it.** An adversarial normalisation matrix plus a two-address experiment
where the permitted host redirects to a denied host and the denied host records the contact. E10/E11.

## G4 — Authenticated vs unauthenticated exposure in deployed vulnerable applications

**Known.** DVWA intends a login gate before its modules.

**Unproven (for the specific deployment assessed).** Whether the gate is effective in the
deployment reached at `pentest-ground.com:4280`, and what is disclosed before authentication.

**Evidence.** E4–E7: unauthenticated LFI, XSS, command injection, `phpinfo.php` and `setup.php`
were all reachable; the identity behind the command execution was `www-data`.

## G5 — Privilege boundary after web-level compromise

**Known.** A PHP application runs as its web-server user; `www-data` (uid 33) holds no special
privileges on a standard Debian image.

**Unproven here, by design.** Whether the compromised container admits escalation to root. The
mission authorises the assessment of the target, not host-level exploitation, and the runner cannot
test a container it does not control. Recorded as an open boundary rather than guessed at.

## 6. What was checked before claiming a gap

- The repository's own docs (`docs/scope.md`, `docs/findings.md`, `docs/STATE.md`, `AI_USAGE_AUDIT.md`)
  were read to see which limitations the authors already acknowledge. Where they do (timing
  false positives; replayable-kind coverage), this study **quantifies** rather than rediscovers.
- A literature search (see `docs/literature-review.md`) found scanner-accuracy evaluation and
  SSRF/DNS-binding guidance, but no measurement of adapter-field fidelity or replay-verification
  soundness in pentest orchestration tooling.
- No claim is made that this is the first such work; only that the specific measurements below were
  not found in the sources consulted, and that they are reproducible.

## 7. Gaps deliberately not pursued

| Gap | Why not |
| --- | --- |
| LLM planner safety (prompt injection into the AI layer) | requires provider credentials; no key in this runner; out of the authorised target scope |
| Web UI auth (bcrypt, flask-limiter) | needs a running service and multi-user setup; not reachable without the `web` extra's full deployment |
| Metasploit / pivot chain correctness | requires MSF and a second host; unavailable and out of scope |
| PDF report fidelity | `weasyprint` absent (environment) |
