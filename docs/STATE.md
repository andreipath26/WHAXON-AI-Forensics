# WHAXON — Project state

**Reviewed:** 2026-11-02
**Repository / inspected branch:** `andreipath26/WHAXON-AI-Forensics` / `main`
**Source baseline:** `6fa1fa5f9bcff9b7afffb87ca908b0f78562fa3b`
**Authority:** [Product trajectory](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md), especially P0–P5 and §38. This is a dated summary; [the baseline register](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) holds detailed evidence.

## Release and verification

The package is **0.11.16, Beta** in source and metadata. **v1.0 acceptance is OPEN.** Package-index/tag publication was not independently rechecked for this review; do not repeat an old publication claim as a current verification.

Exact-baseline [CI #41488450899](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41488450899) passed all nine jobs. Python 3.11, 3.12 and 3.13 each reported **1,408 passed, 14 skipped**, with Ruff, mypy and distribution builds passing. Python 3.12 also passed sdist-resource and clean-wheel checks. Ubuntu/macOS/Windows setup smoke, headless Linux Waitress startup and curated apt/Homebrew installation/scanner smoke passed.

This certifies those checks on that SHA. It does not certify every external tool, platform, transport, deployment mode, UI control or v1.0 release criterion. No local runtime/browser tests were executed for this documentation review; future commits require their own CI evidence.

The old `Route.session_host` collection failure is fixed in current source and covered by the passing matrix. The earlier approvals Refresh-queue failure is historical, not the current CI state. Preserve the session identity guards; do not reopen resolved defects because an old document still lists them.

## What exists

- Shared Core/runner, SQLite job/finding/session persistence, adapter registry, 24 packaged catalog entries and guarded command/session execution.
- Reconnaissance, normalized findings, request-context handling, deterministic supported validation/observation/blind checks, retest and coverage/report paths. POST/state-changing context replay is refused; do not imply arbitrary authenticated replay support.
- Engine v2 immutable contracts/digests/manifests, persisted missions/tasks/attempts, scheduler leases/retries/deadlines/fencing, bounded per-run concurrency/task limits and an initial constrained provider bridge.
- Doctor/setup profiles, deterministic plans, explicit approval-bound Python installation, curated apt/Homebrew tools and diagnostics/operation/history UI/API paths. Native Windows external-tool installation remains manual.
- Supplied UI with 22 production page templates/destinations and 23 UI-v2 test modules. Web root redirects to `/ui-v2`; desktop `gui/embed.py` still loads legacy `/ui` and needs migration. Legacy design source remains preserved unchanged.

Code and tests demonstrate substantial implementation. Registered/installed/verified/authorized are separate states; component presence does not equal full product acceptance.

## Immediate correctness issue and remaining gates

**P1 priority:** `coverage`, `validate`, `retest` and `recon` call `Core.initialize()` with its default queue draining enabled. They can dispatch unrelated older pending jobs before their own action; `run` and `workflow` explicitly use `drain=False`. This is a source-confirmed startup side-effect risk, not an executed exploit demonstration. Add per-command no-unrelated-dispatch tests and repair the contract while preserving intentional worker/follow-up behavior.

Remaining trajectory:

| Gate | Current position |
|---|---|
| P0 baseline/cleanup | Evidence and principal paths refreshed; exhaustive capability/control inventory remains open |
| P1 correctness/Trust Layer | Substantial guards and validators exist; startup issue and integrated authorization/evidence/retest/coverage acceptance remain open |
| P2 shared durable lifecycle | Scheduler primitives exist; durable mission-wide budgets/cancellation/audit/reconciliation and CLI/API/UI parity remain open |
| P3 install/headless | CI smoke passes; clean-platform/upgrade/offline/partial-failure/restart, backup/restore and advertised service-mode acceptance remain open |
| P4 supplied UI | Integration exists; complete control inventory, visual/responsive/accessibility/parity, external assets and desktop default remain open |
| P5 release | Controlled-lab end-to-end proof and §38 G01–G10 acceptance remain open |
| P6–P8 expansion | Full bounty autonomy, multi-target/competition, broad providers, vulnerability patch application and enterprise remain gated/deferred |

## Repository simplification

The tracked baseline has **534 files, including 82 Markdown files**. The old 102-file count and claims that an experiment archive remains in the current tree are stale. [Due diligence](DOCUMENTATION_RECONCILIATION.md) distinguishes exact duplicate/no-consumer removals from dependency-bound retirement and retained design/evidence/legal resources. Cleanup now removes the 23 verified non-runtime superseded files; runtime and branch retirements remain gated.

The 56 remote branches include main, ten other tips strictly behind it and 45 diverged tips. Retire only after exact-tip/reference checks; divergence needs content/PR reconciliation. Old branch tips are not merge instructions.

Scope remains application-level preflight, not a network firewall or connection-time DNS pin. External tool requests/redirects require deployment-specific egress controls. Installation changes are not generally rolled back; hash chains without an independent trust anchor are not immutable. AI proposes and explains; it neither authorizes operations nor determines verification.

Resume from current main/CI and the trajectory's next unmet gate. Do not restart completed implementation from historical notes or infer a global completion percentage from tests/pages.
