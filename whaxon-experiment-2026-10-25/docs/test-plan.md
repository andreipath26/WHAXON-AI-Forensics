# Test Plan

Built from `docs/research-map.md` (what the code claims), `docs/literature-review.md` (how such
claims are measured) and the first target responses. Ordered by (information gain × safety) rather
than by convenience.

Each experiment states: question, hypothesis, preconditions, procedure, expected secure behaviour,
possible outcomes and interpretation, success/failure criteria, safety, evidence.

---

## Priority 1 — offline, zero target traffic

### E1 — Scope decision matrix
- **Q:** Which target forms does `ScopeManager.check()` allow, and does any decision depend on DNS?
- **H:** H1. **Preconditions:** none; fully offline.
- **Procedure:** construct a synthetic scope file (`127.0.0.1/32`, `*.example.test`, `example.com`
  in scope; `127.0.0.2` out) and evaluate 14 forms including decimal/hex/IPv4-mapped encodings,
  userinfo and fragment confusion, trailing dot, wildcard sub-domain, and a name whose A records
  are outside every rule.
- **Expected secure behaviour:** identical addresses decided identically; no rule authorises an
  address outside the declared CIDRs.
- **Outcomes:** (i) all encodings denied → string layer sound; (ii) name allowed while all addresses
  denied → authorisation is nominal, not address-bound; (iii) encoded form allowed → bypass.
- **Success criterion:** every form classified and explained by the matching rule.
- **Safety:** no network.
- **Evidence:** `evidence/scope/decision-matrix.json`.

### E2 — Adapter fidelity on recorded output
- **Q:** Does each adapter record only what the tool observed?
- **H:** H2. **Preconditions:** repository's recorded artefacts.
- **Procedure:** feed silent/default/404 ffuf shapes; parse `data/proof-dvwa/engagement.json`
  per job; diff adapters on shared paths.
- **Expected secure behaviour:** absent input fields are absent (or explicitly `null`) in output.
- **Failure criterion:** a field appears with a value the input never contained.
- **Safety:** no network.
- **Evidence:** `evidence/adapters/fidelity.json` (synthetic part).

### E3 — Validator benchmark
- **Q:** Is `verified` sound (never emitted for a non-vulnerable case) and complete (emitted for
  exploitable cases the engine can reach)?
- **H:** H3. **Preconditions:** local labelled server.
- **Procedure:** 12 cases covering DVWA low/medium/high semantics for XSS, SQLi, command injection,
  LFI, plus two decoys (timing, marker) and one POST-only sink. Both validator paths.
- **Expected secure behaviour:** no false `verified`; `candidate` rather than `refuted` when the
  engine cannot test.
- **Outcomes and interpretation:** a false `verified` on a decoy = unsound marker/timing rule;
  `refuted` on a truly exploitable case = over-claimed negative; `candidate` on an unreachable kind =
  documented coverage limit.
- **Success criterion:** every verdict mapped to ground truth and scored (TP/FP/FN/TN, J).
- **Safety:** loopback only.
- **Evidence:** `evidence/benchmark/*`.

### E4 — Redirect destination binding
- **Q:** Does an allowed target that redirects cause a denied host to be contacted?
- **H:** H1. **Preconditions:** two loopback addresses.
- **Procedure:** A (`127.0.0.1`, in scope) 302s to B (`127.0.0.2`, explicitly denied). Run
  `ToolRunner.run_tool` with `curl -L`; also `Validator._fetch`.
- **Expected secure behaviour:** the redirect is refused before B is contacted, or B is denied.
- **Outcomes:** B contacted → scope escape via tool execution; B not contacted → defence holds.
- **Success criterion:** B's access log is the arbiter, not the tool's stdout.
- **Safety:** no external traffic.
- **Evidence:** `evidence/scope/redirect-escape.json`.

## Priority 2 — live, non-destructive

### E5 — Unauthenticated surface map
- **Q:** What does the deployment serve before authentication?
- **Procedure:** 18 named routes (DVWA menu), benign markers, one request each, sequential.
- **Expected secure behaviour:** vulnerability modules redirect to `login.php`.
- **Failure criterion:** a module executes or discloses without a session.
- **Safety:** GET only; no state change.
- **Evidence:** `evidence/live/routes.json`, `request-log.jsonl`.

### E6 — Confirmation with matched controls
- **Q:** Are the suspected XSS/LFI/command-injection primitives real, and under which identity?
- **Procedure:** positive payload + inert marker control + (for command injection) benign-IP control.
- **Expected secure behaviour:** no raw reflection, no file disclosure, no command execution.
- **Interpretation guard:** the *control* must show the endpoint is otherwise functioning, otherwise
  a 200-with-error would be misread as success.
- **Safety:** `id` only; `/etc/passwd` only; no writes.
- **Evidence:** `evidence/live/confirm.json`.

### E7 — Adapter adjudication against live truth
- **Q:** Do the statuses in the shipped artefact match a live measurement of the same paths?
- **Procedure:** 14 GETs; compare with ffuf/gobuster records; caveat cross-deployment differences.
- **Safety:** read-only.
- **Evidence:** `evidence/adapters/fidelity.json` (live part).

## Priority 3 — verification of the study's own results

### V1 — Independent client re-test
- **Q:** Do the findings survive a different HTTP implementation?
- **Procedure:** `scripts/verify_findings.py` replays F1–F6 with `curl`, no cookie jar, literal
  URLs, grep on raw bytes.
- **Shared-mode error to avoid:** both clients use the same OS resolver and the same TLS stack; a
  DNS or TLS fault would be common-mode.
- **Evidence:** `evidence/verification/verification.json`.

### V2 — Negative controls everywhere
Every positive has an adjacent negative: inert marker, benign IP, intended include file, static
page for phpinfo, direct out-of-scope request for the scope bypass.

### V3 — Characterisation tests
`tests/test_research_observations.py` pins ground truth (labels earned by behaviour) and the
observed defects, so a future fix fails loudly instead of silently invalidating the numbers.

## Excluded experiments (with reasons)

| Planned | Excluded because |
| --- | --- |
| SQLi/brute-force/stored-XSS live tests | database uninitialised; resetting it is destructive to a shared host (H6) |
| Upload → web shell | creates persistent state on a shared host |
| Container escape / root on target | outside the authorised ceiling |
| Nmap/Nikto/Nuclei orchestration | binaries absent, installation impossible (B-001, B-002) |
| Stealth/WAF evasion | not authorised; irrelevant to the research questions |
