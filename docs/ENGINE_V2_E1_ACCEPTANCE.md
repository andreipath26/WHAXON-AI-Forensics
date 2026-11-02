# Engine v2 E1 — Correctness and security acceptance

Status: **OPEN**. Working branch only. Do not merge before all criteria have passing evidence on the exact candidate commit.

## Required gates

- [ ] Follow-up job draining and one-shot startup isolation across CLI and worker paths
- [ ] Nikto metadata/issue parsing, duplicate handling and raw evidence fidelity
- [ ] Scope and DNS/IP/redirect/pivot boundary fail-closed behavior, including target normalization
- [ ] Target and session identity revalidation, stale worker ownership and race handling
- [ ] Idempotency, retry, uncertain external effects and crash/recovery safety
- [ ] Evidence provenance, persistence and audit failure behavior
- [ ] Adversarial tests for unauthorized execution, malformed targets and policy changes
- [ ] Full CI, static analysis, supported platform smoke and exact-SHA acceptance evidence

All E1 changes remain on `fix/engine-v2-e1-acceptance-2026-11-02`. One PR and one merge into `main` only after acceptance. E2–E6 are out of scope.
