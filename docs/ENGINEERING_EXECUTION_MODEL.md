# WHAXON Engineering Execution Model

**Status:** Main engineering rule — non-negotiable  
**Applies to:** Every WHAXON phase, subsystem, interface, and release.

## Main rule

**NON-NEGOTIABLE. Applies to every WHAXON phase, subsystem, interface, and release.**

Develop WHAXON through coordinated parallel workstreams wherever work can safely proceed independently. Roadmap phases define scope, dependencies, and acceptance criteria; they do not require needless serial execution. Optimise for the shortest verified end-to-end delivery time without sacrificing architecture, security, evidence, or release quality.

### Required rules

1. **One source of truth:** the roadmap, repository state, dependency graph, decisions, PRs, and acceptance evidence must stay aligned.
2. **Map dependencies first:** identify prerequisites and stable interfaces. Parallelise independent work; sequence only genuine dependencies and safety gates.
3. **Prioritise the critical path:** work first on blockers that prevent the most downstream progress. Recalculate when conditions change.
4. **Agree contracts before parallel work:** define shared schemas, APIs, state machines, error semantics, security boundaries, evidence formats, and compatibility requirements.
5. **Bounded ownership:** assign each workstream explicit scope, owner, files/interfaces, dependencies, deliverables, and tests. Avoid concurrent edits to the same files; coordinate shared-file changes through one integration owner.
6. **Integrate continuously:** merge small increments against shared contracts; run focused tests immediately and broader regression at integration boundaries. Do not wait for an entire phase.
7. **Independent adversarial review:** security, authorization, scope enforcement, evidence integrity, and recovery require review separate from implementation wherever practical.
8. **Verification is part of the task:** code presence or an agent's assertion is not completion. Require relevant unit, integration, security, browser/E2E, packaging, and compatibility checks; record actual results.
9. **Preserve the five principles:** know the environment; understand impact; recommend before acting; act only with consent; leave durable, attributable, tamper-evident evidence. Parallelism never bypasses them.
10. **Bound concurrency:** use isolated branches/worktrees where available, sensible worker limits, small changesets, explicit merge order, and one integration authority. Avoid duplicated effort and uncontrolled agent spawning.
11. **Record failure and recovery:** blocked work, failed checks, partial effects, cancellation, uncertain outcomes, conflicts, and recovery must be visible. Never claim success when outcome or evidence is unknown.
12. **Release on integrated evidence:** phase/release completion requires all components to work together and acceptance gates to pass. Individually completed components do not equal a working platform.

### Standard workstream lifecycle

Define outcome and acceptance tests → map dependencies and interfaces → assign bounded ownership → implement independent tasks concurrently → test against contracts → integrate continuously → conduct independent review → run cross-component regression → record evidence and update status.

### Required coordination records

Maintain an active dependency graph and critical path; a workstream register (scope, ownership, status, blockers, affected paths, acceptance); shared contract/version decisions; integration queue and merge order; and verification records linking completion claims to commands, CI runs, reviews, and limitations.

### Concurrency decision

Parallelise only when interfaces are stable, ownership is isolated, and outcomes are independently testable. Sequence work when another task changes its contract, data model, security boundary, migration, or precondition. If safe ownership is unclear, resolve or split the work first. Do not parallelise merely to increase agent count.

### Success measures

Optimise verified end-to-end lead time, early blocker discovery, low integration conflict, reduced rework, and reliable release acceptance—not agent count, branch count, lines of code, or reported completion percentages.

**This rule supersedes older roadmap wording that implies unnecessary serial execution.** Existing phase order remains binding wherever a real dependency, safety gate, or acceptance prerequisite requires it.

---

