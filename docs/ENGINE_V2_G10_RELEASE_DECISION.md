# Engine V2 G10 Release Decision

**Assessment date:** 2026-11-06  
**Decision:** **HOLD — NOT READY TO DEPLOY**  
**Source reviewed before this documentation-only reconciliation:** `main` at `0cef416155623199d8cb551b809dd469d62b4778`; exact-head CI run `42253317306` passed all 20/20 jobs. **Release authorization:** None. No V2 release tag, package publication, or deployment was created by this assessment.

## Decision basis

The bounded acceptance evidence for G01–G05 and G07–G09 is recorded in the [product roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) and [requirements register](ENGINE_V2_ROADMAP_REQUIREMENTS.csv). Those records represent bounded engineering checkpoints, not complete production sign-off.

The release decision remains **NO-GO** because G06 UI acceptance is explicitly deferred until last and is still open. Current code has page-level browser suites across all 22 production routes, but these do not establish complete control behavior, approved desktop visuals, manual keyboard/accessibility review, independent security review, or rollout/rollback acceptance. `AGENTS.md` makes the product desktop-only and freezes UI implementation; historical mobile/responsive requirements in older records are superseded. Re-review G10 only after the remaining gates are evidenced and G06 is explicitly reopened and accepted.

## Gate record

| Gate | Current record | Deployment status |
|---|---|---|
| G01 | Bounded V2 crosswalk/lab acceptance is frozen; current main adds a top-level CLI inventory and AST guard. Exhaustive V1 caller inventory and real authorized-target evidence remain open | Open beyond bounded scope |
| G02 | Bounded authorization/execution acceptance frozen, including legacy /api/run scope-override and redirect authorization regressions | Open beyond bounded scope |
| G03 | Bounded independent validation/retest acceptance frozen; unsupported methods and kinds remain conservative candidates | Open beyond bounded scope |
| G04 | Bounded report/coverage acceptance remains frozen; PR #144 report overhaul merged at `edb427b` from exact head `28543e3`, exact-head CI run `42249696631` passed 20/20. Unsigned digests and external audit anchoring remain open | Open beyond bounded scope |
| G05 | Bounded shared lifecycle acceptance frozen; legacy-client migration and provider-effect/production recovery remain open | Open beyond bounded scope |
| G06 | Browser test suites cover the 22 production routes, but all 22 deployment rows and D1–D6 sign-offs remain OPEN. UI implementation is frozen; acceptance is desktop-only under `AGENTS.md` | **Open — release blocker** |
| G07 | Bounded setup/staging acceptance is frozen. PR #143 expanded upgrade smoke to six runs across Python 3.11–3.13: 0.11.14→candidate 0.11.16 and same-version 0.11.16 reinstall; exact-head CI run `42232819920` passed 22/22 and merge `78470c8`. Catalog/scope/job/V2 state preserved; production security, rollback, broader compatibility and disaster recovery remain open | Open beyond bounded scope |
| G08 | Bounded candidate-CI acceptance remains frozen at PR #139 / CI #2239 (14/14); current main exact-head CI run `42253317306` also passed | Accepted bounded scope |
| G09 | Bounded release-safety code/tests exist, but no V2 tag, package publication or GitHub Release exists; full release identity remains open | Open until a real release identity/publication is validated |
| G10 | This record sets the current no-go decision. Final release approval is pending the remaining gates and a new review after G06 | **No-go checkpoint recorded** |

## Known deployment blockers

- G01 exhaustive V1 caller coverage and real authorized-target evidence remain open.
- G06 is not ready for acceptance and is intentionally scheduled last; UI implementation is frozen and all 22 page rows remain OPEN.
- The V1 caller inventory is not exhaustive; desktop, terminal, legacy API, AI, and provider paths remain outside complete V2 lifecycle ownership.
- G04 has no independent external audit trust anchor. Report SHA-256 envelopes are unsigned and do not prove authenticity.
- G05 production recovery and reconciliation of provider-side effects are not fully accepted.
- G07 production upgrade, partial-failure recovery, security review, and disaster-recovery acceptance are incomplete.
- G09 has no new V2 release candidate, matching tag, successful release workflow, or verified PyPI publication. The existing v0.11.16 tag is unsigned and has no exact-SHA CI run in this repository.
- The accepted record does not yet establish a real authorized production target or an independently preserved external audit anchor.

## Reopen condition

Keep this decision at **HOLD** until the open non-UI deployment criteria are resolved and G06 is completed last. Then perform an exact release-candidate review, verify the release workflow and published artifacts, and record a new explicit G10 decision. This checkpoint does not authorize publishing or deployment.