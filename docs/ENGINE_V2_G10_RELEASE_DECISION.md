# Engine V2 G10 Delivery Status and Release Decision

**Assessment date:** 2026-11-23


**Current PR #268 snapshot — 2026-11-23.** PR #268 is open and unmerged on `codex/v2-bounded-startup-recovery-20261121`, exact source head `27faf26ecb20f5b22dad33fab031c240fbfcf47e`, based on main `e8907a1fc369d2b8a92a9e72cf25c0236bb412ce`. Exact-head CI [45171571410](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/45171571410) passed all 20 jobs, including Python 3.11–3.13, G01, E1, both E5 deployment smokes, G07, package/setup, and SearchSploit. README freeze [45171571405](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/45171571405), Dashboard [45171571440](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/45171571440), Findings [45171571442](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/45171571442), and Scope [45171571399](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/45171571399) passed. This bounded batch permanently retires the web validation and retest routes to HTTP 410 without replay or finding mutation, blocks the legacy human-resolution route from changing V2 findings, and adds a fake-`dig` crash/recovery regression through the real catalog provider, ToolRunner, parser, SQLite and recovery path. The regression verifies restart uncertainty, explicit recovery from the sealed provider result, duplicate-recovery refusal, and no later dispatch; it uses a local fake executable and does not prove general exactly-once effects. The branch also contains the versioned digest-bound coverage projection and proposal-only CLI validation/retest aliases. Broader E0–E6 implementation, remaining legacy CLI/Metasploit/session work, provider-specific effect recovery and qualification, full UI wiring, integrated acceptance, external qualification, and release approval remain open. G10 remains **HOLD — NOT READY TO DEPLOY**.

**Decision:** **HOLD — NOT READY TO DEPLOY**
**Current main code head:** `f32ce0913d460f046f6d984ec54a1f7f5d775409` (PR #226 merged 2026-11-20). The exact PR head `65cae35059934a6032cb250bca3752152c88d918` passed CI [44833852913](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833852913) (20/20 jobs), README freeze [44833852900](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833852900), and dashboard acceptance [44833853031](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833853031) before merge. The squash merge has the same source tree as that tested PR head; GitHub reports no separate check run on the merge commit yet. Main's previous exact-head CI [44728330739](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44728330739) and README freeze [44728330736](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44728330736) passed on `668ce5ee72851b257c3b734511d9fa9354cbca04`. The local Engine V2 regression set passes 293 tests; separate server and legacy-boundary checks pass 152 tests. PR #226 added passing focused regressions for operator-enabled legacy scope denial and cancellation after a real provider side effect, confirming uncertainty and no replay. Provider-specific outcome verification and end-to-end accepted provider evidence remain open. This is engineering evidence, not exact release-candidate qualification. The release decision remains HOLD because exhaustive execution-path coverage, remaining legacy-client migration and supported-client parity, provider-specific effect reconciliation, complete UI behavior/control wiring, and deferred external qualification remain open. No V2 release tag, package publication, or production deployment exists.

> **Draft-branch G02 evidence — 2026-11-20, regression code at `ebe52c3e1dbb5362f8030a9ad1dd9aea24a4116f`:** the focused authorization, follow-up, session/pivot, scope, runner, and workflow set passed **254 tests** locally. It includes a new cancellation-during-authorization case that confirms the current task and dependent DAG work are cancelled before any dispatch event. This adds bounded internal evidence; full caller, session, pivot, race, and cross-transport acceptance remains open. The later documentation-only draft head `9e3ed2c824b541158b6c83037454688d78d7aed6` passed exact-head CI [44823570731](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44823570731), README freeze [44823570610](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44823570610), and dashboard acceptance [44823570841](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44823570841). Any later code or documentation update still requires exact-head verification before acceptance.

## Delivery sequence

Complete the agreed V2 engine, V2 UI, and remaining solo-v1.0 implementation scope first. Continue internal unit, integration, security, static, and browser testing throughout development. Do not hold implementation work waiting for real-target, independent-review, manual-accessibility, or production-like deployment evidence.

After the full agreed implementation is complete and internal checks pass, perform final external qualification: authorized real-target testing, independent evidence/security review, manual accessibility review, and production-like multi-worker, installation, upgrade, rollback, backup, and recovery exercises. Production rollout follows a passing exact-candidate qualification. Deferred P6–P8 / E7–E9 expansion is not part of this completion gate.

Previously recorded bounded CI and lab runs remain evidence for their stated scope. They do not prove the complete product is finished, and they do not need to be repeated during implementation unless an internal regression requires it.

## Current decision basis

The decision remains **HOLD** because the implementation is not complete. The open implementation work includes exhaustive V1 execution-path coverage, migration of remaining legacy clients to shared V2 lifecycle services, full transport/client parity, provider-effect recovery, and completion of all agreed UI controls and workflows. The repository has route-level browser suites, but route coverage alone does not prove every UI action is implemented and wired to real services.

The release checklist also contains post-implementation external qualification items. Those items remain pending by sequence; they are not prerequisites for continuing implementation.

## Gate record

| Gate | Implemented or recorded now | Remaining work and sequence |
|---|---|---|
| G01 | Bounded V2 crosswalk and exact-tree isolated lab evidence; top-level CLI inventory and AST guard. Candidate `75880425cdaf4857989f229638e59c5b65de099f` passed CI run #43624338670; G01 chain artifact #14125401711 is retained. PR #224 also passed the current controlled-lab chain. The dormant Qt direct-dispatch path is now default-denied by an explicit environment gate. | Complete exhaustive V1 caller and dispatch-path inventory during implementation. Defer additional real-target qualification until the full scope and internal checks are complete |
| G02 | Bounded authorization/execution regressions, including retired no-dispatch `/api/run` and `/api/ai/run` compatibility routes, redirect boundaries, scope recheck at dispatch, and a stop request during authorization that cancels the task and dependent DAG work before dispatch | Close remaining caller, Metasploit/session/pivot, cancellation-race, and cross-transport authorization gaps with internal tests |
| G03 | Bounded independent-validation/retest behavior; unsupported methods and kinds remain conservative | Complete supported-method and finding-state behavior and internal regression coverage |
| G04 | Report overhaul and bounded evidence/coverage checks | Complete implementation of evidence and report requirements. Defer independent audit anchoring, external custody review, and final evidence qualification until implementation is complete |
| G05 | Bounded shared lifecycle, durable service work, attempt-bound provider-result recovery, and manual reconciliation; malformed persisted findings are rejected before sealing. Direct web tool and AI execution/answer routes now return HTTP 410 without dispatch or resume. | Complete remaining in-scope CLI/Metasploit/session/validation client migration and parity, provider-specific effect verification and recovery, and broader crash/recovery evidence |
| G06 | 22 production routes and page-level browser suites exist. Findings pagination and snapshot behavior are covered; exact-head Findings, Scope, Dashboard, and README workflows pass. Remaining UI controls and workflows are still open. | Complete all agreed UI workflows, control wiring, service behavior, and internal browser/API tests. Final visual, manual accessibility/security, and deployment qualification happen after implementation; there is no UI implementation freeze |
| G07 | Bounded setup/staging and upgrade-smoke evidence | Complete implementation and internal install/recovery checks. Defer production-like upgrade, rollback, and disaster-recovery qualification until the whole product scope is ready |
| G08 | Bounded candidate-CI acceptance is recorded | Run required exact-candidate CI after implementation is complete |
| G09 | Release-safety code and tests exist; no V2 release identity/publication exists | Create and verify the release identity and artifacts after the candidate passes qualification |
| G10 | This HOLD record | Reassess only after implementation, internal checks, external qualification, and release-artifact verification are complete |

## Deferred external qualification checklist

After implementation is complete, record evidence for:

- A controlled target WHAXON is explicitly authorized to assess, with scope, constraints, and retained run evidence.
- Independent review of evidence integrity and audit anchoring.
- Manual UI review against the agreed desktop design and accessibility criteria.
- Security review of the completed candidate.
- Production-like install, upgrade, rollback, backup/restore, worker recovery, and preservation of queued or uncertain work.
- Exact candidate SHA, CI/lab outcomes, limitations, verified publication artifacts, and the final release decision.

These items are deliberately sequenced after feature completion. This record does not authorize testing a target or deploying to production.

## Reopen condition

Keep this decision at **HOLD** while implementation or internal checks remain incomplete. Once they pass, proceed to the deferred external qualification checklist. Record a new G10 decision after the exact release candidate and its qualification evidence are reviewed.
