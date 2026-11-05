# E6 deployment acceptance ledger — non-waivable release gates

**Review:** 2026-11-05. **Candidate:** E6 PR #125, starting at E5 main `80c3ca566ecdaef1181209fab90fc23184796251`.
**Decision:** **NOT DEPLOYMENT-READY.** The new supplied UI is unfinished; no operator security authorization or production lab evidence has been supplied.
This register follows master-roadmap §38 G01–G10 and E0–E9 phase-freeze policy. Historical tests are sources for verification candidates, not automatic acceptance. Do not equate E5 engineering freeze with full V2 production approval.

| Gate | Candidate evidence already available | Specific unpassed obligation | Current decision |
|---|---|---|---|
| G01 — capability/workflow | Existing Core, API/CLI, `ENGINE_V2_E6_SERVICE_UI_HANDOFF_MATRIX.md`, 793 static controls | Exhaustive live capability/transport/client inventory and controlled full solo chain | OPEN |
| G02 — authorization/execution | E1 regression suite and `test_engine_v2_e6_mutation_guards.py` candidate | Authorized target/pivot/redirect/secondary DNS and legacy direct-dispatch no-bypass lab; UI cannot grant permissions | OPEN |
| G03 — independent verification | Existing validator and retest tests | End-to-end replay/verification and conservative inconclusive/failure outcomes with retained proof | OPEN |
| G04 — evidence/coverage/report | E3 audit and evidence seals, E6 empty-evidence parity candidate | Reproducible complete report, redaction, missing/skipped coverage, independent trust anchor, audit fault recovery | OPEN |
| G05 — durable lifecycle | E5 bounded freeze and 12/12 exact-head pre/post merge CI; E6 cross-client tests candidate | Full retained legacy CLI/API/web/UI/no-bypass integration and realistic host/network effect failure cases | OPEN |
| G06 — supplied UI | 22 templates/793 source controls registry | **Blocked: new UI not ready**. Approved visual design, all live controls, keyboard/accessibility/responsive and parity | BLOCKED: UI |
| G07 — install/deployment | E5 staging Docker/systemd smoke and offline snapshots | Supported target host/upgrade, TLS/secrets, external witness, storage/network outage, backup retention and recovery | OPEN |
| G08 — release CI | E5 merge run and E6 PR CI candidate | Exact final E6 release candidate across Python versions, browsers, supported OS and required test environments | OPEN |
| G09 — release identity | Existing beta version and package workflow | Approved release version/tag, reproducible artifact/checksums, release workflow and intended index publication | OPEN |
| G10 — documentation/decision | This ledger and E6 contract matrix | Reconciled current crosswalk, operator deployment/security approval, accepted evidence links, final release decision | OPEN |

## Engineering delivery tracks that can proceed while UI is blocked

1. **C1/C3**: enforce Core/API/CLI durable status and cancellation parity, no browser-owned drainer, no implicit success.
2. **C2**: adversarial authorization/consent/policy and legacy-bypass audit; negative tests independent of UI.
3. **C4**: deterministic observed-versus-verified evidence, coverage, report provenance and failure/recovery.
4. **C6**: isolated headless, wheel, systemd, Docker, off-host backup witness and fault-injection on approved inert fixtures.
5. **C5 (blocked)**: no editing of UI design until it is ready; later build per-control checks against approved variants.

## Gate closeout format

Every gate requires: exact final commit SHA, affected requirement IDs, exact test assertion, supported runner/environment, CI or lab run link, operator authorization for real targets where required, expected/observed results, retained evidence location, limitations, reviewer and decision. Unknown, skipped, unexecuted, draft or stale checks **do not pass**. Only the operator may authorize production deployment.

**Safe candidate:** bounded E5 headless engineering staging with inert approved inputs only; E6 has no full deployment sign-off.
