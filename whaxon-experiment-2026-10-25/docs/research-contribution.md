# Research Contribution

## 1. The unresolved question

Pentest orchestrators now convert third-party scanner output into structured findings and, in
WHAXON's case, gate a `verified` label behind automatic payload replay. The README asserts:
"No LLM decides if a finding is real. The proof does." The literature on scanner accuracy
(Bau 2010; Doupé 2010; Fonseca 2007; OWASP Benchmark) measures whether a scanner *reports* a
vulnerability. It does not measure whether the *evidence an orchestrator records* is faithful, nor
whether automatic replay is a sound false-positive filter. That is the question addressed here.

## 2. Hypotheses and assumptions

H1 scope is name-bound rather than destination-bound; H2 the ffuf adapter invents status codes;
H3 replay verification is unsound (false `verified`) and incomplete (true vulnerabilities labelled
`candidate`, sometimes `refuted`); H4 the live boundary is `www-data`; H5 the deployment exposes
modules unauthenticated. Assumptions: an operator's scope file expresses intent; recorded findings
are consumed downstream by humans and by severity/dedup logic; a `verified` label is understood as
a strong claim.

## 3. Method (all reproducible in this repository)

| Experiment | Mechanism | Reproducible without the target? |
| --- | --- | --- |
| E8 validator benchmark | 12 labelled local endpoints implementing DVWA low/medium/high semantics + 2 decoys + 1 POST-only sink; WHAXON's own `Validator`, both code paths; TP/FP/FN/TN, TPR, FPR, precision, Youden J | **yes** — loopback |
| E9 adapter fidelity | synthetic ffuf shapes; the repository's own shipped proof artefact; live adjudication of 12 paths | partly (live part needs the target) |
| E10 scope matrix | 14 target forms through `ScopeManager`; DNS-binding probe | **yes** — offline |
| E11 redirect escape | two loopback addresses, in-scope host 302s to explicitly denied host; `ToolRunner.run_tool` with a redirect-following tool; the denied host's access log is the arbiter | **yes** — loopback |
| E4–E7 live assessment | 65 audited requests, matched negative controls, two independent clients | target required |

## 4. Results

**R1 — Replay verification, measured.** On 12 labelled cases:

| Path | TP | FP | FN | TN | TPR | FPR | Precision | Youden J |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legacy query-parameter | 2 | 2 | 4 | 4 | 0.333 | 0.333 | 0.500 | 0.000 |
| hardened request-context | 2 | 1 | 4 | 5 | 0.333 | 0.167 | 0.667 | 0.167 |

The two paths see identical evidence and disagree, which localises the defect to the *decision
rules*, not to the target: the legacy path accepts a pure 3.2 s timing delta as proof; the hardened
path does not. Both accept the word `postgresql` as proof of SQL injection.

**R2 — A reproducible false-positive counterexample.** A page that returns
"Database driver error: postgresql backend unavailable" for any non-baseline value is `verified` as
SQL injection on **both** paths, with the reason naming the marker. No injection is possible on that
endpoint. Minimal, deterministic, 40 lines of server code (`experiments/benchmark/server.py`,
`marker_decoy`).

**R3 — Negative labels are over-claimed.** A genuine `UNION SELECT` injection is labelled
**`refuted`** ("response identical to baseline"), because the replayed payload is
`PayloadLoader.get_payloads("sqli")[0]` = `` `+HERP ``, a MongoDB snippet extracted from a
documentation code fence. `refuted` is a claim that the finding is false; emitting it from a single
non-event is the most consequential direction of error for a reporting tool.

**R4 — Adapter fields can be invented, and dedupe erases the contradiction.** `FfufAdapter.parse`
writes `status=200` when the input line contains no status. In the repository's own DVWA artefact,
all 12 ffuf findings carry `status=200`/`size=null`, 9 of 12 disagree with the gobuster job from the
same engagement, and `unique_findings` keeps only the first tool's data — so the canonical view
retains the fabricated value and discards the measured one.

**R5 — The scope boundary bounds names, not destinations.** `example.com` is authorised while both
of its A records are denied by the same ruleset (no resolution occurs). A permitted host that
redirects causes the explicitly denied `127.0.0.2` to receive a request from `ToolRunner.run_tool`;
a direct request to the same URL raises `OutOfScopeError`, and the validator's replay path refuses
the redirect. String-level defences (decimal/hex/IPv4-mapped/userinfo/fragment forms) are sound.

**R6 — Live target.** Six independently re-confirmed findings, including unauthenticated LFI
(`/etc/passwd`), reflected XSS in an executable context, and command execution as `www-data`
(`uid=33`); plus unauthenticated `phpinfo()` and a reachable destructive database-reset control.
No root, and root was neither achieved nor attempted.

## 5. Independent verification

- Different HTTP client (`curl`, no session) re-confirms 6/6 live findings with matched negatives.
- Benchmark labels asserted behaviourally in `tests/test_research_observations.py` (attacker
  capability, not case names).
- Scope escape adjudicated by the *denied host's* own access log rather than by tool stdout.
- Instrument verdicts cross-checked between two code paths on the same inputs; disagreement is
  itself reported.
- Full WHAXON test suite re-run: 779 passed; the single failure and 63 errors are environment
  (no `weasyprint`, no browser) and are reported, not suppressed.

## 6. Alternative explanations considered

| Alternative | Tested? | Outcome |
| --- | --- | --- |
| "The fabricated status comes from my synthetic input, not real ffuf" | real recorded output from the repository's own run | same value, all 12 findings |
| "The validator's false positive is an artefact of my decoy" | decoy implements a realistic misconfiguration page; the verdict reason names a *documented* marker from `SQL_ERROR_MARKERS` | holds; the marker list is the cause |
| "The scope escape is my test tool's behaviour, not WHAXON's" | direct request to the same URL is blocked by WHAXON; only the redirect-following tool escapes | holds — WHAXON's gate is fine, its model of the destination is not |
| "The target findings are session artefacts" | fresh sessions, `Username: Unknown`, cookieless `curl` re-test | rejected |
| "The suite failures are caused by this study's changes" | no `src/` file was modified; baseline measured before additions; final run = baseline + 23 new passing tests | rejected |

## 7. What would falsify the contribution

- A version of WHAXON whose validator refuses marker-only evidence would make R2 false; the
  characterisation tests would fail.
- A scope implementation that resolves and pins the destination would make R5 false.
- An adapter contract that permits absent fields to remain absent would make R4 partly false.
- A study showing that `verified`-gated findings are nonetheless reliable *in practice* would not
  contradict R1, but would change its practical weight — that is a downstream question this study
  does not answer.

## 8. Honest statement of novelty

This study does **not** claim to invent scanner benchmarking (OWASP Benchmark, Bau et al., Fonseca
et al.), nor the name-vs-destination hazard (OWASP SSRF cheat sheet; GitLab). Its contribution is:

1. a **measured** soundness/completeness result for automatic replay verification in an open-source
   pentest orchestrator, with a reproducible harness and explicit counterexamples;
2. an **adapter-fidelity** finding (invented fields) demonstrated in a project's own shipped
   evidence artefact, plus the deduplication behaviour that hides the contradiction;
3. a **measurable** demonstration that scope enforcement in such a tool bounds names rather than
   network destinations, including a self-contained 2-address reproduction.

Whether these generalise beyond this project and this target is an open question; the harness is
published so that it can be pointed at other tools.

## 9. Next research questions

1. Do the same three defects appear in other orchestrators that gate findings on replay
   (commercial "verified findings" features)? A portable version of E8 would answer it.
2. Does a resolver-pinned scope gate measurably reduce out-of-scope traffic in real engagements, or
   merely break legitimate CDN/redirecting targets? (Design risk: pinning breaks CDNs.)
3. Does gating on `verified` change analyst behaviour — do `candidate` findings get reviewed, or
   ignored? An instrumented user study, not a benchmark.
4. **Trigger-vs-cause:** can a marker be chosen so that only real injection can produce it (e.g. a
   server-side canary that requires evaluation, like WHAXON's own `$(printf …)` command probe)?
   That mechanism exists in one branch of the code and is a promising direction for the others.
