# Engine v2 E1 — Correctness and security acceptance

Status: **OPEN for formal E1 acceptance**. Current `main` at `f0b25d3629d776b433f72c83db679bb41313c812` already includes a number of E1 security and recovery implementation slices and source tests. The previous 'working branch only' claim is historical; do not use it to infer unmerged code.

## Required gates

- [ ] Follow-up job draining and one-shot startup isolation across CLI and worker paths
- [ ] Nikto metadata/issue parsing, duplicate handling and raw evidence fidelity
- [ ] Scope and DNS/IP/redirect/pivot boundary fail-closed behavior, including target normalization
- [ ] Target and session identity revalidation, stale worker ownership and race handling
- [ ] Idempotency, retry, uncertain external effects and crash/recovery safety
- [ ] Evidence provenance, persistence and audit failure behavior
- [ ] Adversarial tests for unauthorized execution, malformed targets and policy changes
- [ ] Full CI, static analysis, supported platform smoke and exact-SHA acceptance evidence

Historical E1 branch note (2026-11-02): `fix/engine-v2-e1-acceptance-2026-11-02` was a work-in-progress snapshot, **not** the current implementation source of truth. Related E1 source/tests are already on `main` alongside E2–E5 work. Do not reopen resolved bugs from this dated branch-only note. Formal E1 acceptance remains open until exact candidate-SHA adversarial tests, deployment and evidence are recorded. See `ENGINE_V2_CODE_VS_ROADMAP_AUDIT_2026-11-03.md` for the updated bounded checkpoint breakdown.
