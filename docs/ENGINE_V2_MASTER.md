Warning: truncated output (original token count: 60261)
Total output lines: 2131

# WHAXON — ENGINE V2 MASTER DOCUMENT

> **Current code audit (2026-11-05; main `9bd4dfe`):** E5 PR #124 **merged** with bounded engineering acceptance and 12/12 exact-PR-head CI. `Core` initializes `JobStore`, `WorkflowRunQueue`, `CapabilityRegistry` and `BoundProviderRouter`; workflow requests implement durable claim, heartbeat, cancellation and reconciliation; CLI and Flask have V2 workflow endpoints. UI PRs #126 and #127 are merged, but deployment gates remain open; Scope-focused acceptance succeeded on final pre-merge head `bf89063`. Full CI run [42063514323](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42063514323) failed when the Python 3.13 lane's Ubuntu mirror download exceeded the 17-minute pandoc-install timeout; its tests did not run, while Python 3.11/3.12 and the other reported jobs passed. This branch increases the bounded timeout without skipping report/PDF tests. Legacy `/api/run` and `/api/ai/run` still exist, so full legacy-to-V2 migration, production deployment, E6 and release gates are NOT accepted. Engine V2 E6 remains frozen until the operator explicitly declares the new UI deployment-ready. Historical pre-merge claims below are superseded.

**Consolidation date:** 2026-11-05. **Baseline:** main at `9157afd250bddb15dd56837d49b3c29492ad5aca`.

> **Authority and interpretation:** This is the single consolidated Engine V2 architecture, implementation, acceptance and evidence reference. The root [master product roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) remains authoritative for product priorities, release requirements and scheduling. Current source plus exact-head test/CI evidence determine implemented behavior; the historical records below are not independent current-status claims. A phase freeze is not production approval. Never infer production deployment readiness from a dated green run, merge, or design.

## Reading order and ownership

1. **Architecture and implementation contract:** Part I (canonical technical design, invariants, execution model, delivery gates).
2. **Dated phase acceptance and operational evidence:** Part II (retain baseline SHAs and acceptance caveats; newer exact-head evidence can supersede older evidence but must be validated).
3. **Historical inventories, audit, provider scope and evidence mapping:** Part III (traceability, not a second roadmap).

The previous `ENGINE_V2_*.md` documents were consolidated here and removed from the working tree; their commits remain in Git history. Edit this master for any new, authoritative Engine V2 synthesis; do not create another competing current-state Engine V2 document. Move future raw CI artifacts or evidence snapshots to dated archival files only when required for provenance. Do not remove acceptance evidence or amend historical results retroactively.

## Consolidated source map

| Purpose | Original retained source | Consolidated location |
|---|---|---|
| Architecture / implementation | [ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md](#source-1-engine_v2_architecture_and_roadmap_crosswalkmd) | Part I, source 1 |
| Baseline / audit | [ENGINE_V2_BASELINE_INVENTORY.md](#source-2-engine_v2_baseline_inventorymd) | Part III, source 2 |
| Baseline / audit | [ENGINE_V2_CODE_VS_ROADMAP_AUDIT_2026-11-03.md](#source-3-engine_v2_code_vs_roadmap_audit_2026-11-03md) | Part III, source 3 |
| Phase-specific acceptance | [ENGINE_V2_E1_ACCEPTANCE.md](#source-4-engine_v2_e1_acceptancemd) | Part II, source 4 |
| Phase-specific acceptance | [ENGINE_V2_E1_QUEUE_LEASE_PRIVACY.md](#source-5-engine_v2_e1_queue_lease_privacymd) | Part II, source 5 |
| Phase-specific acceptance | [ENGINE_V2_E3_PHASE_ACCEPTANCE.md](#source-6-engine_v2_e3_phase_acceptancemd) | Part II, source 6 |
| Phase-specific acceptance | [ENGINE_V2_E3_RECOVERY_BOUNDARIES.md](#source-7-engine_v2_e3_recovery_boundariesmd) | Part II, source 7 |
| Phase-specific acceptance | [ENGINE_V2_E3_RUN_REQUEST_AUDIT_EVENTS.md](#source-8-engine_v2_e3_run_request_audit_eventsmd) | Part II, source 8 |
| Phase-specific acceptance | [ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md](#source-9-engine_v2_e5_caller_inventory_and_rollbackmd) | Part II, source 9 |
| Phase-specific acceptance | [ENGINE_V2_E5_PHASE_ACCEPTANCE.md](#source-10-engine_v2_e5_phase_acceptancemd) | Part II, source 10 |
| Phase-specific acceptance | [ENGINE_V2_E5_SERVICE_READINESS.md](#source-11-engine_v2_e5_service_readinessmd) | Part II, source 11 |
| Phase-specific acceptance | [ENGINE_V2_E6_CONTRACT_FIRST_ACCEPTANCE.md](#source-12-engine_v2_e6_contract_first_acceptancemd) | Part II, source 12 |
| Phase-specific acceptance | [ENGINE_V2_E6_DEPLOYMENT_GATE_LEDGER.md](#source-13-engine_v2_e6_deployment_gate_ledgermd) | Part II, source 13 |
| Phase-specific acceptance | [ENGINE_V2_E6_SERVICE_UI_HANDOFF_MATRIX.md](#source-14-engine_v2_e6_service_ui_handoff_matrixmd) | Part II, source 14 |
| Evidence / provider | [ENGINE_V2_EVIDENCE_MATRIX.md](#source-15-engine_v2_evidence_matrixmd) | Part III, source 15 |
| Evidence / provider | [ENGINE_V2_PROVIDER_CAPABILITY_IMPLEMENTATION.md](#source-16-engine_v2_provider_capability_implementationmd) | Part III, source 16 |

---


---

# Part I — Canonical architecture, roadmap crosswalk and engineering rules



## Source 1: ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md

**Provenance:** [Original source](#source-1-engine_v2_architecture_and_roadmap_crosswalkmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### WHAXON Engine v2 — Architecture Specification & Roadmap Crosswalk

> **E5 post-merge disposition (2026-11-05, superseding 2026-11-04 pending status):** [E5 acceptance review](#source-10-engine_v2_e5_phase_acceptancemd) and merged [PR #124](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/124) establish bounded shared-service E5 engineering acceptance. Its reviewed PR head passed 12/12 CI. This does **not** authorize production deployment or certify migration of legacy direct dispatch; all integrated Engine V2 operator gates remain separately open.

**Status:** Target architecture and implementation contract. This document does not claim the design is implemented.  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Authority:** The master roadmap remains authoritative. Its §0 dependency-driven order governs delivery; this specification does not reorder or bypass it.  
**Historical baseline:** Main at `b27d361e706bcea800300dcf3e8b2e094a429d42`. This was the architecture-design starting point, not the current implementation baseline. Implementation has since begun; use current main-branch source, tests and master roadmap §49 for status. The E0 inventory is a dated migration snapshot, not current-state evidence.

## 1. Architectural decision

WHAXON requires a capability-driven, durable mission-execution platform, not an expanded set of hard-coded tool chains. The engine converts an approved objective into a typed task graph, resolves tasks against registered capabilities, applies deterministic authorization, schedules bounded durable work, collects evidence, verifies results and safely pauses, recovers or replans.

Tools are replaceable providers of capabilities. The orchestration core must not know that a particular chain is Nmap→Nikto, Nuclei→SQLMap, or any other named sequence. A new provider should normally require a manifest, adapter, readiness verification and tests—not a new scheduler branch.

This is an evolution, not a big-bang rewrite. Preserve sound catalog/registry, adapters and parsers, typed AI proposals, deterministic validation, scope controls, events, store, worker and existing interfaces wherever they are correct. Replace narrow coupling at boundaries and prove parity before retiring old paths.

## 2. Non-negotiable invariants

1. **AI proposes; deterministic code decides.** Models may propose objectives, plans and replans. They cannot execute arbitrary commands, authorize, approve themselves, alter policy or bypass validation.
2. **Fail closed.** Missing, stale, ambiguous, expired, contradictory or unverifiable authorization blocks consequential work.
3. **Authorization at every boundary.** Recheck target identity, DNS/IP resolution, redirects, each network action, subprocess/child process, session command, pivot, replay and follow-up task immediately before execution.
4. **Customer and bounty isolation.** Customer engagement authorization and bug-bounty programme authorization have separate policy engines, state, activation and audit contexts. Shared neutral infrastructure is permitted; shared permission decisions are not.
5. **Exact consent.** Approval binds to canonical plan/task digest, scope, parameters, impact, budgets, policy/manifest versions, actor and expiry. Material changes invalidate approval.
6. **Bounded execution.** Enforce task, mission, target, tenant and system limits for time, requests, concurrency, compute, storage, cost and impact. Provide pause, cancellation, emergency stop and circuit breakers.
7. **Durability.** Persist plans, tasks, attempts, approvals, leases, checkpoints, budgets, events and evidence references. Reconcile uncertain attempts before retrying. Never assume exactly-once external effects.
8. **Evidence before claims.** Preserve raw outputs and provenance. Separate observations, hypotheses, candidates, verified, refuted, inconclusive, blocked, skipped and untested. Exit code zero or AI confidence is not proof.
9. **One execution service.** CLI, API, web UI and headless daemon are clients of shared application services. No client owns long-running jobs or reimplements policy.
10. **Auditable state transitions.** Record who/what proposed, approved, denied, executed, verified, cancelled or recovered each action. Audit integrity and failure behavior are explicit.
11. **Extensible, not unrestricted.** Typed execution kinds and provider contracts replace arbitrary plugin/code execution. Untrusted manifests never self-authorize.
12. **Honest readiness.** Registered, installed, smoke-tested, lab-validated and end-to-end-verified are distinct states. Unsupported, partial, skipped and uncertain work is reported honestly.

## 3. Target architecture and ownership

### 3.1 Mission and campaign service
Owns objective, operator/tenant, engagement or programme reference, campaign mode, lifecycle, expiry, budgets and stop conditions. Mission state is durable and independent of a conversation, CLI or browser process. Modes: manual, guided, supervised autonomous and fully autonomous. Modes change approval interaction, never authorization rules.

### 3.2 Planning and task-graph compiler
Accepts typed proposals and compiles versioned graphs containing prerequisites, dependencies, conditions, bounded loops, fan-out/fan-in, joins, human approval gates, retry policies and terminal conditions. Graphs are validated for schema, references, cycles, boundedness, provider compatibility, policy requirements and budgets. Every executable node has typed inputs/outputs, capability, constraints, timeout, impact, idempotency class and success/stop criteria. AI replanning creates a new plan version; no invisible mutation of an approved graph.

### 3.3 Capability registry and provider resolver
Resolves required capabilities to compatible providers based on target/protocol/platform/authentication, execution transport, typed I/O, version compatibility, readiness, resource profile, side effects and policy allowlists. Resolution is deterministic and explainable against a versioned registry snapshot. Missing provider/readiness produces a typed blocked or unsupported outcome, never fabricated success.

### 3.4 Independent authorization services
Provide a common decision interface but distinct customer-engagement and bounty implementations and data boundaries. Customer rules include approved assets, exclusions, rules of engagement, techniques, credentials, time windows, impact/rate/concurrency limits and approval requirements. Bounty rules include source-provenanced programme terms, asset and technique eligibility, third-party boundaries, disclosure terms, programme version, activation and expiry. Decisions return allow/deny/approval-required, reason codes, applicable rules, policy version, evaluated action/target and validity. Re-evaluate at execution time.

### 3.5 Approval service
Approval is explicit, attributable, revocable and bound to the canonical plan/task digest, exact target, parameters, policy and manifest versions, impact, budget and expiry. A material plan, provider, policy or target change invalidates affected approvals. No model, adapter or UI can approve an action.

### 3.6 Durable orchestrator and scheduler
Owns dependency readiness, queues, leases, bounded worker pools, priorities/fairness, per-target and per-mission concurrency, rate limits, deadlines, retries/backoff, circuit breakers, cancellation, pause/resume and crash recovery. It does not construct commands or make policy decisions. Before retrying a lost lease, reconcile whether the previous external effect completed. Use at-least-once delivery plus idempotency/deduplication/reconciliation; do not promise exactly-once external execution.

### 3.7 Execution adapters and workers
Workers receive typed requests and return typed outcomes plus evidence references. Explicit execution kinds:
- Local process: trusted argv construction, no shell interpolation.
- Session/transport: supported remote/session commands with identity, route and pivot context.
- HTTP/API integration.
- Browser workflow, only where explicitly approved and constrained.
- Cloud/provider SDK.
- Local analysis, parsing, correlation and validation tasks that do not contact a target.

Each kind defines credential handling, network boundary, timeout, cancellation, cleanup, output capture and idempotency. Tool output is untrusted data. Raw artifacts, provider/version, invocation identity, timestamps, exit/transport status and parse errors are retained.

### 3.8 Evidence, findings and verification
Separate raw observations from normalized findings and verified conclusions. Version normalizers and retain raw-source links. Preserve asset-specific proof during correlation. Independent verification is a task with its own method, inputs, authorization recheck, outcome and evidence. Retest links to original finding and affected asset/version. Evidence is content-addressed, integrity-checked, access-controlled and carries provenance, redaction and retention metadata. Replay recipes require fresh authorization.

### 3.9 Events, audit and observability
Use typed, schema-versioned events with aggregate/version, actor, correlation and causation IDs. Persist state and event publication through an outbox/transactional pattern. Separate operational logs from audit records. Tamper-evident audit requires a verifiable hash chain or equivalent, protected trust anchor and documented retention/deletion semantics. If required audit persistence fails, consequential execution enters a defined fail-closed state.

### 3.10 Shared application services and deployment
Versioned application/API contracts expose missions, plans, approvals, tasks, progress, capability/readiness inventory, findings, evidence, verification, reports and controls. CLI/web/API/headless call these same services. Long-running work belongs to durable workers, not HTTP requests. Support foreground and headless daemon/service/container forms only after verified acceptance. No desktop, browser or TUI dependency for server operation.

## 4. Canonical domain contracts

Define typed, schema-versioned contracts (no untyped dictionaries at service boundaries) for:

| Contract | Required contents |
|---|---|
| Mission | Objective, owner, engagement/programme reference, mode, lifecycle, expiry, isolation boundary |
| AuthorizationContext | Domain/type, policy ID/version, scope, limits, activation/expiry |
| Plan | Mi…52261 tokens truncated…in a historical mapping of compound roadmap requirements, not current completeness.  
**Detailed ledger:** [ENGINE_V2_ROADMAP_REQUIREMENTS.csv](ENGINE_V2_ROADMAP_REQUIREMENTS.csv).

## Coverage and limitations

| Scope | Requirement entries mapped |
|---|---:|
| P0–P4 | 34 |
| P5–P8 | 21 |
| Engine gates E0–E9 | 10 |
| Solo-release gates G01–G10 | 10 |
| **Total** | **75** |

- 42 entries link candidate implementation/doc artifacts; 68 entries link candidate test artifacts. All referenced file paths were checked against the repository tree, and all 29 explicit test-function references were checked against actual definitions; none was missing.
- The entries correspond to the roadmap's P0–P8 bulleted/numbered/table requirements (plus P5/P7 narrative paragraphs), E0–E9 gates, and G01–G10 release gates. A compound paragraph/bullet may contain multiple acceptance obligations; **this is a source-level index, not an atomic criterion tally**. Future acceptance work must split compound requirements rather than declare them complete as a group.
- `CANDIDATE_MAPPING` means a relevant code or test artifact exists; **it does not mean that test proves the full requirement**. A row without a direct test link has an explicit evidence gap; a row with related tests can still have uncovered clauses.
- `NOT_ACCEPTED` is conservative: no row is counted as a completed acceptance criterion until exact assertion/expected result and a candidate-SHA execution result are recorded.
- All nine post-merge CI check-runs on `c75c03888e35f6147cfae3547f286202bb09fd6e` passed, including Python 3.11/3.12/3.13. This is **overall CI evidence**, not a requirement-level sign-off.

## Verified from source

- **E0:** Architecture crosswalk and dated baseline inventory are present. Historical inventory is not evidence of current implementation state.
- **E1:** Fail-closed scope, Nikto regression, replay/retest and approval tests exist. [E1 acceptance](#source-15-engine_v2_evidence_matrixmd) explicitly remains **OPEN**.
- **E2:** `src/whaxon/core/workflow.py` has typed workflow tasks/plans, digest and approval binding; `src/whaxon/core/capabilities.py` has manifests, requirements and deterministic resolution, with persistence and compatibility tests.
- **E3:** `src/whaxon/core/scheduler.py` implements scheduler execution/heartbeat and retries; workflow/worker tests cover durable leases, deadlines, mission limits, cancellation and uncertain attempts. Wider crash/audit/outbox acceptance remains open.
- **E4:** `src/whaxon/core/providers.py` implements the local catalog-adapter provider bridge with pinned version and readiness; remote/session/browser/cloud transport acceptance is not established.
- **E5–E6:** CLI/API, Core, headless and V2 route tests exist; full shared-lifecycle, per-control UI and release-gate acceptance remain open.
- **E7–E9:** Deferred expansion has partial supporting components, not accepted complete phases.

## Acceptance accounting rule

Do **not** use arbitrary percentages. For every atomic requirement, record a durable: (1) source symbol and path, (2) exact test function and assertion, (3) running environment and commit SHA, (4) result, (5) reviewer/acceptance decision, and (6) limitations. Count `accepted / applicable atomic requirements` only after that evidence exists; explicitly exclude roadmap-deferred features from a solo-v1.0 percentage. Do not substitute a generic passing suite or a file's existence for a requirement's acceptance test.

**Current defensible acceptance percentage: not measured.** The ledger is an auditable inventory and gap register, not a release certification.



---


## Source 16: ENGINE_V2_PROVIDER_CAPABILITY_IMPLEMENTATION.md

**Provenance:** [Original source](#source-16-engine_v2_provider_capability_implementationmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2: Provider and Capability Abstraction

> **2026-11-03 main reconciliation:** The branch and pre-merge gate notes later in this file are development history, not current merge instructions. Current main `f0b25d3629d776b433f72c83db679bb41313c812` includes semantic aliases, explicit provider selection, plan-pinned identity, operation-level reconciliation, and live missing-adapter / manifest / catalog-drift refusal. Full E4 multi-transport parity, live provider substitution and legacy autochain cutover remain unaccepted. See [dated audit reconciliation](#source-16-engine_v2_provider_capability_implementationmd).

The capability registry stores immutable versioned declarations and resolves
requirements deterministically, returning an explainable rejection and a registry
digest. Manifest registration never grants execution permission.

## Supported execution path

The bound catalog bridge implements **local processes only**. It accepts a
conservative, per-tool target-form allowlist based on packaged argv templates.
It rejects dynamic arguments, unknown adapters, changed executable or argv
definitions, mismatched manifest fingerprints, unsupported target formats and
uninstalled executables. A catalog change creates a new provider version;
previous manifests remain persisted but cannot hijack new execution.

Core authorization resolves the same bound adapter before applying scope,
exact permission and impact checks, and plan-bound approvals. ToolRunner remains
the only execution path, rechecks scope, builds argv, executes, collects output
and persists job evidence. A process returning exit code zero is not independent
verification of a vulnerability. Missing or contradictory execution identity
fails closed.

## Shared inspection

- `whaxon workflow capabilities`: declarative registry manifests.
- `whaxon workflow providers`: live installed/executable readiness.
- `GET /api/v2/capabilities`: same declarations through Core.
- `GET /api/v2/providers`: same live readiness through Core.

Registered, installed, smoke-tested, lab-validated and end-to-end verified are
**different facts**. The inventory intentionally never invents test validation
from mere binary presence. Unsupported remote, browser, cloud and session
transports remain unavailable rather than being simulated.

## Regression acceptance

Cover Python 3.11/3.12/3.13, Ruff, registry persistence, collision-safe version
registration, deterministic compatibility and refusal reasons, target-form
matrix, changed catalog argv, binary removal, direct-provider permission gate,
runner/store identity, existing workflow scope and approval, CLI and API
inventory parity. Keep broader roadmap acceptance gates separate.

## Trusted provider routing and complete catalog reconciliation

Core now binds the scheduler to a `BoundProviderRouter`, not to a concrete
catalog tool provider. Additional implementations can be registered through
`bindings()`, `resolve_task()`, `dispatch()`, and `inventory()` without
changing the scheduler; duplicate capability bindings fail closed. Merely adding
a manifest to persisted state never enables an execution provider. The router
revalidates live binding on dispatch and rejects result identity mismatches.

The provider inventory now includes **all** catalog tools: those admitted
through the trusted local adapter bridge and those excluded because of an
unsupported transport, unapproved tool category, or missing compatible adapter.
Unbound tools remain non-executable even if installed. This is a truthful
portfolio reconciliation, not an assertion that session, exploit, browser, API,
or cloud capabilities have been implemented. Each new execution transport
still requires its own safe adapter, policy and independent acceptance.

## Evidence-driven follow-up proposals

E4 now compiles sealed, identity-checked workflow evidence into a separate immutable, policy-bound follow-up plan. Declarative rules map observations to resolved capabilities without scheduler-specific tool chains. New plans carry evidence references and manifest fingerprints, are scope-filtered, bounded and deduplicated. Neither planning nor saving approves or executes a follow-up. CLI: whaxon workflow plan followups --source-id PLAN [--save]. Legacy autochain remains until parity and cutover acceptance.


## E4 transition safeguard and scope of this batch

Provider contracts are now statically typed, including a live trusted provider
protocol and the complete catalog-only/unsupported inventory. A V2-originated
ToolRunner job is fenced before findings events are emitted so the legacy
Nmap-to-Nikto Automator cannot create an unapproved duplicate follow-up.
The old Automator remains enabled for legacy jobs pending explicit parity
acceptance and retirement. A failed fence blocks dispatch.

**Not accepted as complete E4:** operation-semantic capability IDs, multiple
compatible providers for one operation, complete import/session/RPC
reconciliation and durable end-to-end provider-substitution proof remain open.
The E4 branch has been reconciled with merged PR #97 and #98 on main; Core and CLI durable queue and continuous-worker paths are preserved. An exact-head CI pass and acceptance remain required before merging.


## Explicit future-provider substitution (E4 development batch)

For a shared semantic operation, the trusted `BoundProviderRouter` now accepts `preferred_providers={capability_id: provider_id}`. Multiple in-process adapters may declare compatible operation identities, but there is **no automatic failover** or implicit provider substitution: the explicitly configured provider is required, its bound manifest is checked during resolution, and its identity is rechecked on dispatch. Without an explicit preference, duplicate capability registrations still fail closed. A configured but absent provider also fails closed. This is an extension contract and deterministic selection proof, **not** a claim that every catalog tool already has a semantic capability ID, that all providers are interchangeable, or that persistent approvals already pin the selection across configuration changes. Approval-bound provider identity and full capability normalization remain acceptance gates.


**Durable legacy isolation:** The V2 job-origin marker is stored in JobStore before ToolRunner dispatch, rather than transiently within Automator. Repeated findings events and an Automator restart cannot resurrect the legacy Nmap-to-Nikto chain for a V2-owned job; failed storage reads fail closed. The marker table is transitional and will be retired with legacy autochain after parity acceptance.


**Plan-bound provider identity:** When multiple trusted implementations share a capability, immutable workflow plans must pin the chosen provider ID and manifest fingerprint by task ID under `metadata.provider_bindings`. Authorization rejects missing or changed bindings; switching an installed provider does not silently alter previously approved work. New evidence-derived follow-up plans record their selected provider identity but remain unapproved until separately authorized. Single-provider legacy plans remain compatible.


**Compatibility admission:** Multiple trusted providers declaring one semantic capability must match typed input/output, target/protocol/auth applicability, permission, side-effect, and impact contracts. Incompatible providers fail registration before any dispatch even if explicitly preferred. Different transports and readiness may coexist only when operation semantics match; per-provider real-world equivalence still requires verification.


## Read-only catalog/adapter reconciliation (E4 development)

The `whaxon workflow portfolio-audit` CLI and `GET /api/v2/providers/portfolio-audit` API use the same Core service to classify every current catalog entry together with adapter registrations. Results explicitly identify catalog-only, adapter-only, local bound, unsupported transport, and non-admitted entries. This is **an inventory only**, not a service health or readiness pass. Third-party adapter discovery may already have occurred during normal WHAXON startup, but auditing cannot promote an external adapter to an executable Engine V2 provider. Full platform/transport/entry-point and interface reconciliation remains a separately measured acceptance gate.


## First-class semantic operation aliases (E4 development)

`SemanticOperationProvider` provides stable operation identities for fixed-argv, admitted local tool adapters without changing the legacy provider implementation or scheduler. Both legacy `tool.<id>` and operation-level `network.services.discover`, `web.server.audit`, etc. remain available for migration. The same policy permissions, targets, effects, parser and execution runner apply; output identity is checked against the legacy provider before the semantic identity is surfaced. New semantic plans must pin provider ID and semantic manifest fingerprint, regardless of candidate count. This compatibility layer does **not** imply that arbitrary providers share equivalent results, nor enable unsupported tools or transports. Future alternatives must pass exact contract checks, explicit preferred selection and separate lab/evidence gates.

## E4 provider binding reconciliation (2026-11-03 batch)

The read-only `BoundProviderRouter.operation_reconciliation()` audits every trusted
in-process capability binding at **operation level**, including explicit preferred
provider identity and compatible but **unselected** alternatives. When the
selected provider is missing, it records `preferred_provider_missing` rather
than silently falling back. The provider portfolio audit also carries
`operation_bindings` when an auditable provider exposes a portfolio report,
preserving existing catalog/adapter rows and the legacy empty-audit response.

A row marked `selected` means only that the trusted router has chosen that
in-process implementation. **It does not attest executable readiness, source
authorization, test execution, lab validation or external transport support.**
This inventory never registers or loads a provider, changes plan approvals,
dispatches a tool, or discloses non-selected manifest fingerprints.

The regression batch `tests/test_engine_v2_e4_provider_reconciliation.py` covers
two compatible implementations with explicit selection, missing configured
providers with and without other trusted implementations, the rule requiring
immutable semantic plan provider pins, and unconfigured ambiguity failing closed.
Full E4 catalog/transport/interface parity, provider substitution in a
controlled lab, and retirement of legacy bypasses are still separate gates.

The catalog/adapter portfolio audit also now checks the live catalog argv-version digest and the currently registered manifest fingerprint before calling a provider `bound`. Catalog drift or missing/changed manifest registration is reported `unbound` with `catalog_or_binding_changed`, rather than retaining a stale admission label. This affects inventory reporting only; the dispatch boundary retains its separate runtime revalidation. Regression tests cover both forms of drift.

## Execution selection versus installation readiness

The shared `BoundProviderRouter.inventory()` now decorates each provider inventory
row with `selected_for_execution`. A provider may be registered and installed,
yet **not dispatchable** because a different trusted provider was explicitly
selected for that semantic capability. Such an unselected row preserves the
underlying `installed` status but reports `executable: false` and
`reason: provider_not_selected_for_execution`. This does not mutate the
provider's own inventory record or change approval/scheduling decisions.

A missing preferred provider cannot silently fall back to an installed
alternative. A selected provider with a missing binary remains non-executable.
These claims have synthetic-provider regression coverage and do not certify
external tool readiness, parity or a full E4 acceptance gate.

