# Engine V2 G10 Release Decision

**Assessment date:** 2026-11-06  
**Decision:** **HOLD — NOT READY TO DEPLOY**  
**Release authorization:** None. No release tag, package publication, or deployment was created by this assessment.

## Decision basis

The bounded acceptance evidence for G01–G05 and G07–G09 is recorded in the [product roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) and [requirements register](ENGINE_V2_ROADMAP_REQUIREMENTS.csv). Those records represent bounded engineering checkpoints, not complete production sign-off.

The release decision remains **NO-GO** because G06 UI acceptance is explicitly deferred until last and is still open. The current static control inventory does not establish that every visible control works; responsive behavior, keyboard/focus accessibility, and visual acceptance are also open. The final release decision must be reviewed again after G06 is completed.

## Gate record

| Gate | Current record | Deployment status |
|---|---|---|
| G01 | Bounded capability crosswalk and controlled-lab chain frozen; exhaustive V1 inventory and real authorized-target evidence remain open | Open beyond bounded scope |
| G02 | Bounded authorization/execution acceptance frozen, including legacy /api/run scope-override and redirect authorization regressions | Open beyond bounded scope |
| G03 | Bounded independent validation/retest acceptance frozen; unsupported methods and kinds remain conservative candidates | Open beyond bounded scope |
| G04 | Bounded report/coverage acceptance frozen; envelope digests are unsigned and external audit anchoring remains open | Open beyond bounded scope |
| G05 | Bounded shared lifecycle acceptance frozen; legacy-client migration and provider-effect/production recovery remain open | Open beyond bounded scope |
| G06 | UI functional, responsive, visual, keyboard/accessibility, and unsupported-feature checks remain incomplete; work is deferred until last per operator instruction | **Open — release blocker** |
| G07 | Bounded setup/staging acceptance frozen; production security, upgrade/partial-failure, and whole-system disaster recovery remain open | Open beyond bounded scope |
| G08 | Bounded candidate-CI acceptance frozen at PR #139 merge 390fa6b; exact-head CI #2239 passed 14/14, including sdist and clean-wheel smoke on Python 3.11–3.13 | Accepted bounded scope |
| G09 | Bounded release-safety acceptance frozen at PR #140 merge 1d4a8f2; exact-head CI #2249 passed 14/14. No V2 tag or publication exists | Open until a real release identity/publication is validated |
| G10 | This record sets the current no-go decision. Final release approval is pending the remaining gates and a new review after G06 | **No-go checkpoint recorded** |

## Known deployment blockers

- G06 is not ready for acceptance and is intentionally scheduled last.
- The V1 caller inventory is not exhaustive; desktop, terminal, legacy API, AI, and provider paths remain outside complete V2 lifecycle ownership.
- G04 has no independent external audit trust anchor. Report SHA-256 envelopes are unsigned and do not prove authenticity.
- G05 production recovery and reconciliation of provider-side effects are not fully accepted.
- G07 production upgrade, partial-failure recovery, security review, and disaster-recovery acceptance are incomplete.
- G09 has no new V2 release candidate, matching tag, successful release workflow, or verified PyPI publication. The existing v0.11.16 tag is unsigned and has no exact-SHA CI run in this repository.
- The exact authorized production target and external audit anchor have not been supplied or accepted.

## Reopen condition

Keep this decision at **HOLD** until the open non-UI deployment criteria are resolved and G06 is completed last. Then perform an exact release-candidate review, verify the release workflow and published artifacts, and record a new explicit G10 decision. This checkpoint does not authorize publishing or deployment.