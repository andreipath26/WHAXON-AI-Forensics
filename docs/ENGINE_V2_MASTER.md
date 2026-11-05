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
| Plan | Mission, version, canonical digest, graph, planner/source, policy/manifest/readiness snapshots, budgets, validation and approval |
| Task | Capability, provider constraints, typed input/output, dependencies, condition, policy requirements, budgets, timeout, retry/idempotency |
| TaskAttempt | Worker/lease, resolved provider/version, invocation digest, timestamps, outcome, resource usage, evidence refs |
| CapabilityManifest | Capability IDs, schema/version, supported targets/protocols/platforms/auth, typed I/O, prerequisites, execution kind, side effects, permissions, limits, retry/cancel semantics, evidence formats |
| ProviderRegistration | Provider identity/version, manifest/adapter refs, readiness, health, compatibility and reliability |
| PolicyDecision | Allow/deny/approval, reason/rule IDs, evaluated action/target, policy version and validity |
| Approval | Actor, exact digest/scope/parameters/impact/budgets, expiry, decision and revocation |
| BudgetLedger | Allocated/reserved/consumed request, time, concurrency, compute, storage and cost |
| ExecutionContext | Mission/task/attempt, asset, authorization, identity/session, route/pivot, environment, correlation and cancellation |
| Observation | Raw source, normalized type/data, target, provider, time and provenance |
| Finding | Stable identity, affected asset, lifecycle, severity/confidence and observation/evidence links |
| VerificationRun | Finding, independent method, authorization recheck, inputs, outcome, limitations and evidence |
| EvidenceArtifact | Content hash/storage ref, media/type, provenance, redaction, retention, access and integrity |
| AuditEvent | Actor/action/decision, causation/correlation, timestamp, canonical digest and integrity link |
| ReadinessSnapshot | Environment, provider/adapter versions, dependency and functional checks, status and capability consequences |

### 4.1 Manifest semantics
Manifests declare stable capabilities; provider and adapter versions; supported asset/target types, protocols, platforms, auth and transport; input/output schemas; preconditions and dependencies; execution kind; permissions and side effects/impact class; passive/active/intrusive/destructive/state-changing/external-cost classification; resource/rate/concurrency limits; timeout/cancellation; idempotency/reconciliation; raw evidence and parser versions; limitations; and readiness/verification level. A manifest describes capability; it never grants permission. Unknown properties remain unknown, not guessed.

### 4.2 Task states and outcomes
Model guarded transitions such as proposed → validated → awaiting approval → ready → queued → leased → running → collecting → verifying → terminal. Terminal outcomes distinguish succeeded, failed, partial, cancelled, blocked, skipped, inconclusive, expired and unknown. Process exit code zero is not sufficient for semantic success. Parser failure is explicit and raw output is retained. Retries create new attempts and never erase history.

## 5. End-to-end execution protocol

1. Receive objective and explicit engagement/programme context.
2. Resolve authorization and capability/readiness snapshots.
3. Gather permitted asset, session, route, finding and evidence context.
4. Planner proposes typed tasks and dependencies.
5. Compiler validates graph, schemas, provider compatibility, boundedness, safety classification and budgets; canonicalizes and digests the plan.
6. Correct policy engine evaluates every consequential task; required approval is obtained against exact digest.
7. Persist plan, decisions, budgets and audit before dispatch.
8. Scheduler dispatches eligible tasks under leases and limits.
9. Worker rechecks authorization immediately before effect, executes via typed adapter and persists progress/outcome/raw evidence.
10. Normalizers create observations/findings retaining source provenance.
11. Independent validators/retest tasks run when appropriate and permitted.
12. Coverage ledger compares planned, approved, attempted, completed, verified, inconclusive, blocked, skipped and untested work.
13. Planner may propose a new version from evidence; compiler/policy/approval run again.
14. Pause/stop on objective completion, budget exhaustion, expiry, policy uncertainty/change, circuit breaker, approval requirement or user request.
15. Produce auditable result and recovery state.

## 6. Future capability requirements

The core must support extension seams for:
- Existing and future scanners, recon, web/API/network/identity tools and alternative providers.
- Passive intelligence, asset discovery, normalization and enrichment.
- Validation, evidence fusion, reproduction, retest and remediation verification.
- Session-aware commands, SSH/SMB/WMI, Metasploit, reachability and route/pivot-aware work.
- Customer pentests and independent bug-bounty campaigns/programmes.
- Multi-target lists, bounded CIDR fan-out, target isolation and aggregated reporting.
- Cloud, code, container, SBOM, Kubernetes and provider SDK operations.
- Browser automation and third-party APIs through explicit execution contracts.
- Manual/guided/supervised/autonomous modes, human/delegated approvals and team ownership.
- Future Fact-Intent Graph, RAG and multi-agent planning as consumers/proposers—not alternate execution or authorization paths.
- PTaaS lifecycle, client delivery, compliance mapping, integrations, threat intelligence, monitoring and training.
- Offline/air-gapped, on-prem, local-only and headless server deployments.
- Future queue/storage/worker scaling without binding domain logic to one vendor.

These are extension requirements, not permission to implement every future feature now. Follow roadmap gates and prioritize measured need.

## 7. Security and trust model

Treat prompts, imported programme pages, target responses, files, manifests, API responses and tool output as untrusted. Threat model includes prompt injection, SSRF, DNS rebinding, redirect escape, scope confusion, alternate host/IP forms, argv/path injection, credential leakage, approval forgery, race conditions, cross-campaign leakage and adapter bypasses.

Validate DNS/IP/redirect destinations at the actual network boundary and record resolution/decision evidence. Use least-privilege worker identities and secret references, not secret values. Redact logs and protect evidence. Enforce isolation in service/data access, not only UI. Define safe behavior for DB/queue/worker/audit/evidence/event-store failures. Emergency stop blocks new work immediately, cancels active work where supported, checkpoints safe state and reports uncertain external effects. Never claim success when required evidence/audit is missing.

## 8. Migration strategy

1. **Inventory:** map every invocation path through runner, Automator, worker, event bus, store, catalog/registry, adapters, AI executor, sessions, validators, CLI, web and reports. Record all scope checks, state transitions, tests and deployment wiring.
2. **Correctness first:** close follow-up-job draining, Nikto parsing, scope and evidence-chain defects with regression and end-to-end tests.
3. **Compatibility façade:** route existing CLI/web call sites through shared application services; preserve supported public behavior and report contracts.
4. **Manifest bridge:** derive truthful manifests for existing catalog/adapters; mark unknown metadata explicitly; add schema/compatibility tests; retain working parsers.
5. **Durable task graph:** add mission/plan/task/attempt state, scheduler, leases, outbox, budgets, cancellation, idempotency and recovery. Start with parity for existing sequential workflows, then safe parallel/conditional execution.
6. **Automator migration:** replace hard-coded Nmap→Nikto ownership with declarative evidence/capability follow-up policies. Follow-ups are durable, deduplicated, reauthorized at dispatch, bounded and visible to initiating client.
7. **AI integration:** adapt typed Action proposals to plan/task proposals. No raw command, policy mutation, self-approval or bypass. Retain provider independence and offline/manual behavior.
8. **Transport expansion:** add session, API, browser and cloud execution kinds only with their own security, lifecycle and integration tests.
9. **Cutover:** retire old paths only after parity, migration, rollback, security and no-bypass evidence. No big-bang rewrite.

## 9. Complete roadmap crosswalk

This table maps roadmap requirements to architecture ownership. It is not a completion claim and does not override §0 ordering.

| Roadmap sections / themes | Engine response and required seam |
|---|---|
| §0 and foundational principles | Dependency-first gates, deterministic execution, consent, bounded work, verification, provenance and recovery |
| §§1–6, §§13–15 | Preserve completed foundations and explicit exclusions; inventory existing behavior before changing it |
| §7 tool adoption | Capability manifests, registry/resolver, adapter contract, readiness, provider substitution and adapter acceptance |
| §§8–9 portability/cloud | Typed execution kinds, platform compatibility, readiness and truthful unsupported/degraded states |
| §10 AI modes | Planner/proposer separation, four interaction modes, deterministic plan compiler and policy |
| §§11–12 historical schedule | Historical plans subordinate to §0; no competing sequence |
| §16 integrations/MCP references | Optional provider/integration contracts; no integration becomes permission authority or mandatory runtime dependency |
| §§17–18 team/company | Actor, tenant, organization and delegated approvals; isolated engagements, shared audit and service boundary; implement only at gate |
| §§19, 41, 44, 48.5 UI | Versioned services/API, durable progress/reconnect, readiness/programme contracts; supplied UI remains exact design, unsupported controls hidden |
| §20 market/platform coverage | Extension seams for PTaaS, remediation, ASM, compliance, collaboration, threat intel, training, cloud posture, APIs, i18n, air-gap and mobile |
| §§21, 25 reporting | Stable finding/report contracts, asset-specific evidence, provenance, severity and honest verification/coverage |
| §§22, 24 historical triage | Historical context informs tests/requirements but is not live execution state |
| §23 agentic blind spots | Stateful graph, session/reachability context, safety gates and evidence-backed transitions |
| §26 bounty foundation | Independent bounty policy domain, source-backed programme rules, versioning, inert import until activation, approvals |
| §§32–34 solo v1.0 and Trust Layer | Engagement execution, validation/reproduction, coverage ledger, retest, independent validators, payload provenance and integrated acceptance |
| §35 portfolio R&D | Stable external integration seams; defer broad cross-project coupling until core products stable |
| §36 recon pipeline | Passive/active task classes, discovery provenance, asset normalization and bounded enrichment |
| §37 strategic pivots | Fact-Intent Graph, governance, hints, proof-driven remediation and multi-agent consumers use stable task/evidence APIs |
| §38 release blockers | Integrated regression, security, compatibility, acceptance evidence and known-risk reporting |
| §39 tool portfolio | Capability-first tool adoption across recon/cloud/code/container/API/session categories and impact tiers |
| §40 dependency readiness | Readiness snapshots, dependency probes, install lifecycle integration and capability activation only after verification |
| §42 multi-target/subnet | Per-target policy, bounded graph fan-out, concurrency/rate controls, failure isolation, partial aggregation and cancellation |
| §43 competitive parity | Benchmarkable events, coverage/verification metrics, seeded-lab repeatability and evidence-backed claims |
| §44 UI-first gate | Engine architecture may be specified; runtime expansion remains subject to §0/§44 sequencing and UI gate |
| §45 bounty intelligence | Independent programme/asset graph, autonomous investigation graph, evidence vault, prioritization, monitoring, learning and approval-gated disclosure |
| §46 autonomous campaigns | Four modes, shared campaign controller, isolated customer/bounty policy, durable recovery, stateful chains and transport/session validation |
| §47 installation/readiness | Environment/readiness service, consent-bound installation tasks, bounded cancellation, post-install verification and recovery |
| §48 capability/headless/deployment | Machine-readable capability inventory, shared clients, durable workers, health/readiness, systemd/container acceptance and integrated deployment tests |

## 10. Delivery gates (subordinate to §0)

- **E0 Baseline:** execution-path, state-transition, data-contract, permission-boundary, test and deployment inventory. Exit only when unknowns are explicit.
- **E1 Correctness/security:** follow-up draining, Nikto parser, scope, target identity, idempotency and evidence regressions closed.
- **E2 Contracts:** versioned manifest/task/outcome/policy/approval/event/evidence contracts and compatibility façade.
- **E3 Durability:** mission/plan/task/attempt persistence, scheduler, leases, budgets, outbox, cancellation, retry reconciliation and crash recovery.
- **E4 Capability migration:** current adapters registered truthfully; evidence-driven follow-up; new provider added without scheduler changes.
- **E5 Shared/headless:** CLI/API/web use shared services; readiness; verified daemon/systemd/container; jobs survive client disconnect/restart.
- **E6 Solo v1.0/UI:** supplied UI integrated without redesign; real backend contracts; end-to-end acceptance and release gates pass.
- **E7 Autonomy/bounty:** customer and bounty campaigns independently authorized; supervised autonomy, pause/stop/recovery and adversarial isolation tests.
- **E8 Multi-target/measurement:** bounded target fan-out, aggregation and seeded competitive measurement after §0/§44 gates.
- **E9 Selective expansion:** cloud/code/container/API/team/enterprise/graph integrations only when justified and individually accepted.

## 11. Verification and acceptance matrix

- **Contracts/registry:** schema and version compatibility, deterministic provider choice, ambiguous/missing provider, malicious metadata and readiness drift.
- **Graph:** invalid references, cycles/unbounded loops, dependency/conditional paths, fan-out bounds and stable canonical digest.
- **Authorization:** customer/bounty isolation; target, DNS, redirect, pivot, child process and replay boundaries; stale/expired/ambiguous policy; mid-run policy changes; fail-closed.
- **Approval:** digest/parameter mismatch, replay, expiry, revocation, actor forgery, races and manifest/policy invalidation.
- **Scheduler:** worker crash, lease expiry, duplicate delivery, idempotency, retry cap, fairness, resource limits and queue outage.
- **Recovery/cancellation:** client disconnect, process restart, graceful shutdown, emergency stop, partial output and uncertain side effect without unsafe replay.
- **Adapters:** argv injection, target injection, timeout, cancellation, cleanup, transport loss, parser error, truncated output and raw artifact retention.
- **Evidence/audit:** hash verification, missing events, store outage, corruption, redaction, access isolation and provenance continuity.
- **Verification/coverage:** seeded vulnerable and clean targets, false positive/negative measurement, inconclusive/blocked/skipped accounting and reauthorized replay.
- **Isolation:** engagements, bounty programmes, organizations/tenants, credentials, sessions, findings and evidence.
- **Headless/platform:** no browser/TUI dependency, restart, persistent storage, service/container lifecycle and backup/restore.
- **Compatibility:** CLI/API/report behavior, adapters, supported Python/OS matrix and full regression.
- **Adversarial:** prompt injection, SSRF, DNS rebinding, redirects, scope confusion, approval forgery, race, allowlist bypass and frontend manipulation.

Zero unauthorized/out-of-scope actions is a release blocker. Track coverage, precision/recall, evidence reproduction, cancellation latency, recovery, resource use and setup friction against seeded ground truth.

## 12. Non-goals and decisions requiring evidence

Do not big-bang rewrite adapters/parsers/reports; hard-code tool chains; allow arbitrary model shell or self-approval; merge customer and bounty policy; keep campaign state in memory; assume exactly-once effects; dynamically execute untrusted manifests; build a universal workflow language without demonstrated need; prematurely require microservices or a distributed queue; implement every future roadmap feature in the foundation; or use legacy UI/TUI as a substitute for approved UI/headless requirements.

At E0, record evidence-backed decisions on: persistence transaction/lease/outbox capabilities; exact Python module boundaries; whether a separate queue is justified; event cursor semantics; evidence blob storage/encryption; tenant/organization isolation; deterministic provider tie-breaks; migration compatibility window/rollback; and platform/transport support. Each decision records options, evidence, risks and migration impact.

## 13. Architecture readiness and Engine v2 definition of done

Architecture is implementation-ready when current paths and permission boundaries are inventoried; contracts/state machines are versioned; customer/bounty isolation is testable; manifests and typed transports cover current and future provider classes; scheduler/recovery semantics are specified; evidence/verification/coverage/audit are end-to-end defined; clients share services; roadmap crosswalk and §0 gates are reconciled; threat model, migration, rollback and acceptance tests are reviewed.

Engine v2 is done only when it executes a versioned, policy-checked, capability-resolved task graph across supported transports; persists and recovers safely; preserves and independently verifies evidence; exposes truthful progress/coverage through shared clients; and passes security, compatibility and operational acceptance. Future capabilities must be addable through provider/contracts without rewriting mission, policy, scheduler or evidence foundations.


---

## Metasploit and Armitage — complete capability integration

The Metasploit integration is a first-class Engine v2 provider and a substantial product capability, not a narrow adapter. The complete architecture, Framework coverage, Armitage patterns, security requirements, implementation gates and acceptance matrix are specified in `docs/METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md`.

Architecture decisions:
- Metasploit Framework is a dynamically discovered execution provider; WHAXON remains mission, policy, scheduler, evidence and verification authority.
- Discover the connected Framework's real version and RPC/API surface. Do not hard-code module totals or assume identical APIs across versions/editions.
- Cover module intelligence and all supported module families, structured jobs/consoles, payloads/handlers, shell and Meterpreter sessions, Framework database/loot, plugins and route/pivot lifecycle.
- Adopt Armitage's attack-surface/session graph, Find Attacks recommendations, contextual session workflows, pivot awareness and future deconfliction concepts. Do not clone its UI or make it a runtime dependency.
- Build explainable, evidence-backed module recommendations and independent vulnerability verification; module matches and module checks are not proof by themselves.
- AI proposals become typed tasks and pass deterministic authorization, policy, approval, budget and runtime checks. Replace fixed MSF auto-chain behavior with independently authorized declarative transitions.
- Support headless execution and truthful optional-dependency/readiness reporting.
- Follow Engine v2 E1–E9 sequencing; E1 security/recovery blockers precede broad capability expansion; E6 retains supplied UI design and visibility gates.



---

## Tool Intelligence & controlled onboarding

Tool Intelligence is a first-class Engine v2 subsystem, not a second capability registry. It provides a source-backed lifecycle for auditing current tools and researching candidates. Its detailed requirements and acceptance gates are in roadmap §52 and docs/TOOL_INTELLIGENCE_AND_ONBOARDING.md.

Two entry points—current portfolio audit and new candidate research—share one pipeline: discovery, source research, capability extraction, normalization, gap/overlap analysis, compatibility/risk assessment, proposal, operator decision, integration and validation. The durable output is a versioned Tool Capability Report.

Reports separate (1) upstream claims/support, (2) WHAXON implementation, (3) WHAXON verification in a named environment/version and (4) current permission to execute. These states must never be collapsed.

Extend the existing Engine v2 CapabilityManifest, registry/provider resolver and readiness contracts. Do not create a parallel schema. Contracts must cover provider identity/version, stable capability IDs, typed schemas, interface/transport, target/platform/auth compatibility, prerequisites and secret references, pre/postconditions, side effects/impact, execution limits, cancellation/idempotency/reconciliation, evidence/parser provenance, capability-specific readiness and source confidence/version/retrieval metadata.

CycloneDX/SBOM, OpenAPI, JSON Schema, MCP discovery and Python entry-point metadata are complementary extraction/provenance sources. They do not replace WHAXON policy. External descriptions, annotations and manifests are untrusted.

Discovery is read-only and bounded by default: inspect local catalog/registry/entry points, executable version/help and documented capability listings; research official docs/source/releases/advisories/licensing. Never run scans, exploits, listeners, post-exploitation, arbitrary RPC, downloaded code or candidate operational functionality during discovery. Never auto-install, upgrade, enable or load plugins. Each consequential validation/install/credential/network action requires separate explicit approval and deterministic policy authorization.

Persist onboarding states: proposed → researched → assessed → approved_for_implementation → integrated → validated → enabled, with rejected/deprecated paths. Record actor, time, report version, decision and evidence. Implementation approval is not installation or execution approval. Version/security changes trigger reassessment and can invalidate readiness.

Dependency mapping:
- E1: no bypass of correctness/security blockers.
- E2: define manifest, provenance, readiness, report and lifecycle contracts in common domain model.
- E3: persist lifecycle/report events and schedule monitoring only on durable scheduler semantics.
- E4: reconcile catalog/adapters/transports, migrate manifests, local discovery, extraction, gap analysis and deterministic provider compatibility.
- E4/E5: source-backed candidate research and operator-reviewed onboarding after contracts stabilize.
- After registry/readiness stabilize: upstream delta monitoring and revalidation.
- E6+: expose only implemented, verified, authorized capabilities through shared services and supplied UI.

Logical modules may include local discovery, source research, documentation ingestion, capability extraction, normalization, gap analysis, compatibility, risk assessment, onboarding workflow and report persistence. They must reuse shared contracts and must not create a second scheduler, policy engine or registry.

Acceptance includes full portfolio reconciliation; safe local discovery; reproducible source-backed reports; explicit upstream/implementation/test/authorization separation; malicious metadata/schema handling; no automatic installation/execution; auditable/revocable lifecycle; upstream drift reports without runtime changes; and provider extensibility without changing mission/scheduler/evidence core.


## Implementation record — 2026-11-01

The first implementation slice is on main:

- E1: worker leases carry owner/token/heartbeat; stale recovery uses heartbeat age; Metasploit session dispatch requires persisted session identity and scope revalidation; TLS verification is enabled by default and the weak default RPC password is removed. CI acceptance remains pending.
- E2 foundation: versioned WorkflowTask and immutable WorkflowPlan contracts validate DAGs and produce a content digest. ApprovalBinding ties consent to the exact plan, task, target, inputs, permissions, impact, policy version and expiry. SQLite persists missions, plans, tasks and attempts transactionally.
- E3 foundation: WorkflowScheduler atomically claims dependency-ready tasks, bounds retries, requires an explicit authorization callback and marks timeouts uncertain rather than replaying potentially side-effecting work.
- This 2026-11-01 snapshot is historical and is superseded by the 2026-11-02 implementation update below. The scheduler/provider bridge and shared Core integration have since landed; release acceptance remains open.


## Implementation update — 2026-11-01 (supersedes the earlier E2/E3-only status)

The following Engine v2 work is now implemented on `main`; release acceptance is still open:

- **E2 contracts/persistence:** versioned WorkflowTask/WorkflowPlan contracts, immutable nested JSON values, deterministic plan digests, exact ApprovalBinding, durable mission/plan/task/attempt storage, immutable versioned capability manifests, and plan-local task identifiers.
- **E3 scheduler/recovery:** atomic dependency-ready claims, bounded retries, explicit fail-closed authorization, synchronous and asynchronous provider deadlines, stale-attempt fencing, cancellation/timeout uncertainty, interrupted-worker reconciliation, and legacy attempt recovery. Unknown outcomes are not automatically replayed.
- **E4 first integration slice:** catalog-backed adapter providers are registered through the common capability registry. An allowlist of read-only scanner adapters dispatches through the existing ToolRunner, preserving existing scope checks, process isolation, adapter parsing, events and evidence persistence. Credential attacks, exploit frameworks, command execution and session transports are intentionally excluded pending dedicated policy/approval contracts.
- **Shared Core:** Core now exposes mission/plan/scheduler services and a default fail-closed policy that requires an exact manifest permission/impact match and an in-scope target. The scheduler can use the real catalog provider bridge without a caller-supplied dispatch callback.
- **Headless:** the CI headless Linux server smoke passed on the provider-integration build. Full Python-version regression and static checks remain under CI verification; do not mark the release green until the latest run is complete.

### Still required before v2 deployment

1. Complete E1 security acceptance and regression testing, including scope/DNS/pivot edge cases and worker ownership races.
2. Complete E3 production guarantees: durable cancellation semantics, execution budgets/concurrency limits, audit/outbox guarantees, and reconciliation interfaces for uncertain external effects.
3. Complete E4 portfolio reconciliation and truthful capability/readiness extraction; add supported session/Metasploit/API transports only behind their own policy and tests.
4. Complete E5 shared CLI/API/headless application lifecycle and expose durable progress, coverage, evidence and verification state.
5. Complete E6 supplied-UI integration without redesign or placeholder capabilities.
6. Run full cross-version tests, static analysis, packaging/install/upgrade tests, restart/recovery tests and controlled-target end-to-end acceptance. Deployment is blocked until all required jobs pass.

### Current execution example

The first provider-backed task uses a capability such as `tool.nmap`, with `permissions=("network.scan",)`, `impact="moderate"`, an explicitly in-scope target and empty `inputs`. Dynamic CLI arguments are deliberately rejected by this initial provider bridge. The provider invokes the existing ToolRunner; it does not construct shell commands or bypass scope enforcement.


### 2026-11-02 scheduler deadline correction

A task's declared timeout now covers both deterministic authorization and provider dispatch. Synchronous callbacks execute in worker threads rather than blocking the event loop, preserving lease heartbeats and independent task progress. Authorization timeout fails closed as `blocked` and never dispatches; provider timeout remains `uncertain` because cancelling an await or timing out a worker thread cannot prove that an external effect stopped. Regression tests cover synchronous and asynchronous authorization timeouts. This closes a scheduler correctness gap, not the remaining mission-wide budget, cancellation, audit/outbox or recovery acceptance gates.
---

## 14. Whole-engine roadmap implementation plan — 2026-11-03

**Scope and decision:** This section consolidates the approved full-engine direction across E0–E9, not just E4. **E0, E1, E2 and E3 are UNFROZEN**, as are E4–E9. Their implementation, contracts, scheduling, persistence, policy and other foundations may be repaired or refactored when necessary for the integrated architecture. Reuse correct, tested code; do not rebuild simply because a phase is open. No phase is considered accepted merely because its code or tests exist.

**Priority and source order:** (1) the CURRENT master roadmap \`WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md\`, especially §0, P0–P8, §38, §49–50; (2) this architecture specification and its E0–E9 gates; (3) \`docs/ENGINEERING_EXECUTION_MODEL.md\`; (4) scoped designs such as \`docs/TOOL_INTELLIGENCE_AND_ONBOARDING.md\`, \`docs/METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md\`, \`docs/bounty-addon.md\` and the remediation addendum. Older roadmap detail is retained only where not superseded by the current master; historical estimates, completion claims, tool quotas and conflicting implementation instructions are not current authority.

**Architectural objective:** Deliver WHAXON's **single long-lived, capability-driven, policy-controlled, durable execution engine**. New tools, providers, transport implementations, automation modes and approved product features must normally attach through versioned extension contracts, without new scheduler branches, alternative permission authorities, independent evidence stores or client-owned execution engines. “Build once” means stable and migratable boundaries, not a guarantee that unspecified future requirements can never change a contract or a requirement to ship every future provider today.

### 14.1 Phase-to-roadmap ownership and action

| Engine phase | Current master roadmap responsibility | Foundation or product work required | Acceptance boundary |
|---|---|---|---|
| **E0 — Baseline and architectural decisions** | P0; §0; §49; G01/G10 | Keep a current exhaustive execution/caller/adapter/tool/transport/permission/data/dependency map; record schema, queue, storage, audit, trust-anchor, provider-selection and cutover decisions. Correct stale assumptions when implementation changes. | Exact source-to-feature inventory, migration dependency graph and reviewed decisions; old E0 snapshot is historical. |
| **E1 — Correctness and security** | P1; §0 invariants; G02–G04 | Complete fail-closed scope/DNS/redirect/session/pivot/replay/follow-up checks; exact action/consent, startup no-unrelated-dispatch, cancellation boundaries, parser/evidence integrity and adversarial coverage. Preserve existing corrections. | Controlled negative/positive authorization, evidence and recovery tests; no unauthorized effect; explicit limitations for external tool networking. |
| **E2 — Versioned domain contracts** | P2; §49; G01/G05 | Complete and version canonical mission, authorization, plan/task/attempt, manifest/provider, policy/approval, budget/context, observation/finding/verification, evidence/audit/readiness contracts; migrations and compatibility façades. | Schema/version/backward compatibility, immutable digests, explicit unsupported results, no implicit authorizations. |
| **E3 — Durable operations** | P2; G02/G04/G05 | Finish mission-wide rate/time/request/resource/cost/concurrency limits, leases, cancellation/emergency stop, retry/reconciliation, outbox/audit integrity and failures, crash/restart safety and bounded work. Adapt existing scheduler/store rather than introducing a second one. | Real worker crash, duplicate delivery, lease loss, cancellation, queue/store/audit failures and recovery without unsafe replay. |
| **E4 — Capability migration** | P0/P2, §49–50; tool-intelligence portfolio audit; G01/G02 | Reconcile every existing catalog, adapter, entry point, local/session/RPC transport, parser, runner dispatch path and advertised UI/API/CLI capability; stable operation-level capability IDs independent of product/tool names; provider-neutral deterministic routing; capability-specific readiness; evidence-driven follow-up and no hard-coded chains; demonstrate another compatible provider without modifying scheduler. | Complete mismatch/unsupported inventory; truthful authorization/readiness; provider substitution and bounded follow-up equivalence; no legacy bypass. |
| **E5 — Shared services and headless** | P2/P3; G05/G07 | One mission/approval/run/progress/evidence/verification service for CLI, API, supplied web UI and headless; durable execution ownership and process restart behavior; health/readiness, deployment/secrets, installation state and client reconnect. | Client disconnect/server crash does not lose accepted work; supported daemon/systemd/container, backup/restore and clean-install acceptance. |
| **E6 — Solo v1.0 and supplied UI** | P4/P5; §38 G01–G10 | Integrate supplied design with **zero redesign**, preserve distinct source variants, wire visible controls to real service contracts, report blocked/untested accurately; prove authorized scope→recon→enumeration→supported initial access→verification→evidence/report→retest. | Visual/accessibility/API parity, controlled seeded lab, truthful evidence/report/export, packaging and exact-candidate release decision. |
| **E7 — Independent bounty and bounded autonomy** | P6; G02/G04/G05 | Separate programme/engagement policy and state; provenanced source ingestion, review/activation, envelope-aware manual/guided/supervised/autonomous campaigns, stop/reapproval and verified follow-ups. | Customer/bounty isolation, no scope expansion by inference, bounded operation and adverse-input tests; never self-approval. |
| **E8 — Multi-target and measurement** | P7; §38 applicable gates | Canonical URL/domain/IP/CIDR/mixed assets, scoped bounded fan-out/fan-in, per-target policy and quotas, isolated failures, aggregation, reachability/pivot constraints; reproducible seeded comparative measurement. | Cancellation/recovery/partial coverage per asset and sourced benchmark with known-ground-truth limitations. |
| **E9 — Selective advanced expansion** | P8; §50 retained §§20, 35–37, 39, 45–52 | Add only justified Metasploit/Armitage breadth, new scanner/API/browser/cloud/code/container/Kubernetes/SBOM providers, remediation, graph/retrieval, monitoring, team/PTaaS/enterprise integrations through existing contracts. | Per-provider requirements, license, compatibility, risk, trust, cost, isolation, lifecycle, tests and specific product gate; deferred features do not block solo v1.0. |

**Phase ordering:** Master roadmap P0–P5, §0 dependency and §38 release gates remain binding; P6–P8 are gated expansions. Unfreezing E0–E3 permits necessary foundation repair, **not** bypass of those dependencies. Work may run in parallel only with stable contracts, bounded ownership, explicit integration order and independent verification. Do not report approximate percentages as accepted coverage.

### 14.2 Permanent engine ownership and boundaries

One authority owns each concern. The intended dependency path is:

\`\`\`text
CLI / API / supplied UI / headless / optional integrations
                    |
          Versioned application services
                    |
Mission/engagement/programme + campaign objective/mode/budgets
                    |
Typed plan compiler -> deterministic policy -> exact approval
                    |
          Durable task graph and scheduler
                    |
   Versioned capability resolver + trusted provider bindings
                    |
    Explicit typed execution adapters and bounded workers
                    |
Raw artifacts -> normalized observations -> independent verification
                    |
  Coverage / audit / recovery / report / operator progress
\`\`\`

- **Planning:** support typed input/output, DAG dependencies, conditional branches, bounded loops, fan-out/fan-in/joins, human gates, validated constraints, plan digests and versioned replanning. No model or UI can bypass the compiler.
- **Security:** distinct customer and bounty policy engines; target/identity/route/session/redirect/scope revalidation at the actual effect boundary; consent bound to actor, plan/task, parameters, impact, budgets, manifest/policy versions and expiry. All new transports reapply it.
- **Durable runtime:** persistent task/attempt/lease/approval/budget/checkpoint/stop/event/evidence state; fenced ownership, no unsafe retry of unknown effects, explicit outcomes, bounded concurrency/time/requests/storage/cost and audit failure semantics. Queue and database changes must preserve transaction boundaries and recovery semantics.
- **Evidence:** raw output and source identity, parser/normalizer version, asset, timestamps, hash/provenance, redaction/retention and independent verification. Neither exit code 0 nor tool/AI confidence is proof of a finding.
- **Service clients:** no browser request, desktop process, TUI or model session owns long-running execution, permissions or authoritative result state; clients can disconnect, reconnect and inspect recovery honestly.
- **Forward compatibility:** schema-version all durable and provider-facing contracts, define deprecation/migration rules and feature negotiation, and test that new compatible providers do not require mission/scheduler/evidence-core modifications.

### 14.3 Tool- and provider-independent capability model

Do not equate \`tool.nmap\`, \`tool.nikto\` or another executable name with a permanent semantic operation. Maintain migration aliases where necessary, but canonical capability IDs describe an **operation and its semantics**; different providers may implement that operation with compatible typed schemas and evidence guarantees. Compatibility must be demonstrated rather than assumed: overlapping tools are not automatically interchangeable.

The **single canonical CapabilityManifest/ProviderRegistration model** must be able to represent:

1. Stable capability/operation ID; provider, tool and upstream identity/version/edition; module or sub-operation identity when relevant; provenance and deprecation.
2. Typed input, output, pre/postconditions and schema versions; target, protocol, platform, architecture, identity, authentication and session applicability.
3. Explicit execution kind (local argv, session/transport, HTTP/API, browser, cloud SDK, local analysis) with its own boundary-specific credential, network, cancellation, cleanup, timeout and evidence contract.
4. Prerequisites, dependencies, environment, platform/installation checks, secret **references**, privilege, supported versions and optional features.
5. Permissions, side effects, impact and risk, rate/concurrency/compute/storage/cost limits, idempotency, retry and reconciliation semantics.
6. Raw evidence formats, parser/normalizer versions, provenance, verification methods, limitations and known blind spots.
7. Capability-specific readiness at a named environment/version: discovered/researched/installed/registered/smoke-tested/lab-validated/end-to-end-verified/degraded/stale/unsupported, with timestamps and linked proof. Do not collapse these into a single \`available\` Boolean.
8. Resolution trace explaining compatible candidates, rejections, tie-break and policy restrictions; pin provider identity/manifest digest to an approved task and revalidate before execution.

**Registration never grants execution authority.** Persisted or imported metadata cannot become an executable provider merely by claiming a safe label. Loading external plugins, remote MCP descriptions or downloaded candidate code is not automatic discovery.

### 14.4 Complete current-portfolio reconciliation and future-tool admission

**E4/P0/P2 migration prerequisite:** reconcile packaged catalog, internal/entry-point adapters, parsers, local runner, legacy Automator, sequential AI executor, worker, session/SSH/SMB/WMI paths, Metasploit RPC, existing passive recon, validators, CLI/API/UI exposure, dependency checks, platform limitations, audit/evidence and tests. Identify all catalog-only, adapter-only, import-only, duplicate, stale, unavailable, unregistered, unreachable-dispatch, partially supported, supported-but-untested and intentionally excluded cases. A catalog listing is not proof of supported capability.

**Future tool pipeline** (P8 implementation only after prerequisites): discover -> source-backed research -> extract capabilities -> normalize into existing manifest -> compare gaps/overlap -> assess license/version/maintenance/platform/security/credentials/cost -> operator decision -> implement adapter -> independently validate -> enable with separate runtime policy. Versioned Tool Capability Reports preserve upstream claims, WHAXON implemented behavior, environment-specific test/readiness, and current authorization as four **separate** states. Reassess upstream drift; never silently upgrade, install, load a plugin, broaden scope or activate an operation.

The provider seam must support at least one independently authored second provider for an already supported semantic capability and prove deterministic selection/explicit rejection under missing readiness, incompatible schema, version, target, platform or policy. Generic provider fallback is not permitted to lower safety requirements or change test meaning.

### 14.5 Future product compatibility without premature implementation

| Roadmap direction | Shared contract to support from the foundation | Feature delivery rule |
|---|---|---|
| New scanners, recon and passive intelligence | Operation-level capability, bounded discovery, parser/provenance, readiness | Add approved providers under E4/P8 admission; no fixed tool count. |
| Metasploit / Armitage / shells / Meterpreter / pivots | Dynamic Framework/version/module/option discovery; typed job/console/session/handler/route/loot operations; identity/approval/evidence and reconciliation | Follow detailed Metasploit design and lab gates; do not hard-code module totals or self-authorize exploit/post work. |
| Authenticated APIs / browser workflows | Explicit auth/identity/session/reference, redirect/DNS/network boundaries, versioned I/O, recording, cancellation | Each transport needs its own approved adapter and lifecycle/evidence tests. |
| Cloud / containers / code / SBOM / Kubernetes | Account/project/region/cluster/resource identity, role/privilege, secret refs, cost and inventory provenance | Typed SDK/source-analysis providers under P8, not general CLI-string escape hatches. |
| Bug bounty and autonomy | Independent activated programme policy, bounded consent envelope, human gates, plan versioning, stop/recovery | P6/E7 only after foundation and isolation acceptance. |
| Multi-target / subnet work | Canonical assets, scope proofs, bounded graph fan-out/joins, per-asset budgets, aggregation and partial outcomes | P7/E8 after supplied UI and solo gates. |
| Remediation and retest | Finding/evidence identity, reviewable patch/action, isolated validation, separate application approval, rollback and original-test replay | P8; current dependency remediation planner is not the full vulnerability patch workflow. |
| Team/enterprise/PTaaS/MCP/graph/RAG/multi-agent | Tenant/actor/role, immutable audit, services and proposal interfaces; integration never creates policy authority | Defer broad features until approved need and specific acceptance; no cross-project product dependency. |
| Offline/on-prem/headless/deployment scaling | Local-first optional dependencies, durable service, storage/queue adapters, secrets, health, upgrades/backup | Verify advertised platform/deployment combinations; no unjustified microservice dependency. |

Preserve approved exclusions (§4); the repository name alone does not authorize digital forensics, malware, wireless, social engineering, mobile app testing or unrestricted post-exploitation work.

### 14.6 Legacy cutover policy

The intended destination is **one Engine V2**. Preserve legacy ToolRunner/parsers/store compatibility, Automator, old workers, AI executor and legacy interface designs only until all affected consumers, state and workflows have verified replacement paths. Avoid dual ownership while migrating: V2-originating observations must not silently trigger an extra legacy follow-up, and legacy authorization must not bypass V2 plan approval when V2 owns the workflow.

Before retiring an old runtime path require: complete caller and persisted-record inventory; parity of supported operations and outputs; scope/approval/credential/pivot checks; migration/rollback strategy; no bypass or duplicate effects; controlled restart/cancellation/evidence tests; then deliberate removal. **Do not remove legacy code merely because a router exists.** Preserve supplied UI designs exactly; old UI reference source is not an implementation target.

### 14.7 Delivery and verification order

1. **Reconcile E0/P0 and unblock E1 correctness** as needed against the current main baseline; scope changes narrowly and preserve fixed behavior. All phases are editable.
2. **Stabilize E2 contracts and E3 durability** required for later transport, service and operational guarantees; close actual gaps, not historical defects that are already fixed.
3. **Complete E4 as an integrated capability migration**, including stable semantic capabilities, full portfolio reconciliation, trusted provider routing, truthful readiness, provider addition without scheduler changes and independently authorized evidence-driven follow-ups.
4. **Complete E5 shared durable lifecycle**, eliminating process-local execution ownership; verify service clients and headless/container/service restart and reconciliation on an exact revision.
5. **Complete E6/P4/P5 and §38 G01–G10**, using supplied UI without redesign and a reproducible controlled-lab solo workflow with honest report and validation results.
6. **Activate E7, E8 and E9 only at P6–P8 gates**, using the same authority, capability, audit and evidence boundaries. Treat all major transport/product additions as independently accepted extensions.

Record each work item with roadmap section, architecture owner, affected source paths, consumer/dependency, exact implementation acceptance test, test environment/commit, failure modes and migration impact. Perform source changes and actual test execution; a requirements spreadsheet or passing unrelated tests are **not** implementation evidence. Integrate contract-compatible work in bounded batches under \`docs/ENGINEERING_EXECUTION_MODEL.md\`; do not manufacture unrelated tests or paperwork as substitutes for missing functionality.

### 14.8 Release and acceptance invariants

- **G01:** complete crosswalk of advertised capabilities/interfaces/transports to actual code, contracts, authorization, tests and limitations.
- **G02–G04:** adversarial fail-closed authorization, independently verified findings and reproducible raw evidence/coverage/audit with explicit trust-anchor limitations.
- **G05:** consistent durable missions/approvals/tasks/progress, cancellation, budgets, reconnect and crash/reconciliation across CLI/API/web/headless.
- **G06–G07:** zero-redesign UI controls/accessibility/deployment parity, clean install/upgrade/offline/headless and supported platform/service recovery.
- **G08–G10:** Python 3.11–3.13 tests/static/build/browser acceptance on the exact candidate; version/tag/publication identity; documentation/known-risk/release decision.

Use the architecture §11 adversarial matrix and relevant Metasploit/Tool Intelligence/provider acceptance matrices. A failed/skipped/missing check is not a pass. Keep **implemented**, **tested**, **accepted**, **partial**, **deferred**, **unsupported** and **blocked** distinct; do not calculate unvalidated overall percentages.

### 14.9 Source-confirmed blockers at the time of this plan

This is a dated snapshot, not a permanent claim: on 2026-11-03, \`main\` was \`8aa91bf659e4208f2de7fec7256254e431653603\`. Engine V2 already has immutable DAG/manifest/approval contracts, persisted plans and attempts, the scheduler, per-plan controls and an initial catalog adapter bridge. Its local-process provider bridge is explicitly limited and does not prove all catalog, session or API transports are V2-dispatchable. The old Automator retains a hard-coded Nmap-to-Nikto follow-up. The V2 web run endpoint presently submits to a **process-local** runner and explicitly does not guarantee that a submitted task survives a server crash.

PR #96 (\`engine-v2/e4-complete-provider-abstraction\`) is **open, not integrated into main** at this snapshot. Its then-current head \`b94d534c7278ffd14831a9ce0942d9044a5eb667\` adds initial router and evidence-derived follow-up planning, but CI Python 3.11–3.13 type checking failed (four errors reported in \`src/whaxon/core/providers.py\`). This PR does not close the semantic-capability, complete-portfolio, legacy-bypass or lifecycle gates. Repair, reconcile with main and rerun checks before considering merge; do not label it E4 accepted.

The remaining E1/E3 operational acceptance, E4 complete provider migration, E5 service lifecycle, E6 UI/solo release acceptance, and gated E7–E9 expansion remain independently tracked. **Unfrozen** means eligible for correction and integration—not automatically complete.


### 14.10 Implementation continuity — 2026-11-03, durable V2 run-request ownership (in progress)

**Active workstream:** E1/E3/E5 shared execution lifecycle; the source-of-truth priorities remain roadmap §0/P1/P2/P3 and architecture §§2–3/14. Work is now permitted in E0–E3 (no freeze). The one-shot CLI paths \`coverage_cmd.py\`, \`validate_cmd.py\`, \`retest_cmd.py\`, \`recon_cmd.py\` and \`run_cmd.py\` already initialize with \`drain=False\` on the inspected main revision; **do not reimplement this fixed behavior**.

**Confirmed gap before this change:** \`src/whaxon/interfaces/web/server.py\` V2 workflow run API previously returned HTTP 202 after submitting work to \`AsyncRunner\`, a process-local daemon thread. A process crash could lose the accepted run request before any durable task claim. The API explicitly admitted this limitation.

**Implementation on branch \`engine-v2/durable-run-request-lifecycle\` (not yet accepted/merged at this record):**

- Added \`src/whaxon/core/workflow_requests.py\`: one durable SQLite \`workflow_run_requests\` table (automatically installed from Core), request IDs, plan digest and bounded execution parameters; transactional deduplication of open requests; unique open-run-per-plan constraint; fenced atomic claim/heartbeat/completion; stale running requests transition to **uncertain** with no automatic replay.
- Extended \`src/whaxon/core/__init__.py\`: Core-owned \`enqueue_workflow_run\`, \`workflow_run_request\` and \`drain_workflow_run_requests\`. The existing \`WorkflowScheduler\`, authorization policy, task leases and evidence logic remain the only task execution authority; no duplicate scheduler is introduced.
- Changed V2 API \`POST /api/v2/workflows/{plan_id}/run\` to persist a run request **before** responding 202; added \`GET /api/v2/workflow-runs/{request_id}\` with stored status; background wakeups are best-effort optimizations, not the persistence mechanism. Both waitress/Gunicorn app factory and development server start a worker drain for queued requests after startup.
- Added CLI \`whaxon workflow plan drain-requests\` and \`whaxon workflow plan run-request --id REQUEST\` so a separate headless process can resume queued work and inspect the request state.
- Added \`tests/test_workflow_run_requests.py\` for restart persistence, deduplication, mismatched limits, fenced claims, stale/uncertain outcomes, denied unsupported task execution, API acknowledgment semantics and cancellation refusal.

**Safety and honest limitations:** A queued request survives process restart and can be claimed by a later worker. A previously running request is **not** automatically retried after interruption because its external effect may be uncertain. The existing task scheduler's leases, policy and independent reconciliation remain necessary. This is not yet a proof of daemon/systemd/container deployment, disaster recovery, automatic continual queue polling, or completed G05. Treat worker startup, event-loop ownership, service shutdown, request/error observability, multi-worker races and exact-candidate CI as acceptance obligations.

**Required checks before claiming implementation accepted:** Ruff and mypy; full Python 3.11/3.12/3.13 suite; workflow API and queue tests; controlled subprocess restart, overlapping workers, mid-dispatch crash, stale heartbeat, cancellation, and explicit no-unsafe-replay cases; packager/headless compatibility. Record exact head SHA and failures below after checks. Continue from this branch if PR remains open; reconcile with current \`main\` before merge. Do not merge older failing E4 PR #96 as a shortcut.

**Verification log — current implementation branch:** PR #97 is open and targets `main`. Initial CI run on `6081b649` passed setup/headless smoke where completed but failed Ruff on closure binding (B023); corrected in `d8f17bae`. Follow-on rapid commits cancelled intermediate CI runs; the latest revision's complete Python 3.11–3.13 matrix and restart-lab acceptance are **not yet verified** at this record. The run-request status GET intentionally hides lease fencing tokens; API worker-wakeup failure does not undo persisted acceptance. Do not report this batch as accepted or merged until exact-head checks complete.

**Next integration step:** Audit and complete headless worker lifecycle and task attempt reconciliation under real process restarts, then reconcile PR #96's E4 provider/follow-up changes only after successful checks. This section is the session-resumption record; update it with actual results, limitations and merge commit whenever the workstream state changes.


**Continuation update (2026-11-03):** Reviewed the current PR #97 code against cancellation and restarted-worker semantics. Closing a plan now also marks its still-queued run requests `cancelled`; a running request is not falsely reported stopped. Added regression coverage for the queued-request cancellation barrier. The status API omits private worker fencing tokens. At this point setup smoke/headless checks were green on earlier revisions, while full test-matrix acceptance and real process-kill/restart acceptance were still outstanding. These earlier check results do **not** accept the revised head. This batch is not merged until an exact-revision clean CI result; do not treat queued-intent persistence as a complete continuous daemon or E3/E5 acceptance.


**Validation findings (2026-11-03):** On earlier PR #97 revision `f5978efa`, the full Python 3.11 suite produced `1618 passed, 14 skipped, 1 failed`; Python 3.13 reported the same results. The sole failure was `test_drain_queued_work_after_restart_without_unsafe_reexecution`, which called `asyncio.run()` from the pytest-managed event loop. Corrected the regression test to use an async test and directly await `Core.drain_workflow_run_requests()` in commit `376469c0`. This correction requires a fresh exact-head CI run; prior near-green results are not acceptance. Remain explicit that a real mid-execution process-kill/restart integration test and long-lived worker polling are outstanding before complete E3/E5 acceptance.


**Regression follow-up (2026-11-03):** CI on earlier head `4588e1c4` passed 1,619 tests and skipped 14 on Python 3.11, but one recovery test still failed because the pytest async plug-in attempted to start its runner while an event loop was already active in that worker process. A local isolated worker-thread event-loop invocation replaces the test's direct async pytest execution in `a3cf3a08`, matching the V2 web worker's thread boundary. This is a test harness correction; it still requires confirmation on the **new exact commit**. Maintain honest `in progress` status and do not merge until all required jobs pass.


**PR #97 acceptance update — 2026-11-03:** PR #97, branch `engine-v2/durable-run-request-lifecycle`, was **merged to `main`** as squash commit `d3907cc21134b133f405063672773b236f4c91cf`. The exact PR head `04ef65311fc90b5a5ea517fda76fdf56dbd69978` passed **9/9 GitHub Actions checks**, including full Python 3.11, 3.12 and 3.13 jobs, Ubuntu/Windows/macOS setup, curated apt/Homebrew installation and headless Linux. Python 3.11 reported `1620 passed, 14 skipped`; no overall Engine V2 completion percentage is established by this CI result.

**What is now integrated:** Durable workflow run-intent submission before HTTP 202, bounded request deduplication, atomic claims and fenced heartbeats, conservative `uncertain` recovery without automatic replay, queued-request cancellation, Core/headless CLI/API paths, status endpoint excluding private fencing token, and regression tests. **What remains open:** Real process-kill and restart acceptance, continuous dedicated worker lifecycle/polling and service shutdown, worker-loss and task-attempt reconciliation across external effects, durable audit/outbox guarantees, all later E4–E9 gates. PR #96 remains an independent, unaccepted E4 migration and must be reconciled with this updated `main`. Next session should start from `main` at/after `d3907cc`, inspect these precise blockers, implement and validate the next bounded batch; do not recreate the already merged queue or infer that E3/E5 is fully accepted.


### 14.11 Continuation — continuous headless run-request worker (2026-11-03)

**Active branch:** \`engine-v2/continuous-run-worker\`, based on \`main\` commit \`50cb1a7894122d990099f58ad4bb0889d2973aa6\`. This is the next bounded E3/E5 implementation after merged PR #97; it is NOT an E3/E5 acceptance claim.

**Source changes:** \`Core.serve_workflow_run_requests(stop_event, poll_interval_s=1, max_runs_per_batch=20)\` continuously polls the existing SQLite-backed workflow request queue using the existing \`drain_workflow_run_requests\` and task scheduler. The new headless command \`whaxon workflow plan serve-requests --poll-interval 1 --max-runs-per-batch 20\` runs this worker until SIGINT/SIGTERM, restores prior signal handlers, and stops claiming new batches after a shutdown request. There is still just one task scheduler and one authorization path. Added \`tests/test_workflow_continuous_worker.py\` covering queued work arriving after the worker starts, restart-safe claim through another Core, stop-before-claim, invalid polling values and CLI parsing.

**Operational semantics:** The web API already persists a request before acknowledging it. A dedicated headless worker can pick it up without a browser, a request-specific daemon thread, or a fresh HTTP submission. Multiple cooperating workers use the existing transactional queue claims and fencing; the existing task-attempt subsystem retains effect ownership. SIGTERM is a request for graceful shutdown after the current batch; it does not imply cancellation of an in-flight external effect. A hard process crash can still yield \`uncertain\`, requiring reconciliation before replay.

**Acceptance remaining:** Exact-commit Ruff/mypy/Python 3.11–3.13 CI; controlled process-kill/restart and concurrent-worker tests, bounded shutdown latency for long-running tasks, task-outcome reconciliation, service-mode startup/health diagnostics and audit/outbox failure tests. This worker command is not a claim that the web server is independently supervising it or that all advertised daemon/systemd/container modes are accepted.

**Implementation refinement (2026-11-03):** A long-lived service now initializes Core once instead of re-running startup reconciliation every polling cycle. It checks the stop signal at least every 250 ms while idle, even with a long configured poll interval. Added explicit regressions for both behaviors. This is still a worker-lifecycle slice, not whole-engine or deployment acceptance.

**Next-session checkpoint:** Verify branch head and CI; fix test/runtime failures; merge only if checks pass and update this section with the exact SHA, CI run and remaining limitations. Continue E3/E5 service lifecycle and E4 provider reconciliation against the latest \`main\`, without recreating the merged request queue. PR #96 is still separate until reconciled.

### 14.12 E4 provider migration batch — 2026-11-03

**Integration checkpoint:** E4 branch `engine-v2/e4-complete-provider-abstraction` rebased as a single replacement commit on `main` 50cb1a789412. This is a *development* integration, not an E4 completion claim. PR #98 continuous worker is separately under CI and will need reconciliation if merged after this branch is formed.

**Included changes:** trusted bound-provider router with typed protocol and fail-closed ambiguity handling; catalog-wide truthful inventory of unsupported/unavailable tools; evidence-derived bounded and deduplicated follow-up plan proposals from verified workflow jobs; follow-up proposals never auto-approve or dispatch. The migration now fences V2 jobs from the legacy findings-triggered Automator **before** ToolRunner dispatch, refusing execution if the fence fails. Existing legacy jobs remain supported pending parity proof. Core V2 run-request queue and durable CLI/API code from current main are preserved; E4 Core and CLI features are layered on top rather than overwriting them. New regression tests cover the fence, refusal, router and follow-up integrity.

**Still required before E4 acceptance:** complete operation-semantic (not tool-named) capability IDs, multiple compatible providers for one operation, full session/RPC/import-only catalog reconciliation, real provider-substitution proof, E4 security regression CI and post-merge integration with E3/E5 worker lifecycle. Do not merge PR #96 until CI succeeds and the branch is reconciled against the latest main. The roadmap §0 and architecture §§10/14 remain governing authority.

**Reconciliation and regression correction (2026-11-03):** This batch rebases E4 on the merged PR #98 continuous-worker main (c0c5dd54eeeb), preserving durable run requests, long-lived workers and existing CLI/API recovery. E4 follow-up discovery runs only after a completed source plan with a succeeded task. Secondary planner exceptions are captured as `followup_error` without changing an already completed run request to `uncertain`. The previous E4 branch revision failed the existing `test_drain_queued_work_after_restart_without_unsafe_reexecution` regression (one failure across Python 3.12); exact-head CI acceptance is required. PR #96 remains development-only until green.


**E4 regression acceptance cases (2026-11-03):** The rebased batch adds `tests/test_workflow_run_requests.py` coverage proving that blocked source tasks never invoke follow-up planning and a secondary evidence/planner exception does not change a completed successful scheduler outcome. This is a separate review-only control; the planner cannot authorize or run work. Verify under Python 3.11–3.13 exact-commit CI before merge; these tests do not establish complete E4 acceptance for multi-provider or semantic capability abstraction.


**E4 batch extension and next-session checkpoint (2026-11-03):** Added explicit per-capability trusted provider selection (`BoundProviderRouter(..., preferred_providers={...})`) with no scheduler changes. Duplicate providers still fail closed unless a preferred provider is declared; missing preferred provider cannot dispatch; binding and result identity checks remain mandatory. Added provider-substitution/missing-selection regression tests. The current E4 branch contains the one-commit integrated batch, reconciled with merged PR #98 and the guarded E3/E5 workflow-completion fix. **Acceptance not yet confirmed**: exact-head Python 3.11–3.13 CI, semantic normalization of the entire existing portfolio, approval-pinned provider identity and session/RPC reconciliation remain open. Resume from PR #96 against the current `main`; check the exact head CI before any merge. Do not confuse this proof of provider selection with complete E4 acceptance.


**E4 security integration — durable execution ownership (2026-11-03):** Replaced the earlier bounded in-memory V2 job suppression list with a JobStore-backed `engine_v2_execution_jobs` provenance table. V2 providers persist ownership before invoking ToolRunner; legacy Automator checks the durable provenance on every findings callback (including repeated and post-restart events) and refuses legacy follow-up dispatch if the provenance read fails. This closes the first-event-only and 4096-entry eviction bypasses. Added regression coverage for multiple events, reopened JobStore, and unavailable provenance storage. The provenance table is transitional until legacy autochain retirement; no claim of full E4 acceptance before exact-head CI.


**E4 approval-bound multi-provider selection (2026-11-03):** For capabilities with multiple trusted provider implementations, `BoundProviderRouter.plan_binding_valid` requires the exact selected `provider_id` and `manifest_fingerprint` in the persisted workflow plan's `metadata.provider_bindings[task.id]`. `Core.authorize_workflow_task_for_plan` checks this after plan integrity verification and before authorizing the effect. A missing binding or provider switch fails closed, while single-provider plans retain compatibility. Evidence-derived follow-up plans include the selected provider binding as immutable plan metadata; this does not grant approval or dispatch. Added tests for unpinned plans, pinned provider, switched provider and follow-up binding provenance. Full CI acceptance remains required.


**Semantic contract admission (2026-11-03):** The multi-provider router now compares candidate providers' versioned typed input/output, target/protocol/auth applicability, permissions, side-effects and impact before permitting them to share an operation identity; transport and readiness may legitimately differ. Rejected incompatible providers cannot be selected even with an explicit preference. Added a regression proving a same-name provider with a different output schema is refused. This does not replace per-provider lab validation or end-to-end operation equivalence acceptance.


**Provider pin lifecycle safety (2026-11-03):** E4 now verifies explicit `metadata.provider_bindings` even when only one provider is currently registered. This closes a configuration-drift case where a previously approved plan could otherwise disregard an explicitly pinned provider or manifest fingerprint after alternatives are removed. Historical unpinned single-provider plans retain compatibility; adding alternatives requires explicit pins. Test: `test_provider_pin_remains_required_after_alternative_is_removed`. Exact-head CI is still the acceptance authority.


**E4 implementation continuation — catalog/adapter crosswalk (2026-11-03):** Added a read-only `portfolio_audit()` on the bound catalog provider and router. It enumerates the union of catalog entries and currently registered adapters and explicitly separates `bound`, `adapter_only`, `catalog_only`, `unsupported_transport`, `not_admitted` and `unbound`. No listing, missing adapter or present executable authorizes operation. The same Core method is available through `whaxon workflow portfolio-audit` and `GET /api/v2/providers/portfolio-audit`. Unit tests cover uncatalogued adapters and session-only providers; **future plugin/entry-point imports are not automatically trusted V2 execution providers**. This improves P0 reconciliation but does not yet prove the entire CLI/API/UI/transport inventory or real multi-provider operations. Exact-head CI and controlled-lab acceptance still required.


**E4 CLI/API parity regression (2026-11-03):** Added `test_e4_portfolio_audit_matches_cli_and_api` using the production Core contract. It verifies that the CLI and read-only API return the same catalog/adapter gap summary, categories partition the rows, and the API does not accept POST. This is a contract-level check; it is not proof of downstream UI integration, install-time plugin safety, or transport support. Exact-head CI remains the acceptance gate.


**E4 CI correction (2026-11-03):** The earlier E4 revision `f1dad82f` failed one existing router negative test across the Python matrix: an unknown/unbound capability was incorrectly described as a missing *preferred* provider. Corrected `BoundProviderRouter.manifest_for` to distinguish missing trusted implementation from missing explicitly selected provider, both failing closed. Added `test_router_unknown_capability_has_no_trusted_provider_error`. The earlier Python 3.12 run reported 1660 passing, 14 skipped, 1 failed; this does not accept the revised head. The follow-on portfolio-audit additions must pass exact-revision CI before PR #96 merges.


**E4 optional-provider protocol correction (2026-11-03):** The initial catalog/adapter audit revision `07b90657` failed mypy because the router invoked `portfolio_audit()` on a required `ProviderContract` that deliberately does not require it. The implementation now retrieves this **optional** hook through `getattr` and checks callability, retaining support for existing trusted providers with only the four original mandatory methods. No provider is enabled or dispatched by this audit. Exact-head CI required.


**E4 semantic-operation compatibility layer (2026-11-03):** `SemanticOperationProvider` now registers explicit stable `network.services.discover`, `web.server.audit` and other narrowly defined local-catalog operation identities alongside legacy `tool.*` aliases, without adding another runner or scheduler. The bridge converts typed operation tasks to the same existing catalog adapter, then verifies the legacy provider identity, version and fingerprint before returning a semantic-manifest result. New semantic plan tasks require explicit `metadata.provider_bindings` even with one available provider; legacy single-provider plans remain compatible. Semantic nmap evidence can now propose separate, unapproved semantic web-server follow-ups, and the provenance check accepts only the fixed tool→operation identity map. Tests verify unchanged execution path, pinned provider identity and manifest tamper refusal. **No broad claim of semantic equivalence across different tools or verified deployment is made; complete P0/P2 and E4 acceptance remain open.**


**E4 semantic-evidence regression (2026-11-03):** Added a separate evidence-to-follow-up test proving that a source scan executed under `network.services.discover` proposes only `web.server.audit` tasks with an immutable provider ID/fingerprint, without granting approval or starting execution. Legacy `tool.nmap` → `tool.nikto` plans remain supported, but the new semantic path is versioned independently. This is a controlled unit test rather than live-lab support or completed E4 acceptance.


**E4 exact-revision lint repair (2026-11-03):** CI for head `64a5aa2d` reported five Ruff errors: import ordering in Core, provider and semantic tests (four) and tuple concatenation style in the semantic manifest (one RUF005). Corrected all five without changing the execution boundary, provider selection or workflow policy. The previous head failed the Python matrix at Ruff; the next exact head must pass Ruff, mypy and pytest before acceptance or merge.

### 14.13 E3/E5 follow-up batch — stop-aware durable claim barrier (2026-11-03)

**Active implementation branch:** `engine-v2/e3-e5-stop-aware-worker-batch`, based on the already-merged PR #98 continuous worker. Previously the signal-aware worker stopped only **between** calls to `drain_workflow_run_requests(max_runs=20)`. A stop arriving during the first request could allow the remaining 19 requests in that batch to be claimed, violating the intended graceful shutdown boundary. The Core draining method now accepts an optional, validated stop-event and checks it **before each new claim**. The continuous service passes its same stop-event to the shared drain. The API and one-shot drain callers retain unchanged behavior when no event is supplied. A signalled worker does not claim queued requests; already claimed effects are neither killed nor falsely reported cancelled. Added three regression tests: stop after first job of a multi-request batch, pre-set stop leaving the queue unchanged, and malformed stop-event refusal. An absolute zero-race guarantee against signals coinciding exactly with the atomic claim is not claimed; the existing durable lease and uncertain-effect recovery still apply.

**Verification/next-session gate:** Run Ruff, mypy and full Python 3.11–3.13, cross-platform and headless CI on the exact branch head; merge only after passing checks. This is an independent E3/E5 batch and must not silently overwrite the E4 PR #96 provider/semantic work. Rebase onto up-to-date main before merge if the E4 PR lands first. Remaining E3/E5 work includes task-outcome reconciliation, service supervision, health/readiness and audited resource/stop guarantees.

**E4 + stop barrier integration checkpoint (2026-11-03):** E4 PR #96 reconciled against current main `ce10615d` preserving `drain_workflow_run_requests(stop_event=...)`, the per-claim stop barrier, and continuous service forwarding of stop events. E4 capability, follow-up and provenance changes remain layered on those current Core contracts. Base tree and tests from latest main are retained. This is an integration commit, not E4 acceptance. Revalidate exact SHA and do not merge CI failures; if green, merge as one batch then record merge SHA and follow-on gates.

### 14.14 E5 operational queue diagnostics batch — 2026-11-03

**Implementation branch:** `engine-v2/e5-run-queue-observability-batch` based on `main` after merged stop-aware durable worker. Added read-only `WorkflowRunQueue.summary()`, `Core.workflow_run_queue_summary()`, CLI `whaxon workflow plan queue-summary`, and API `GET /api/v2/workflow-runs/summary`. They expose counts of queued/running/uncertain/terminal requests, age of oldest queued intent, stale-running count and actionable reconciliation count. Summary never reports actual worker liveness, exposes no fencing token, never mutates a queue row, and never auto-retries unknown external effects. Regression tests cover cross-Core visibility, stale/uncertain, read-only inspection, invalid thresholds, and CLI/API parity. **Not accepted until exact-commit CI passes; not a daemon supervision implementation.** E4 PR #96 is a separate concurrently developed batch; reconcile against E4 after merge, retaining both provider work and E5 Core/API/CLI interfaces. This is the session continuity checkpoint.

**Integration checkpoint:** This E5 batch has been reconciled on merged E4 `main` (781246b87575), retaining E4 semantic provider contracts, report API, CLI and all provider regression tests while layering queue diagnostics only. No worker scheduling, approval or retry behavior changed. The E5 branch is reissued as exactly one commit ahead of current main. Verify Ruff/mypy/Python 3.11–3.13 and headless/cross-platform checks on the NEW revision before merging. Actual liveness supervision and guaranteed task recovery remain open.


### E5 durable queue-head quarantine and bounded continuation (2026-11-03)

The run-request claim transaction now inspects queued requests in order and
**quarantines** missing-plan or changed-plan-digest requests as `uncertain`
without dispatch. It also closes queued requests whose persisted plan is
already `cancel_requested`. Instead of stopping at the first invalid queue
head, the claim searches for eligible work within the same SQLite transaction,
with a limit of 64 entries per invocation to avoid an unbounded database lock.
A larger invalid backlog is handled over subsequent worker polls.

This fixes a potential one-shot drain starvation case and preserves existing
lease fencing, strict plan identity, no automatic uncertain-effect replay, and
the distinction between persistence and actual service liveness. Regression
tests cover valid work behind a corrupt or cancelled request, two competing
workers and all-invalid queues. **It is not proof of external-tool crash
reconciliation or an accepted E5 service-mode deployment.**

### E2 deterministic JSON contract construction (2026-11-03)

`WorkflowTask.inputs` and `WorkflowPlan.metadata` now reject unsupported
Python objects, non-string mapping keys, NaN/infinite floating-point values,
circular containers and excessive nesting **before** a workflow can be saved
or approved. Canonical approval/plan digests use strict JSON serialization
with `allow_nan=False`. Legitimate nested lists/tuples and shared-but-acyclic
subobjects remain supported; stable round trips keep the same digest.

This is an E2 source-contract safety improvement, not a migration of all
legacy finding/evidence schemas or full E2 acceptance. Regression tests
verify fail-closed validation at construction and digest boundaries.

### E3/E5 persisted run-intent contract integrity (2026-11-03)

The durable `WorkflowRunQueue` now validates stored execution limits again
**inside the atomic worker claim**, beyond its original enqueue validation.
Malformed JSON, missing/extra fields, boolean integers and out-of-bounds values
are quarantined as `uncertain` and create an audit event in the **same
transaction**. A bad queue head cannot starve a valid request behind it.
Duplicate submissions to a corrupt active request fail closed rather than
adopting an altered execution budget. Read-only status inspection preserves
the evidence of malformed stored limits as `limits: null` and
`limits_integrity: invalid`, without exposing worker credentials. Valid
worker claims still return their private lease token. Regression tests cover
multiple corruption classes, restart, audit event cardinality, valid queue
continuation and worker fencing.

**Acceptance boundary:** This is E3/E5 durability and truthful reconciliation
behavior, not proof of safe replay of unknown external effects or complete
service/container acceptance. Full E0–E6 gates and exact-revision CI remain open.

### E4 current provider-binding and adapter disappearance gate (2026-11-03)

This batch consolidates the still-useful E4 provider migration differences
from overlapping historical PRs #104 and #110 on top of current `main`.
The read-only catalog/adapter crosswalk now distinguishes a **previously
registered** `tool.*` provider whose adapter, immutable manifest or versioned
argv contract has drifted (`stale_binding`) from a binding that is **currently
eligible for resolution**. Each row exposes `previously_bound`,
`binding_current`, `bound_provider_id` and the originally registered
manifest fingerprint. A stale row is never counted as `v2_provider_bound`.
Audits neither reload nor enable providers and never approve or execute tasks.

Crucially, `CatalogAdapterProvider.resolve_task()` also checks the live
adapter registration before dispatch; an installed binary and a historical
manifest are not permission to dispatch a missing adapter. This addresses
an E4 migration/cutover safety requirement rather than adding a new tool or
transport. Tests cover adapter removal, registry-manifest removal and argv
drift, preserving the original trusted registry digest. Existing live
provider selection and immutable-plan approval remain independent gates.

**Still open:** exhaustive catalog/CLI/API/supplied UI control/transport
migration crosswalk, external-provider lab equivalence, and the explicit
legacy-autochain cutover decision. No E4 phase acceptance is asserted.

### E5 standalone systemd durable-worker integration (2026-11-03)

A dedicated `whaxon-workflow-worker.service` provides an **explicit**
foreground process supervisor for the existing durable
`whaxon workflow plan serve-requests` CLI entry point. It shares the
production web unit's restricted `whaxon` identity, environment file,
working directory and `WHAXON_DATA=/var/lib/whaxon/data` SQLite store,
while running independently of Gunicorn. The unit uses systemd
`Restart=on-failure`, SIGTERM graceful stop, restricted write paths,
and no direct public listener. No process-local in-memory handoff or
automatic replay of uncertain external effects is introduced.

`tests/test_engine_v2_e5_systemd_deployment.py` checks
service identity/storage parity, exact supported foreground CLI arguments,
and the absence of a second web-side worker command. This is a deployable
service-unit candidate, **not** evidence that it has been started and
restarted on a real supported host. Host provisioning, filesystem ownership,
reverse-proxy/auth/TLS, packaged unit placement, Docker/service lifecycle,
backup/restore and crash-recovery acceptance remain E5/P3/G07 gates.

**Release artifact delivery:** both the existing web unit and the dedicated
worker unit are now explicit source-distribution inputs and are force-included
in installed wheels under `whaxon/data/systemd/`. This makes the unit
templates retrievable from a published package; systemd installation,
permissions, path adjustments and service enablement remain manual and are
not claimed as automatic packaging behavior.

**SQLite snapshot/recovery lab:** `tests/test_engine_v2_e5_backup_restore.py`
uses SQLite's transactional backup API to copy durable run/mission state
from one Core data directory into another. It checks that a queued request
remains claimable with its original limits and digest, that the original
store remains untouched, and that a backed-up, now-stale running request
becomes `uncertain` and cannot automatically replay or reuse its old
fencing token. This tests a **database snapshot only**; a complete operator
backup additionally requires protected configuration, scope/approval
materials, evidence and installed-provider provenance. Live filesystem copy,
encrypted backups, schema upgrade and deployment restore remain unaccepted.

**State-directory provisioning:** the existing web service and the new durable
worker now use systemd `StateDirectory=whaxon` with mode `0700` and
`RequiresMountsFor=/var/lib/whaxon`. This aligns user/group ownership,
persistent state availability and the service's restricted writable path
without granting the worker root privileges or allowing a second queue store.
This is configuration-level verification, not a claim that systemd has
actually launched both units on a supported target host.

**Cross-phase CI corrections on this candidate:** The sdist exclusion
no longer strips the installed web service unit required by wheel
force-inclusion. The hard-kill crash-test marker is published atomically
before its parent asserts its contents. Late asynchronous reference
approval buttons are denied after insertion unless they belong to the
real live-approval panel; no demo operation is enabled or UI restyled.
These are exact-head CI corrections, not a full E3/E6 acceptance claim.

**CI scope correction (E6/G08):** The legacy `test_web_smoke`
findings-page assertion is a route/DOM smoke test and no longer depends
on the exact count of mutable session-scoped seeded findings. Source
and API/behavior acceptance tests still own true finding-count and
evidence correctness. This does **not** accept E6 supplied UI controls.


### E5 integration status — merged 2026-11-03

- **Merged:** PR #120, squash commit `15fd5e4058377abaea2f0103f849f3817f050ba8` on `main`.
- **Exact-head CI:** 10 of 10 checks successful on PR head `435725b7bb1ac3415a122b220491a0378f880acb` before merge.
- **Integrated scope:** independent supervised durable V2 request worker,
  restricted and persistent systemd service state, web/worker unit packaging
  in source and wheel artifacts, SQLite database-only snapshot/restore and
  stale-worker no-replay regressions, plus cross-phase test corrections.
- **Acceptance limits:** no claim of an actual systemd host deployment,
  production disaster-recovery validation, complete backup of non-database
  evidence/configuration, or final Engine V2 E0–E6 acceptance.


## Binding Engine V2 engineering execution rules — operator directive (2026-11-03)

**Status: MANDATORY.** These are repository-level execution rules for **all E0–E6 Engine V2 work**, including future implementation agents and sessions. They supplement the master roadmap (which remains authoritative) and `docs/ENGINEERING_EXECUTION_MODEL.md`. Do not substitute a serial series of tiny patches or PRs for the required coordinated phase delivery. Only the operator may explicitly authorize an exception.

1. **Roadmap is law; repository is implementation truth.** Inspect the current `main` source, tests, existing branches/PRs, authoritative roadmap, and phase acceptance gates before planning or claiming progress. Dated documentation and past branches never override verified current code.
2. **Define the entire selected phase's remaining work before coding.** Inventory all real functionality, security, durability, concurrency, recovery, migration, integration, tests, documentation, and evidence gaps for the selected phase. Build a whole-phase dependency graph, workstream ownership map, stable interface contracts and clear acceptance matrix. Do not mistake a handful of quick fixes for finishing E3 or another phase.
3. **Deliver substantial batches.** Group meaningful related implementation and adversarial regression work into coordinated batches, integrating against common contracts. Intermediate commits are permitted *inside* the phase's existing integration branch, but each small fix is not a separate deliverable or stopping point.
4. **Parallelize genuinely independent engineering workstreams.** Implement and test concurrently where dependencies and file ownership allow; assign one integrator to shared files. Parallel reads, searches, and status checks **alone** do not count as parallel development. Serialize only genuine contract, safety, conflicting-file, or acceptance dependencies. Never claim agent concurrency that did not actually occur.
5. **One phase, one branch, one PR, one final merge.** Use a single integration branch and a single PR for the selected E0–E6 phase, and consolidate all work and intermediate commits into that PR. **Do not open another PR for that phase or merge its PR until all remaining required implementation and phase acceptance work has been completed and verified.** If a phase PR already exists (E3: PR #122 at the time of this directive), continue working in it.
6. **Use CI time productively.** While CI executes, continue independent implementation, adversarial analysis, reviewing and reconciling test/evidence gaps, documentation and integration work. A new head commit requires fresh exact-head CI. Do not stop merely because a CI job is pending.
7. **No premature stopping or repeated instructions.** Work through the agreed phase plan without ending the task after a small fix, commit or status update. Do not ask the operator to repeat constraints already established. If an actual execution/tool/resource blocker prevents completion, record it precisely and leave the state truthful; never promise autonomous/background execution that cannot occur.
8. **Acceptance is evidence-based, never inferred.** Record the exact commit SHA, tests/commands, CI conclusions, execution environment, security/recovery failure injection, limitations and residual risks for every claimed gate. Code presence, synthetic-only tests, green CI on a different SHA and unweighted checkpoint percentages do **not** establish whole-engine completion, production readiness or formal gate acceptance.
9. **Preserve non-negotiable product boundaries.** Enforce scope, approval, deterministic policy, bounded execution, independent verification and durable attributable evidence; do not invent or mock missing functionality. Preserve the user-supplied UI without redesign, and do not alter protected legacy UI outside the authorized scope.
10. **Finish the phase before merging, then move on.** The sole phase PR should contain implementation, integration tests, adversarial checks, operational evidence and reconciled docs. Integrate and merge only after the required exact-head gates pass; report genuinely unverified acceptance obligations as open rather than declaring success.

**Conflict resolution:** These phase-level batching and single-PR requirements take precedence over any suggestion elsewhere in this document that a small isolated implementation slice should be merged before phase acceptance. Existing instructions to test individual components early and commit coherent internal changes remain valid *within the one phase PR*. The master roadmap's actual safety and dependency gates always remain binding.


## Engine V2 E0–E9 phase-freeze policy (operator decision, 2026-11-03)

For **every Engine V2 phase E0–E9**, engineering completion, phase merge and freeze are distinct from final integrated-engine deployment acceptance. A phase may be frozen after its required implementation and interfaces are complete, applicable automated unit/integration/adversarial/security tests and supported exact-head CI pass, residual integration obligations are recorded, and engineering sign-off is documented. Preserve the one-phase/one-branch/one-PR/one-final-merge rule. Do not infer acceptance from source presence or older CI.

**Deferred to the final full Engine V2 deployment gate, not waived:** authorized real-scanner controlled-target laboratory runs, externally protected audit-anchor/witness and retention validation, production-like service and multi-worker operation, host/network crash and recovery, backup/restore, complete cross-client end-to-end validation, and deployment/operator sign-off. These remain explicitly **NOT PASSED** until evidenced. No frozen phase, green CI or mock test implies production readiness or closes the overall release gates. Security authorization, fail-closed behavior, uncertain-effect reconciliation and audit integrity remain mandatory implementation requirements. Reopen a frozen phase only for evidenced correctness/security defects or necessary cross-phase integration repairs with regression coverage.

This operator decision supersedes earlier requirements to finish deployment-level tests *before phase engineering freeze*, but does not supersede final release safety and acceptance gates.



---

# Part II — Phase acceptance, operations and deployment gate records



## Source 4: ENGINE_V2_E1_ACCEPTANCE.md

**Provenance:** [Original source](#source-4-engine_v2_e1_acceptancemd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine v2 E1 — Correctness and security acceptance

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



---


## Source 5: ENGINE_V2_E1_QUEUE_LEASE_PRIVACY.md

**Provenance:** [Original source](#source-5-engine_v2_e1_queue_lease_privacymd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E1/E5 — Run-queue lease credential isolation

The durable run queue uses a private `lease_token` to fence worker heartbeat and
completion operations. This credential must not be returned to callers that
submit workflow execution requests.

Previously, `WorkflowRunQueue.get()` redacted the token, while
`WorkflowRunQueue.enqueue()` returned a raw row. Submitting the same plan
again while a worker was running returned the existing raw row, including its
active fencing token.

This batch introduces a shared `_public_record()` transformation and applies
it to **new enqueue**, **duplicate queued/running/uncertain enqueue** and
**request status lookup**. Only `claim()` retains the raw lease credential for
the worker that owns it. Heartbeat and finish still require the correct token,
and no queued or uncertain job is automatically replayed.

Regression coverage in `tests/test_engine_v2_e1_queue_lease_privacy.py`
checks fresh and duplicate submissions, an actively running private worker,
uncertain requests, Core/Web API response paths, and continued fencing.

**Acceptance boundary:** This is a concrete credential-confidentiality fix,
not complete authentication isolation, transport isolation, queue-operation
authorization or E1/E5 acceptance. The API's existing authentication and policy
configuration still require separate security verification.



---


## Source 6: ENGINE_V2_E3_PHASE_ACCEPTANCE.md

**Provenance:** [Original source](#source-6-engine_v2_e3_phase_acceptancemd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E3 — whole-phase acceptance register

**Scope:** E3 durable operations, on the sole E3 integration PR #122. The master roadmap §0/P2 and the V2 crosswalk §14 are authoritative.

**Decision:** ENGINEERING FREEZE PENDING exact-head CI and engineering sign-off. Real-world lab, independent external audit anchor and production recovery validation are mandatory at the final integrated Engine V2 deployment gate, not at the phase engineering freeze. Source tests below are test *definitions*, not claims of observed passing results until a cited exact-head run succeeds. Zero additional phase PRs or premature merge permitted.

| Gate | Required behavior and evidence | Source/test candidate | Current decision |
|---|---|---|---|
| E3-A | Durable mission, plan, task and attempt lifecycle across reopen | `store.py`, `tests/test_workflow.py` | SOURCE_PRESENT, acceptance open |
| E3-B | Atomic claims, multi-process workers, no double ownership | `tests/test_engine_v2_e3_process_boundaries.py` | SOURCE_PRESENT, acceptance open |
| E3-C | Plan and mission attempt, concurrency, deadline, rate, cost budgets enforced during claim and dispatch | `tests/test_workflow.py`; `tests/test_engine_v2_e3_dispatch_gate_classification.py` | SOURCE_PRESENT, acceptance open |
| E3-D | Cancellation and stop intent durably fenced through final run-request completion | `tests/test_engine_v2_e3_queue_atomicity.py` | SOURCE_PRESENT, acceptance open |
| E3-E | Expired task/request leases fenced and reconciled without blind replay | `tests/test_engine_v2_e3_process_boundaries.py`; `tests/test_engine_v2_e3_recovery_boundaries.py` | SOURCE_PRESENT, acceptance open |
| E3-F | Actual controlled external HTTP side effect, worker hard kill and response disconnect; no retry | `tests/test_engine_v2_e3_external_effect_crash.py` | NEW TEST DEFINED, CI pending |
| E3-G | Corrupt run-request limit/digest, plan drift and missing source fail closed | `tests/test_engine_v2_e3_e5_queue_integrity.py`; `tests/test_engine_v2_e3_completion_identity.py` | SOURCE_PRESENT, acceptance open |
| E3-H | Audit event/state write failure rolls back all related transitions | `tests/test_engine_v2_e3_queue_atomicity.py` | NEW TEST DEFINED, CI pending |
| E3-I | Event cursors monotone and persisted; at-least-once delivery, post-effect failure redelivery and independent consumer isolation | `src/whaxon/core/outbox.py`; `tests/test_workflow.py`; `tests/test_engine_v2_e3_outbox_delivery.py` | NEW DELIVERY TESTS DEFINED, CI pending; external transport acceptance open |
| E3-J | Semantic audit integrity cross-check and fail-closed reporting | `tests/test_engine_v2_e3_audit_semantic_integrity.py` | NEW TEST DEFINED, CI pending |
| E3-K | Lifecycle snapshot stable across restart; changed event/attempt/task detected against caller-held digest | `tests/test_engine_v2_e3_audit_snapshot_anchor.py`; `tests/test_engine_v2_e3_audit_cli.py` | NEW TEST DEFINED, CI pending |
| E3-L | Independently protected trust anchor, retention and deletion contract verified under database tampering | Operator-controlled external anchor and witness evidence required | **DEFERRED TO V2 DEPLOYMENT — NOT PASSED** |
| E3-M | Real authorized scanner external effects plus crash, network failure, host restart and independent reconciliation | Approved lab target, recorded run, side-effect ledger and recovery transcript required | **DEFERRED TO V2 DEPLOYMENT — NOT PASSED** |
| E3-N | Production multi-worker/service/database-backup and restored-client operational recovery | Systemd deployment, backup including config/evidence, supported host, recovery evidence required | **DEFERRED TO V2 DEPLOYMENT — NOT PASSED** |
| E3-O | Supported Python/platform lint, mypy, tests, package and security checks on exact PR SHA | GitHub Actions workflow `.github/workflows/ci.yml` | **OPEN until exact-head CI succeeds** |
| E3-P | Signed reviewer/operator acceptance, SHA, test commands, environment, residuals and rollback | Final acceptance record | **OPEN** |

## Governing phase-freeze decision (applies to Engine V2 E0–E9)

Every Engine V2 phase may be engineering-accepted, merged and frozen once its implementation, phase-level automated adversarial/security/integration tests, exact-head supported CI and engineering sign-off pass. External authorized-scanner labs, independently operated audit-anchor/witness retention, and production-like service, host-restart and backup/restore testing are deferred until the fully integrated V2 engine is ready for deployment. Deferred gates are NOT PASSED and must be retained for final deployment acceptance; no production-readiness claim or release closure is permitted before they pass. Frozen phases may be reopened for proven security, correctness or cross-phase integration defects, with regression evidence. This decision supersedes earlier phase-freeze prerequisites without weakening execution authorization, fail-closed safety or audit integrity.

## Coordinated workstreams and integration rules

- **W1 — durable queue/worker ownership:** `workflow_requests.py`, process and recovery tests. Own enqueue/claim/finish/cancel lease transitions and reconciliation.
- **W2 — scheduler and persisted budgets:** `scheduler.py`, `store.py`, budget/deadline/concurrency and cancellation correctness, with one integration owner for shared `store.py`.
- **W3 — audit/outbox integrity:** event cursors, transaction rollback tests, immutable snapshot reference API and external anchor delivery contract. Never claim local hashing proves immutability.
- **W4 — independent adversarial validation:** loopback HTTP crash/disconnect, process kill, multi-worker races, corrupted ledger and audit writes; controlled authorized scanner effects remain a separate E3-M gate.
- **W5 — operator surface, evidence and integration:** CLI/Core audit interfaces, exact-head CI results, E3/E5 operational handoff, recovery/rollback documentation and the single-PR merge gate.

Workstreams may proceed concurrently only with stable contracts and explicit file ownership. A single integration owner combines shared-file changes. Parallel source reads do not count as independently implemented engineering.

## Required exact-head gate evidence

Record, on the *final* PR SHA: Python 3.11/3.12/3.13 CI job names and conclusions, all E3-focused test names and outcomes, real process/network failure evidence, environment and commands, deployment/recovery lab constraints, an independently retained audit snapshot witness, limitations, reviewer and rollback decision.

**Never infer a phase-completion percentage from this register's number of SOURCE_PRESENT rows.** Until every required gate is accepted, E3's formal status is open. The implementation may be substantial without full acceptance.

## Operator lifecycle audit snapshot workflow

Run `whaxon workflow --data-dir <state> plan audit-snapshot --id <plan>` and **save the displayed digest outside the WHAXON host/database in an independently protected store**, with plan ID, UTC time, environment and code SHA. Later run `whaxon workflow --data-dir <state> plan audit-verify --id <plan> --expected-digest <64-hex-reference>`. A result of `digest_matches_reference: true` proves equality to the caller-provided reference for the documented snapshot scope only. It does **not** authenticate the source of that reference. Both subcommands are read-only.

### Snapshot content verification scope

The candidate E3 lifecycle digest now includes persisted plan JSON plus task input/dependency/permission/impact/timeout/idempotency contracts in addition to task states, attempt outcomes and ordered workflow events. The digest output does not expose those potentially sensitive values. Tests independently tamper with plan JSON and task inputs; both must mismatch an external reference. This remains **local candidate implementation**, not acceptance of an independently operated trust anchor.



---


## Source 7: ENGINE_V2_E3_RECOVERY_BOUNDARIES.md

**Provenance:** [Original source](#source-7-engine_v2_e3_recovery_boundariesmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E3 — Durable recovery boundary hardening (2026-11-03)

**Scope:** One implementation batch, no scheduler/provider/transport redesign.

- Duplicate run-request submissions now compare the existing persisted request's plan digest with the current source plan digest. A changed digest refuses the duplicate submission and keeps the historical queue record intact for safe claim-time quarantine/reconciliation. This check applies to queued, running and uncertain active requests; it does not grant authority or rebind any plan.
- Task-attempt stale-lease recovery rejects boolean, nonfinite and invalid timeout thresholds **before** acquiring the reconciliation transaction. A NaN threshold must not silently make stale recovery a no-op.
- Focused tests in `tests/test_engine_v2_e3_recovery_boundaries.py` cover queued and running plan drift, preserved worker-token privacy, existing claim-time quarantine, invalid-threshold no-mutation and valid fresh-lease preservation.

**Limits:** These are concrete safety hardenings, not proof of real scanner-effect cancellation, complete external-effect reconciliation, independent audit integrity, outbox delivery or the full E3 acceptance gate. CI execution results belong to the exact PR/head revision and must not be assumed from source inspection.

## Coordinated E3 atomicity/recovery batch

- **Cancellation-to-completion fence:** run-request terminal status and plan cancellation are serialized in the same SQLite write transaction. Any worker completion after a cancellation is recorded as `uncertain` with one durable `workflow_run_uncertain` event, never as success. Missing source plan cannot certify a completed run.
- **Audit fail-closed:** an audit insert failure rolls back the run-request status transition. Regression tests use real SQLite `RAISE(ABORT)` triggers to inject write failures at cancellation completion, stale run recovery, claim-time changed-digest quarantine, and task-attempt recovery. These are local database atomicity checks, **not** an externally anchored audit delivery guarantee.
- **Bounded run-request reconciliation:** the durable run queue processes at most 128 stale requests per transaction, and its continuous worker revisits remaining requests on later polls. Global task-attempt startup recovery retains its existing all-stale-attempts-per-call behavior so a one-time initialization cannot silently strand the 129th attempt. Bounded task recovery with guaranteed full draining remains a separate integration concern; do not claim that task recovery is bounded.
- **Integration contract:** no change to automatic retry of uncertain external effects, no authority escalation or provider redesign. Full E3 acceptance still requires real external-effect crash/side-effect validation, independent trust anchor/outbox delivery semantics, whole-lifecycle worker deployment and exact-head CI evidence.

## Scheduler dispatch gate classification

- `mark_workflow_dispatch_started()` can refuse dispatch due to cancellation **or** a newly expired deadline/tightened mission or plan budget. The scheduler now records a non-cancellation refusal as **blocked** rather than falsely labelling it **cancelled**. A true durable cancellation remains **cancelled**. No refused task invokes a provider.
- Parameterized scheduler tests tighten the plan deadline, exhaust mission cost permission and request cancellation *after the second policy check but before external dispatch*. These verify exact terminal status and absence of `dispatch_started` evidence.

## Controlled external network side-effect crash validation

- `tests/test_engine_v2_e3_external_effect_crash.py` uses a bound 127.0.0.1 HTTP server, not a simulated local-file-only callback. A child process sends a real POST, receives HTTP 204, and is killed before reporting an attempt result. Stale lease reconciliation must mark the external outcome **uncertain**, refuse retry, keep readiness unaccepted, and leave the receiver's side effect count at exactly one.
- A second test has the HTTP receiver accept the POST and deliberately disconnect without a response. The scheduler must record an **uncertain** post-dispatch exception; subsequent invocations must not retry.
- These tests are **controlled local-only network effects**, not proof of behavior with production scanners, live pivoting, remote servers or a verified independent trust anchor. They are designed to execute in the existing exact-head Python CI matrix.

## Completion-time plan identity and worker uncertainty

- The terminal write transaction now checks both the cancellation state **and the original bound plan digest**. A changed plan digest cannot produce `completed`, `incomplete` or `failed` final status under the obsolete intent. The run is `uncertain`, its original digest is preserved, and an audit event is committed atomically.
- A worker explicitly reporting `uncertain` also produces exactly one transactional, bounded reason-coded `workflow_run_uncertain` event. Raw provider error text is not copied into the audit detail. Audit insertion failure rolls back the queue transition.
- Missing source plans remain uncertain but cannot write a plan-scoped event to a nonexistent plan; the queue row retains the failure reason. This is an explicit operational limitation, not proof of independent auditing.

## Audit semantic integrity and readiness

- The internal, non-cryptographic workflow audit consistency check now rejects terminal event names that disagree with their attempt's persisted terminal status, terminal events attached to still-running attempts, duplicate dispatch-intent events and events referencing unknown attempt IDs. All findings fail readiness closed. This does not independently prove that an attacker did not modify **both** the event table and attempt table.
- The readiness flag `requires_manual_reconciliation` now reports whether an in-flight or uncertain attempt actually needs manual reconciliation, rather than returning true for every ordinary healthy pre-dispatch attempt. In-flight effects after dispatch remain explicitly in need of reconciliation until confirmed.
- Regressions mutate real SQLite rows (not fake mocks), then check both audit diagnostics and success readiness.

## Externally anchorable read-only lifecycle digest

- `JobStore.get_workflow_audit_snapshot(plan_id)` hashes the versioned plan identity, ordered durable task/attempt state and persisted event stream from one SQLite read transaction. It exposes only the SHA-256 digest and counts, not raw event details, inputs or stored results.
- `verify_workflow_audit_snapshot(plan_id, expected_digest)` compares a caller-retained reference with the current snapshot. A separate operator-controlled, immutable or independently protected location must retain **the original digest** (and associated plan, SHA, environment and observation time) before this protects against rewriting the local database. Tests mutate event, task and attempt records and detect mismatch across restarts.
- **Not a shipped independent trust anchor.** This API cannot prove its own previous digest was retained externally; it is no substitute for a signed/anchored audit log or an approved operational retention/deletion procedure. The snapshot does not cover external provider-side effects, legacy jobs outside this workflow, or binary evidence files. `independent_anchor_verified` remains `False`.

## Operator-facing shared CLI/Core service

- `Core.workflow_audit_snapshot()` and `Core.verify_workflow_audit_snapshot()` surface the store's read-only versioned lifecycle digest. `whaxon workflow plan audit-snapshot --id ...` prints the digest; `audit-verify --id ... --expected-digest ...` returns nonzero on mismatch.
- The CLI explicitly emits `independent_anchor_verified: false` even on a matching caller-provided digest. Operator-managed independent retention and a recorded witness are mandatory for external trust assurance. See `docs/ENGINE_V2_E3_PHASE_ACCEPTANCE.md`.

## At-least-once lifecycle outbox delivery

- `WorkflowEventOutbox.deliver()` and shared `Core.deliver_workflow_outbox_events()` deliver a bounded page of persisted events to a caller-provided trusted transport callback, checkpointing its consumer cursor **only after** each callback returns successfully. A failed callback never advances its event checkpoint. Each consumer has an independently durable cursor across restarts.
- A simulated downstream effect followed by an exception leaves the event deliberately unacknowledged and proves duplicate delivery on retry; receivers **must** deduplicate by `(plan_id, event.id)`. An internally inconsistent workflow audit refuses publication. The service makes no exactly-once claims and does not configure or authenticate an external transport by itself.
- Remaining E3 acceptance requires an actual independently supervised publisher process/transport, authenticated downstream sink, external receipt evidence, fault/restart tests and external protected audit anchor.

- The current synchronous outbox contract refuses an awaitable/coroutine return (with no acknowledgement); otherwise accidentally passing an async callback could checkpoint an event before the coroutine ever executes. An asynchronous transport needs a separately awaited publisher boundary and its own acceptance tests.



---


## Source 8: ENGINE_V2_E3_RUN_REQUEST_AUDIT_EVENTS.md

**Provenance:** [Original source](#source-8-engine_v2_e3_run_request_audit_eventsmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### E3 — Auditing uncertain durable run requests

Engine V2 run requests are persisted independently from task-attempt records.
When an unclaimed request's persisted plan digest changes, the queue
conservatively transitions it to `uncertain`. When a running request's
heartbeat expires or is missing, reconciliation likewise marks it `uncertain`
rather than replaying its possible external effects.

This batch adds a **same-transaction** `workflow_run_uncertain` event to the
existing `workflow_events` feed for each such transition where the plan is
still present. The event carries only the run request ID and one bounded
reason (`plan_digest_changed` or `worker_lease_lost`); it does **not**
expose lease tokens, worker identifiers, task inputs, or other secrets.
Reconciliation is idempotent: a second inspection of an already uncertain
request does not write another event.

If a workflow plan has been deleted, its queue row may still be quarantined,
but no now-orphaned plan event is fabricated.

These events improve persistence and operator traceability; they are **not**
a tamper-proof independent trust anchor, verified external-effect outcome,
or complete transactional outbox implementation. The E3/P2 and G04/G05
crash, audit-failure, recovery and release acceptance gates remain open.



---


## Source 9: ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md

**Provenance:** [Original source](#source-9-engine_v2_e5_caller_inventory_and_rollbackmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E5 — caller and execution-authority inventory with rollback controls

**Status:** evidence-backed inventory, **not** E5 engineering phase acceptance.
**Inspected implementation:** E5 PR #124 head `fe628013bf04309f262224f62179ff9c3438c1a2`.
**Governing rules:** master roadmap P2/P3, G05/G07; E5-A/E5-B/E5-C/E5-G; architecture crosswalk §14.7; engineering execution model.

## Observed execution paths and ownership

| Surface | Source/contract | Durable V2 authority | Current limit |
|---|---|---|---|
| V2 run API | `src/whaxon/interfaces/web/server.py`: `POST /api/v2/workflows/<plan_id>/run` | `Core.enqueue_workflow_run` commits before HTTP 202 | In unsupervised legacy web mode, best-effort process-local wakeup remains; HTTP 202 is not execution success |
| V2 status/reconnect | `GET /api/v2/workflow-runs/<id>`, `/snapshot`, `/summary`, `POST /cancel` | `Core.workflow_run_request`, `workflow_run_snapshot`, `workflow_run_queue_summary`, `cancel_workflow_run_request` | Snapshot uses separately persisted views, not atomic cross-table read; worker liveness is **not verified** |
| V2 CLI request | `src/whaxon/interfaces/cli/workflow_cmd.py`: `plan submit-run` | Same Core enqueue and bounded identity as API | No direct execution claim or task success on submission |
| V2 CLI inspection | `plan queue-summary`, `run-request`, `run-snapshot`, `cancel-request`, `progress`, `readiness`, `evidence` | Same Core/store paths as web API | Not a full proof that every legacy frontend uses these services |
| Headless worker | `plan serve-requests` | `Core.serve_workflow_run_requests` polls and calls `drain_workflow_run_requests` | One worker process can own claims with fencing; no automatic replay of uncertain effects |
| Manual queue drain | `plan drain-requests` | Same Core transactional queue and lease fencing | Should not run ad hoc in paired supervision without operator coordination |
| Gunicorn web factory | `create_app_factory()` | When `WHAXON_V2_EXTERNAL_WORKER=1`, no web-startup local V2 drainer | Without the flag, backwards-compatible process-local wakeup remains |
| Flask V2 run route | `workflow_v2_run()` | Same external-worker flag suppresses per-request web drainer | The persisted 202 remains available even if worker is down |
| systemd web + worker | `whaxon.service`, `whaxon-workflow-worker.service` | Web unit sets external-worker mode; worker runs CLI `serve-requests` | Unit definitions and static tests are not successful host installation |
| Docker web + worker | `docker-compose.e5.yml`; `Dockerfile` | Web external-worker mode, dedicated worker, common `/data` volume | CI launch/persistence tests are an engineering surrogate, not production-host sign-off |
| Synchronous V2 CLI plan run | `workflow_cmd.py`: `plan run` | `Core.run_workflow_plan` executes through V2 plan authorization, provider binding and scheduler/task lifecycle | Synchronous V2 execution; it does not enqueue a durable run request. This is distinct from the legacy direct CLI runner. |
| Durable V2 CLI request | `workflow_cmd.py`: `plan submit-run`, `plan serve-requests`, `plan drain-requests` | Core run-request queue and worker lifecycle | Durable request and worker path; submission is not execution success. |
| Legacy direct CLI run | `interfaces/cli/run_cmd.py`: `whaxon run` | Direct `ToolRunner` / session dispatch | Legacy execution authority remains outside V2 plan/task ownership; preserve until explicitly reconciled and accepted. |
| Legacy web tools/AI | `server.py`: `POST /api/run`, `POST /api/ai/run` and Metasploit paths | Existing JobRegistry/AsyncRunner/runner integrations | **Separate legacy execution authority remains**; do not declare platform-wide single-authority completion |
| External effect scheduler | `Core.run_workflow_plan`, workflow scheduling, `WorkflowRunQueue.claim/finish/reconcile_stale` | Task-level authorization/lease and request-level fencing | Failed/expired worker effects become uncertain, never silently requeued |

**Important distinction:** the new paired deployment has a single **V2 durable run-request drainer** by default. WHAXON still contains legacy direct execution paths and interfaces. E5-A cannot be fully accepted until their permitted coexistence, migration, security boundary and rollback are explicitly reviewed.

## Current evidence (not whole-phase sign-off)

- `tests/test_workflow_run_requests.py`: request persistence, deduplication, cancellation, reconnect, external-worker mode and cross-client submission parity.
- `tests/test_workflow_continuous_worker.py`: shutdown, poll, lost lease and bounded queue continuation.
- `tests/test_engine_v2_e5_queue_head_recovery.py`: poisoned heads, bounded quarantine and stale lease recovery.
- `tests/test_engine_v2_e5_systemd_deployment.py`: two-unit contract with matched identity and shared state.
- `tests/test_engine_v2_e5_docker_compose.py`: isolated Compose deployment, image resources and hardening.
- `tests/test_engine_v2_e5_state_snapshot.py`: SQLite+configuration+evidence snapshot, checksum verification, tampering and no-overwrite restore.
- `.github/workflows/ci.yml`: paired Docker web/worker launch, inert request, worker restart, cold offline snapshot and isolated restored mission check.
- The exact final E5 PR-head CI run and supervised real-host/service deployment evidence must be recorded before E5-F/E5-E are closed.

## Controlled rollout and rollback

1. Before rollout, select the authorized deployment target, persist the exact artifact digest/commit, documented scope, credentials and endpoint exposure plan. Identify a responsible operator and establish an external evidence/manifest witness.
2. Prevent new submissions, stop **both** web and worker services, and take an offline full-state snapshot with `python -m whaxon.core.state_snapshot backup`. Retain the resulting manifest SHA-256 **outside** WHAXON data and verify it independently.
3. Deploy the matching web and worker package/image as a pair. Use `WHAXON_V2_EXTERNAL_WORKER=1` for the web side so the web accepts durable requests but does not separately drain them. Keep the worker under systemd or Compose supervision.
4. Check readiness truthfulness and queue status. Use only explicitly approved inert/sandboxed workflow targets for admission, reconnect, cancellation and restart checks; record request IDs and exact result evidence. A 202 or successful health probe is never proof of external execution.
5. On failure, stop new intake, stop both processes and inspect all running, stale and uncertain attempts. Do **not** downgrade SQLite/schema, auto-requeue uncertain requests, blindly delete credentials, or convert queued work into a success claim.
6. Restore only a verified matching-version full-state snapshot into a new protected directory. Verify manifest against its externally retained digest; restore operator-controlled secrets, scope and permissions separately where needed. Validate queue reconciliation before a deliberate cutover.
7. Do not remove external-worker mode to fall back to web-only execution while old accepted queued work is present without explicit policy review: startup web draining could begin execution unexpectedly. Version rollback and schema migration require independent compatibility tests and operator approval.

## E5-A through E5-G decision

All seven whole-phase engineering gates remain **OPEN** until the acceptance file records a checked source baseline, exhaustive supported-path matrix, cross-client contracts, adversarial and live service evidence, exact-head CI for required platforms, migration/rollback verification and an explicit engineering acceptance decision. Final production lab, host/container, independent audit anchor and real external-target acceptance remain additional non-waivable deployment gates under the master roadmap.

This inventory does not authorize direct security tooling, scanner use or any unapproved target.



---


## Source 10: ENGINE_V2_E5_PHASE_ACCEPTANCE.md

**Provenance:** [Original source](#source-10-engine_v2_e5_phase_acceptancemd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E5 — whole-phase engineering acceptance register

**Status (2026-11-04 engineering decision):** E5 **ENGINEERING-ACCEPTED FOR SUPPORTED DURABLE V2 SERVICE SCOPE**, conditional on exact final documentation-only PR-head CI and final PR review. Not production deployment-accepted. Earlier OPEN statements below are dated pre-decision evidence checkpoints and are superseded only within the bounded engineering scope set out in the final decision.
**Authority:** master roadmap P2/P3, G05/G07; Engine V2 crosswalk §14.1, §14.2, §14.7–14.8 and binding execution rules; engineering execution model.
**Integration branch:** `engine-v2/e5-whole-phase-integration` (one phase, one PR, one final merge).

## Verified baseline / reuse, not acceptance

- Existing Core durable run-request enqueue, claim, stop-aware drain, continuous worker, fenced leases and conservative uncertain-effect reconciliation.
- Shared queue summary in Core, CLI and API; summary explicitly does not verify worker liveness.
- Packaged web and worker systemd units, restricted state directory, core/store readiness, SQLite snapshot regression and stale-worker no-replay tests.
- E3 merged on `main` as `ad192b931a1480eaad76d3a11735cbe1d85b4818`; retain its audit/outbox and durability contracts. Existing unit tests and prior CI are not proof of full E5.

## Whole-phase dependency graph and bounded workstreams

| Stream | Owner boundary | Dependencies | Engineering acceptance |
|---|---|---|---|
| S1 — shared application contract | Core mission/run/approval/progress/evidence service and versioned response semantics | E2/E3 durable state, E4 provider policy | CLI/API/headless invoke the same persisted service authority; no browser-owned execution or second scheduler; compatibility tests |
| S2 — worker lifecycle | Core worker, queue, stop/reconciliation and scheduler integration | S1 stable contracts; E3 fencing | Concurrent claims, SIGTERM/drain, heartbeat/lease loss, crash injection, no duplicate external effect or unsafe automatic replay |
| S3 — client reconnect and observability | API/CLI/UI integration through existing service endpoints | S1 persisted identifiers, S2 state | Disconnect/reconnect/restart can inspect truthful persisted status, progress, errors and reconciliation; no lease credential leakage |
| S4 — deployment and readiness | Headless entry points, health, packaging, service templates, secrets/configuration | S1–S3 behavior | Clean-wheel/sdist, CLI and worker unit parity, optional dependencies degrade independently, readiness never asserts worker liveness without proof |
| S5 — independent adversarial verification | Tests and acceptance register; no conflicting production source ownership | S1–S4 integrated revisions | Cross-process races, cancellation, failed audit/store, stale worker, corrupted state, replay denial, authorization/identity and migration regression; exact-head supported CI |

One integration owner coordinates changes to shared Core and service contracts. Workstreams may proceed in parallel only after their interfaces and ownership are stable. Do not merge partial work as a separate E5 PR.

## Engineering gates (all OPEN until evidenced)

- **E5-A:** Complete actual caller/endpoint/worker/service inventory and contract migration, including legacy paths and rollback; no second execution authority.
- **E5-B:** Durable mission/run/approval/progress/evidence/verification service parity across CLI/API/web/headless for supported operations.
- **E5-C:** Durable client disconnect/reconnect and process restart with truthful status, cancellation and no unapproved side effects.
- **E5-D:** Multi-worker claims, fencing, shutdown, lease expiry, uncertain-effect reconciliation and adversarial recovery tests.
- **E5-E:** Headless lifecycle, health/readiness, secret/path permissions, supported package/service modes and failure behavior verified at engineering-test level.
- **E5-F:** Exact-final-head lint, types, Python 3.11–3.13, cross-platform packaging, security and integration CI with recorded SHA, run links and limitations.
- **E5-G:** Explicit engineering review, rollback/migration plan, reconciled crosswalk/roadmap and controlled phase freeze decision.

## Final integrated V2 deployment gates — DEFERRED, NOT PASSED

Authorized real-scanner laboratory, production-like host/service/container and multi-worker recovery, full backup/restore of evidence/configuration, independent external audit anchor, and complete cross-client end-to-end deployment/operator sign-off are mandatory at the final Engine V2 deployment gate under the 2026-11-03 operator decision. They are **not** waived and no phase freeze implies production readiness.

**Next implementation target:** complete S1/S2/S3 source-level contract inventory and build coordinated functional and adversarial changes, not standalone documentation or superficial test-count milestones.


### Shared reconnect contract — engineering implementation in progress

The Core `workflow_run_snapshot(request_id)` contract returns the persisted
request and its durable workflow progress with explicit
`worker_liveness_verified=false` and `automatic_uncertain_replay=false`.
The web route `GET /api/v2/workflow-runs/<request_id>/snapshot` and
`whaxon plan run-snapshot --id <request_id>` consume this same Core
contract. A request is not proof of execution, and the read models are
individually persisted views, not an atomic cross-table snapshot.

Adversarial tests cover restart/reconnect, duplicate-submission fencing,
lease-token secrecy, bounded stale recovery, and durable-health fail-closed
behavior. **All test results and E5 gates remain unverified until exact-head
CI and applicable integration evidence are recorded.** No production or
deployment acceptance is claimed.


### Accepted-intent reconnect discovery

A successful `POST /api/v2/workflows/<plan_id>/run` returns HTTP 202,
`run_request_id`, `run_request_url`, `run_snapshot_url`, and the existing
`durable_progress_url`. The snapshot URL derives from the persisted request
identity and remains usable after a different web process starts against the
same data directory. Duplicate active submissions with identical bounds reuse
the same durable request identity. A 202 is **not** execution success.


### Bounded lost-lease reconciliation and stop behavior

The headless drain now repeats the existing 128-record transactional
stale-lease reconciliation until no stale leases remain before admitting
new work. A stop signal exits between bounded passes. This is recovery
bookkeeping only: no uncertain request is automatically re-executed.
The worker still requires exact-head CI and multi-process adversarial
acceptance before E5-D can close.


### Cancellation and lease-loss reconnect tests

The cross-process API acceptance suite now exercises queued cancellation,
durable cancellation after Core restart, stale-worker reconciliation, and
credential-free inspection of an uncertain request. These tests require
execution and exact-head CI evidence; their presence alone does not close
E5-C or E5-D.


### Request-identity cancellation

The Core `cancel_workflow_run_request(request_id)` operation and the
API `POST /api/v2/workflow-runs/<request_id>/cancel` and CLI
`plan cancel-request --id <request_id>` share the existing persisted
plan cancellation barrier. Unknown requests fail closed. Running external
effects are never represented as stopped by this acknowledgement. This
cancels the associated plan, not an isolated task.


### Adversarial concurrency coverage

Additional tests race 24 independent HTTP submissions against one durable
SQLite request and race request-identity cancellation against a worker claim.
The allowed cancellation/claim race outcomes are either cancellation before
claim or a previously claimed run with a durable stop barrier; neither permits
a second claim. These are engineering tests pending exact-head CI, not
production multi-host proof.


### Poisoned backlog progress in one-shot drains

The Core drain now retries a bounded number of claim passes when a
64-record poison quarantine yields no claim but queued intents remain.
This prevents one-shot headless/CLI drains from mistaking a bounded
quarantine yield for an empty queue. Retries are capped at 16 passes
per requested run to prevent starvation from an unbounded producer.
No uncertain intent is automatically replayed.

### E5 integration evidence update — backup and paired-container verification

The active E5 PR #124 now includes a separated `docker-compose.e5.yml`
web/worker deployment candidate, non-root state-volume preparation, and CI
that starts both containers, checks Core readiness, observes persisted state
across a worker restart, and requires an inert blocked workflow to be consumed
without launching an external scanner. A paired service smoke does not replace
real supported-host operation or prove production worker liveness.

An offline state snapshot module `src/whaxon/core/state_snapshot.py` and
`tests/test_engine_v2_e5_state_snapshot.py` cover SQLite plus scope/evidence
file preservation, per-file digest verification, symlink rejection, tamper
detection and no-overwrite restore. Services must be stopped by the operator;
the manifest does not authenticate itself and external evidence anchoring,
backup rotation, off-host retention and host-level disaster recovery remain
unaccepted. All additions are **candidates pending exact-head CI** and the
final E5-A through E5-G review; no deployment or phase sign-off is asserted.

### Durable run submission parity — implementation candidate

The E5 integration branch adds CLI `plan submit-run` using the same Core
`enqueue_workflow_run()` transaction and limits as API
`POST /api/v2/workflows/<plan_id>/run`. A cross-client test verifies that
identical CLI/API submissions deduplicate to one durable request and changed
limits fail closed, without starting external effects. This is *bounded run
submission parity*, not evidence that all legacy CLI direct execution paths
have migrated. E5-A and E5-B remain open pending exact-head CI and full
caller inventory.

## Caller-inventory and rollback checkpoint

Read [E5 caller and execution-authority inventory](#source-10-engine_v2_e5_phase_acceptancemd) before any claim of E5-A/G completion. It distinguishes the sole supervised V2 queue worker from preserved legacy CLI/web/AI tool execution and specifies fail-closed rollback and full-state recovery. As of this document update, **E5-A through E5-G remain OPEN** pending exact-head CI, remaining migration decisions and operator acceptance.

### Two independent worker processes — adversarial claim test

`tests/test_engine_v2_e5_process_claims.py` now starts two independent
Python processes against the same persisted SQLite run request, waits for
both to be ready, releases them together and requires only one claim/blocked
workflow result. This strengthens E5-D beyond thread-only tests. It uses an
unsupported fixture capability, **never** an actual scanner or target. The
whole gate remains OPEN until exact-head CI and wider failure injection,
restart and recovery evidence are accepted.

### E5 offline recovery verification expansion (pending exact-head CI)

A full-state restore regression now preserves a previously claimed request,
forces an expired lease after restore, and requires the outcome to become
`uncertain`. The restored worker cannot reclaim or mark that external effect
completed using the old fencing token. Scope and binary evidence are checked
alongside the same persisted run identity. Separate tests reject missing and
unexpected snapshot files. Evidence copies use bounded-memory streaming.
This does **not** simulate an actual power loss, prove host quiescence, establish
external evidence authenticity, or close E5-D/E5-E without the required
real-service recovery acceptance.

## Engineering exit review — 2026-11-04, E5 PR #124

**Decision state:** ENGINEERING ACCEPTANCE CANDIDATE; **NOT YET FROZEN OR MERGED**.
The implementation must pass exact-final-commit CI, and the reviewer must record
the complete SHA, check results and explicit decision before phase freeze.
Production release and final integrated Engine V2 deployment acceptance remain
separate, open milestones under the roadmap's E0–E9 phase-freeze policy.

### Whole-phase evidence and remaining boundaries

| Gate | Source and evidence | Engineering assessment |
|---|---|---|
| E5-A — shared execution authority | `src/whaxon/interfaces/web/server.py` `WHAXON_V2_EXTERNAL_WORKER=1` prevents web-owned V2 draining; `Core.enqueue_workflow_run`, `WorkflowRunQueue.claim`, `whaxon workflow plan submit-run`; `tests/test_workflow_run_requests.py`; `docs/ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md`; Docker CI stops worker, tests HTTP 202 remains queued and starts worker separately | One durable **V2** queue authority in paired deployment is implemented. **Legacy direct CLI/web/AI execution has NOT migrated**. It remains an explicitly enumerated P2/E4 cross-phase and final integration obligation; do not claim platform-wide single authority |
| E5-B — shared service model | Core methods for mission, approval, persisted plan/run/progress/evidence/audit/readiness; CLI `workflow_cmd.py` and web `server.py`; `tests/test_workflow_cli.py`, `tests/test_server_workflow_v2.py`, cross-client request parity in `tests/test_workflow_run_requests.py` | Supported V2 requests share the persisted Core authority; complete legacy frontend parity, all advertised features and independent verification are NOT inferred |
| E5-C — reconnect and cancellation | `test_e5_api_client_reconnect_after_server_restart_keeps_durable_identity`, `test_e5_run_snapshot_reconnect_and_lease_secrecy`, `test_e5_cancelled_intent_stays_cancelled_across_api_restart`; paired Docker and systemd smoke | Durable identity and bounded stop semantics supported; HTTP 202 never implies execution success |
| E5-D — adversarial worker safety | `tests/test_engine_v2_e5_process_claims.py` starts two independent Python processes; `tests/test_workflow_continuous_worker.py` kills a child worker; `tests/test_engine_v2_e5_queue_head_recovery.py` exercises poisoned heads and stale leases; `tests/test_engine_v2_e5_state_snapshot.py` checks restored stale claims never replay | Bounded claim, fencing and uncertain-effect tests; no exactly-once guarantee or production external-effect proof |
| E5-E — deployment candidate | `whaxon.service`, `whaxon-workflow-worker.service`, `docker-compose.e5.yml`, `Dockerfile`, `.dockerignore`, `docs/deployment.md`; CI paired-container job and actual Ubuntu systemd-host job use installed wheel and restore offline state | Supported engineering deployment smoke on ephemeral CI host/container. Network/TLS/secrets, production host, independent audit witness and real disaster-recovery acceptance remain OPEN |
| E5-F — exact-head validation | `.github/workflows/ci.yml` Python 3.11–3.13, Ruff, mypy, packaging, headless, cross-platform setup, E1 security, Docker, systemd. [11/11 passing on `11190f737`](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41814000683). New host test passed on `3e5f5fb` but full matrix had a timing-race failure in `test_killed_worker_request_requires_reconciliation_before_replay`; test updated to wait for complete child output on `7c6ba849` | **OPEN until all checks pass on exact final PR HEAD**, after this documentation update |
| E5-G — review and controlled freeze | This register, caller inventory/rollback, offline recovery runbook and limitations; master roadmap and `docs/ENGINEERING_EXECUTION_MODEL.md` remain binding | Await exact-head proof and an explicit dated engineering-review/freeze record. No implied sign-off |

### Explicit release deferrals, never waived

No unapproved real scanner or target execution, no externally retained immutable audit witness in a controlled enterprise environment, no independent production host crash/failover and network service recovery, and no end-to-end parity claim for retained legacy execution surfaces. Those are **not passed**. The engineering smoke is limited to inert unsupported fixture workflows and isolated ephemeral CI runners.

**Merge rule:** mark this PR ready and merge only after documented E5 engineering gates are passed for the supported V2 service scope and exact-final-head CI is green. Even then, E5 engineering freeze **does not authorize production deployment** or close the master roadmap's G01–G10 gates. Keep residual legacy migration assigned to E4/P2 and integrated validation to the final Engine V2 release gate.

## E5 engineering phase-freeze decision — 2026-11-04

**Review source SHA:** `557311dfa12504b22c5d3f32da1f949ac6ae0abd` (all **12/12 GitHub CI jobs successful** in [run #41815823360](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41815823360)).
**Environment:** CI Python 3.11–3.13 + macOS/Windows/Ubuntu setup, Linux headless, Ubuntu systemd supervised real service units installed from a wheel, paired Docker web+worker with a shared volume, approved inert unsupported-capability task, state restoration, E1 security regressions.
**Reviewer:** engineering source/test/evidence reconciliation conducted in the E5 integration workflow; **no independent production-operator approval claimed**.
**Independence boundary:** no independent external security audit or human production-operator authorization was performed by this engineering review; those remain mandatory at final integrated deployment.
**Decision:** E5 engineering scope below is accepted as a **phase-freeze candidate** for the supported V2 durable lifecycle, **subject to final exact-PR-head CI and review/merge record**. The operator's existing E0–E9 phase-freeze policy permits separately recorded residual integrated-engine obligations, not false production readiness.

| Gate | Bounded engineering decision | Residual obligation |
|---|---|---|
| E5-A | Accepted for the single persisted **V2** queue dispatch authority in paired deployment, source-to-client inventory and fail-closed rollback restrictions; no web-owned V2 drainer when external worker enabled | Legacy CLI ToolRunner, web /api/run, AI and Metasploit direct execution **remain**, explicitly not certified as unified authority. P2/E4 caller migration/no-bypass required before **integrated-engine** acceptance; never claim platform-wide single authority |
| E5-B | Accepted for supported Core/CLI/API/headless V2 mission, bounded run, approval, progress, evidence, audit and readiness contracts; cross-client submit-run and durable identity regressions | Full legacy UI/front-end operation-semantic migration and all-capability end-to-end parity remain final integration work |
| E5-C | Accepted for persisted request IDs, client reconnect, server restart, truthful 202, cancellation barrier, blocked worker/no local web fallback | Real network failure and production client deployment testing remain final release work |
| E5-D | Accepted for SQLite atomic claims, two independent worker processes, stale leases, crash injection, poisoned queue, uncertain-effect no-replay, restored stale worker fencing | No exactly-once external effect guarantee; controlled real external-effect and production multi-host recovery remain open |
| E5-E | Accepted for candidate service-mode setup: real Ubuntu CI-host systemd units, Docker two-service process separation, queue/state persistence, offline full-state restore, read-only/least-privilege/container tests | Operator-owned service TLS/identity/secrets, actual supported target host/upgrade, network/storage faults, independent backup witness and production disaster recovery not accepted |
| E5-F | Verified 12/12 at source SHA above, including Ruff, mypy, Python 3.11–3.13, cross-platform setup, packaging, E1 security, Docker and systemd | Exact **final** documentation-only commit must pass the same suite before merge; no waiver |
| E5-G | Engineering review, impact/rollback decision, source/legacy caller inventory, test-to-gate evidence and upstream roadmap reconciliation recorded here and in PR #124 | Independent external security review and operator deployment sign-off remain separate nonwaivable final full-V2 release gates |

**Final staging decision:** The E5 supported V2 durable-service candidate is suitable for a **controlled staging installation** using documented systemd or Docker paths, with only operator-approved inert/sandboxed work. It is **not certified for unrestricted production use or authorized live-scanner operation**. No E6 functionality, G01–G10 release gate, or full Engine V2 deployment gate is accepted here.

**Source-of-truth ordering:** This decision supersedes earlier E5 candidate/OPEN notes within this file for the bounded engineering scope only. The master roadmap still governs final E4 legacy migration, E6 product UI and integrated deployment. The final PR review/merge record must include the documentation-only head SHA and exact-head CI run link and must refuse merge if any check fails.



---


## Source 11: ENGINE_V2_E5_SERVICE_READINESS.md

**Provenance:** [Original source](#source-11-engine_v2_e5_service_readinessmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E5 — Core service readiness and optional integration health

This batch makes `GET /api/health` report **core readiness** separately from
optional Metasploit RPC availability.

- A writable **actual Core data directory** and a successful SQLite `SELECT 1`
  are required for `core_ready: true` and HTTP 200.
- A missing or failing Core database, or an unwritable Core data directory,
  produces `core_ready: false`, `status: degraded` and HTTP 503.
- Metasploit is an optional transport. Its `checks.msf` may be `up`,
  `down` or `unavailable`; a non-up value appears in
  `optional_degraded` but does not alone make the Core unready.
- The writable-directory check uses a unique temporary file in
  `Core.data_dir` and cleans it up. It no longer creates a predictable
  `.healthz` path or probes an unrelated `WHAXON_DATA` fallback.
- Internal errors are not returned verbatim by the health endpoint.

**Limits:** Readiness is a momentary local Core/store check, not proof of a
live dedicated worker, external tool availability, safe network egress,
application authorization, restored backup or complete daemon/container
acceptance. Existing `/api/health/simple` is a separate liveness probe.
The endpoint does not grant any execution permission or alter the supplied UI.

Source: `src/whaxon/interfaces/web/server.py`.

Regressions: `tests/test_engine_v2_e5_core_readiness.py` checks optional
RPC outage, correct data path, SQLite failure, data-path failure, optional
RPC exception and cleanup behavior. Deployment-specific end-to-end health
acceptance remains open under the master roadmap's P2/P3 and E5 gates.



---


## Source 12: ENGINE_V2_E6_CONTRACT_FIRST_ACCEPTANCE.md

**Provenance:** [Original source](#source-12-engine_v2_e6_contract_first_acceptancemd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 E6 — contract-first integration and UI readiness boundary

**Status:** E6 implementation in progress; **NOT engineering-accepted, NOT UI-ready, NOT release-ready**.
**Branch:** `engine-v2/e6-contract-first-integration` (one E6 branch, one phase PR, no partial merge).
**Base:** E5 squash merge `80c3ca566ecdaef1181209fab90fc23184796251`.
**Governing documents:** master roadmap P4/P5 and §38 G01–G10; `ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md`; `ENGINEERING_EXECUTION_MODEL.md`; `UI_CONTROL_INVENTORY.md`.

## Binding boundary: supplied UI is NOT yet ready

Do not redesign, edit, restyle, silently complete, or declare accepted the supplied UI. Keep `web ui files and rendering/` and existing `ui_v2_*.html` source intact. A rendered route, a source script reference, a successful HTTP 200 or a passing API test **does not** certify the UI's visual fidelity, accessibility, control behavior or release readiness. UI completion remains an explicit external dependency. Preserve distinct supplied reference variants, and do not build a substitute interface.

## Parallel workstreams and contracts

| Stream | E6 deliverable independent of unfinished design | Pass condition | State |
|---|---|---|---|
| C1: service truth | Stable read-only API semantics for mission, plan, progress, readiness, findings/evidence, queue summary and reconnect snapshots; reject unknown IDs; do not claim liveness or execution | Exact-SHA tests for truthful unsupported/queued/cancelled/error states without external effects | IN PROGRESS |
| C2: authorization and actions | Cross-client mutation inventory and explicit scope/plan/approval/CSRF/expiry barriers; no UI-only authorization | Negative assertions and no-bypass evidence across API/CLI; no live scanner | OPEN |
| C3: durable client lifecycle | Persist request identity, reconnect URL, cancellation and uncertainty; no per-browser runner | Independent-server restart and API/CLI parity tests; preserve E5 worker fencing | EXISTING E5 CONTRACT, E6 PARITY OPEN |
| C4: evidence and reporting | Verified result versus observed raw output; deterministic report provenance, audit and missing-data disclosure | Seeded controlled workflow with negative/inconclusive cases, repeatable exports | OPEN |
| C5: supplied UI binding | Control-to-service matrix for each actually-visible control, including loading/error/blocked/reconnect/no-data states | Only after final supplied design is ready, visual/accessibility/user acceptance | BLOCKED ON UI |
| C6: release operations | Clean installs, headless/desktop/browser parity, offline and deployment/resource behavior | Supported exact-head CI plus independent G01–G10 acceptance | OPEN |

## Source-backed integration inventory (not acceptance)

- V2 mission and plan APIs: `GET/POST /api/v2/missions`, `GET /api/v2/missions/<id>/plans`, `POST /api/v2/workflows`, `GET /api/v2/workflows/<id>`.
- V2 durable submission: `POST /api/v2/workflows/<id>/run` returns a durable **accepted request** (202), never a guarantee of execution.
- V2 reconnect: `GET /api/v2/workflow-runs/<id>`, `GET /api/v2/workflow-runs/<id>/snapshot`, `GET /api/v2/workflow-runs/summary`, `GET /api/v2/workflows/<id>/progress`.
- V2 control: `POST /api/v2/workflow-runs/<id>/cancel`, plan cancel, approval/revoke, limits, deadlines, rate limits. Each action needs separate authority and negative-test evidence.
- V2 evidence and readiness: `GET /api/v2/workflows/<id>/readiness`, `/audit`, `/evidence`, `/reconciliation`, `/events`, `/attempts`. These surfaces do not themselves demonstrate truthful complete reports.
- 22 supplied production template files with the existing static inventory of 793 controls. The inventory marks static unresolved and script-reference-only controls; no runtime acceptance implied.

## Initial E6 preflight checks

`tests/test_engine_v2_e6_contract_preflight.py` checks that a distinct web instance can inspect a durable queued request without executing it, that status, snapshot and queue views never present a queued request as completed or a live worker as verified, and that unknown requests are rejected. Uses an inert unsupported fixture address in the reserved TEST-NET-1 range and `WHAXON_V2_EXTERNAL_WORKER=1`. **No new UI**, no scanner, no external target or new runtime authority.

## E6 acceptance blockers

1. Finish supported API/CLI/desktop parity and test all exposed mutation authority boundaries; reconcile E4/P2 legacy direct-execution exceptions.
2. Finish deterministic findings, verification, evidence, coverage and reports in one controlled end-to-end solo workflow.
3. When design is declared ready, reconcile every visible control against a real endpoint, permissions, states and error behavior without altering the supplied design.
4. Verify pixel/responsive fidelity, focus/keyboard/assistive-tech behavior, external assets and environment parity against approved design evidence.
5. Execute, evidence and sign off G01–G10; preserve production external audit-anchor and live authorized lab requirements.

**Gate rule:** E6 stays OPEN until applicable supported engineering checks and documented phase decision succeed; production/full V2 deployment acceptance remains separately OPEN even after engineering freeze. No percentage based solely on pages, test count or source presence.



---


## Source 13: ENGINE_V2_E6_DEPLOYMENT_GATE_LEDGER.md

**Provenance:** [Original source](#source-13-engine_v2_e6_deployment_gate_ledgermd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### E6 deployment acceptance ledger — non-waivable release gates

**Review:** 2026-11-05. **Candidate:** E6 PR #125, starting at E5 main `80c3ca566ecdaef1181209fab90fc23184796251`.
**Decision:** **NOT DEPLOYMENT-READY.** The new supplied UI is unfinished; no operator security authorization or production lab evidence has been supplied.
This register follows master-roadmap §38 G01–G10 and E0–E9 phase-freeze policy. Historical tests are sources for verification candidates, not automatic acceptance. Do not equate E5 engineering freeze with full V2 production approval.

| Gate | Candidate evidence already available | Specific unpassed obligation | Current decision |
|---|---|---|---|
| G01 — capability/workflow | Existing Core plus `ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md`: catalog/transport map, all 104 Flask API method/path/handler bindings, consequential route and deployment/readiness crosswalk, guarded direct-dispatch inventory; UI controls remain separately frozen | Complete capability/transport/client/test semantics and controlled full solo chain | OPEN |
| G02 — authorization/execution | E1 regression suite and `test_engine_v2_e6_mutation_guards.py` candidate | Authorized target/pivot/redirect/secondary DNS and legacy direct-dispatch no-bypass lab; UI cannot grant permissions | OPEN |
| G03 — independent verification | Existing validator and retest tests | End-to-end replay/verification and conservative inconclusive/failure outcomes with retained proof | OPEN |
| G04 — evidence/coverage/report | E3 audit and evidence seals, E6 empty-evidence parity candidate | Reproducible complete report, redaction, missing/skipped coverage, independent trust anchor, audit fault recovery | OPEN |
| G05 — durable lifecycle | E5 bounded freeze and 12/12 exact-head pre/post merge CI; E6 cross-client tests candidate | Full retained legacy CLI/API/web/UI/no-bypass integration and realistic host/network effect failure cases | OPEN |
| G06 — supplied UI | 22 templates/793 source controls registry | **Blocked: new UI not ready**. Approved visual design, all live controls, keyboard/accessibility/responsive and parity | BLOCKED: UI |
| G07 — install/deployment | E5 staging Docker/systemd smoke and offline snapshots | Supported target host/upgrade, TLS/secrets, external witness, storage/network outage, backup retention and recovery | OPEN |
| G08 — release CI | E5 merge run and E6 PR CI candidate | Exact final E6 release candidate across Python versions, browsers, supported OS and required test environments | OPEN |
| G09 — release identity | Existing beta version and package workflow | Approved release version/tag, reproducible artifact/checksums, release workflow and intended index publication | OPEN |
| G10 — documentation/decision | This ledger and E6 contract matrix | Reconciled current crosswalk, operator deployment/security approval, accepted evidence links, final release decision | OPEN |


## G01 acceptance status — 2026-11-05

G01 is **IN PROGRESS and OPEN** on main baseline `b12470d6708ab658fd86195b9e8bc2f445e74bfe`. The G01 integration candidate is PR [#132](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/132). Its first batch reconciles direct ToolRunner calls, recon/validation/retest/MSF service paths, packaged catalog IDs/transports, V2 provider admission, semantic operation aliases, declared target types, and client ownership in `docs/ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md`. A regression guard pins catalog transports and the V2-admitted capability/target map. The stale `whatweb` provider-admission declaration was removed because no packaged catalog entry exists.

A read-only local portfolio audit recorded 24 catalog entries, 26 discovered adapters, 12 V2-bound catalog tools, 12 unsupported catalog entries, four adapter-only integrations, and zero executable providers in that audit environment. None of the admitted providers was smoke-tested, lab-validated, or end-to-end-verified there. This is environment-specific evidence; it is not a target-host readiness claim.

**G01 is not ready to freeze.** The required controlled full solo chain has not been executed, and the current V2 provider set has no admitted initial-access capability. A bounded SQLi verification/retest subset is now scheduler-owned, but other validation paths remain uncovered and the new provider has not been lab-validated. Keep G01 open until the full chain and all required evidence pass. Do not start the next gate or mark this gate frozen before that acceptance record exists.

### G01 candidate update — 2026-11-05

Candidate based on `c4356c712c200834ecd4694befa15a31c28c25a9` adds exact
catalog/admission/transport and semantic-operation crosswalk guards, all 22
UI page handlers and 23 route aliases, and a loopback-only SQLi smoke. The
current working candidate also adds scheduler-owned SQLi verification and
conservative retest tasks for sealed, same-target V2 findings. The HTTP
requests recheck scope immediately before dispatch, reject redirects and
path changes, and accept IP literals only to prevent DNS rebinding. Results
are written to separate V2 evidence jobs. This remains a narrow SQLi subset:
XSS, timing, and observation validation are not integrated, each operation is
a separate plan, and no initial-access capability or controlled full-chain
proof exists.

Local focused results: **255** G01 tests pass across capability serialization,
provider/workflow, API/CLI, callsite inventory, and Burp import. Ruff, Python
compilation, and `git diff --check` pass. The API now serializes nested
capability-schema arrays as JSON arrays while retaining immutable manifests.
Scanner-backed smoke and exact-head CI are not yet available on this candidate. G01 remains
**OPEN** and unfrozen; the full controlled chain is still unproven.

## Engineering delivery tracks that can proceed while UI is blocked

1. **C1/C3**: enforce Core/API/CLI durable status and cancellation parity, no browser-owned drainer, no implicit success.
2. **C2**: adversarial authorization/consent/policy and legacy-bypass audit; negative tests independent of UI.
3. **C4**: deterministic observed-versus-verified evidence, coverage, report provenance and failure/recovery.
4. **C6**: isolated headless, wheel, systemd, Docker, off-host backup witness and fault-injection on approved inert fixtures.
5. **C5 (blocked)**: no editing of UI design until it is ready; later build per-control checks against approved variants.

## Gate closeout format

Every gate requires: exact final commit SHA, affected requirement IDs, exact test assertion, supported runner/environment, CI or lab run link, operator authorization for real targets where required, expected/observed results, retained evidence location, limitations, reviewer and decision. Unknown, skipped, unexecuted, draft or stale checks **do not pass**. Only the operator may authorize production deployment.

**Safe candidate:** bounded E5 headless engineering staging with inert approved inputs only; E6 has no full deployment sign-off.



---


## Source 14: ENGINE_V2_E6_SERVICE_UI_HANDOFF_MATRIX.md

**Provenance:** [Original source](#source-14-engine_v2_e6_service_ui_handoff_matrixmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### E6 service-to-UI handoff matrix — backend evidence only

**Date:** 2026-11-05. **Status:** candidate contract inventory, NOT UI acceptance.
**UI owner dependency:** final supplied UI design **not ready**. This matrix is an integration handoff specification, *not* an instruction to change templates. Zero redesign; preserve supplied references and existing templates. Never mark a static control accepted because its route exists.

## Existing APIs and consumer contracts

| Consumer concern | Current V2 service path | Evidence location | Required semantics for future UI | Open validation |
|---|---|---|---|---|
| Mission list/create | `GET/POST /api/v2/missions` | `tests/test_server_workflow_v2.py` | No phantom missions, error on invalid input, authentication and scope | Complete real-client behavior |
| Plans and detailed task state | `GET /api/v2/missions/<mission_id>/plans`, `GET /api/v2/workflows/<plan_id>` | `tests/test_server_workflow_v2.py` | Persisted identifiers, 404 on unknown, distinguish blocked from succeeded | Full visual mapping |
| Durable start | `POST /api/v2/workflows/<plan_id>/run` | `tests/test_workflow_run_requests.py` | HTTP 202 means accepted/queued only; reconnect URL, no automatic success | Human consent and actual tool lab |
| Run status and snapshot | `GET /api/v2/workflow-runs/<id>`, `/<id>/snapshot` | `tests/test_engine_v2_e6_contract_preflight.py`, `tests/test_engine_v2_e6_client_parity.py` | Persisted request, no private lease token, no assumed worker liveness, uncertain state visible | Browser lifecycle |
| Queue summary | `GET /api/v2/workflow-runs/summary` | `tests/test_workflow_run_requests.py` | Read-only counts, not worker liveness proof | Empty/error/offline behavior |
| Cancel intent | `POST /api/v2/workflow-runs/<id>/cancel`, `POST /api/v2/workflows/<plan_id>/cancel` | `tests/test_engine_v2_e6_client_parity.py`, `tests/test_server_workflow_v2.py` | Request-level stop barrier; never imply external effect already stopped | Browser confirmation/reconciliation |
| Workflow progress/events | `GET /api/v2/workflows/<id>/progress`, `/events`, `/attempts` | `tests/test_server_workflow_v2.py` | Distinguish queued, blocked, failed, uncertain and actual verified evidence | Event polling/reconnect proof |
| Approval and revoke | `GET/POST /api/v2/workflows/<id>/approvals`, `POST /api/v2/workflows/<id>/approvals/<approval_id>/revoke` | `tests/test_server_workflow_v2.py` | No implicit approval; server enforces exact scope/actor/expiry and change of plan | Cross-client adversarial approval lab |
| Budget/deadline/rate | `/api/v2/workflows/<id>/limits`, `/deadline`, `/rate-limit` and mission-level bounds | `tests/test_server_workflow_v2.py` | Tightening and fail-closed invalid settings, one server-side authority | Negative/migration matrix |
| Evidence and audit | `GET /api/v2/workflows/<id>/evidence`, `/audit`, `/reconciliation` | `tests/test_server_workflow_v2.py` | Report raw/observed versus independently verified; disclose broken seals and uncertainty | Final report reproducibility and external witness |
| Readiness | `GET /api/v2/workflows/<id>/readiness` | `tests/test_engine_v2_e6_client_parity.py` | Never infer success from queue completion or HTTP 200 | Full solo lab acceptance |

## Explicitly unresolved legacy paths

Existing legacy `/api/run`, `/api/ai/run`, Metasploit and CLI direct execution remain separate from V2 queue authority. The E5 freeze did **not** migrate them. E6 must consume the P2/E4 caller migration/no-bypass results rather than add another UI-side execution path. Do not delete compatibility code before migration and rollback checks.

## Future visual-control acceptance protocol (not yet executable)

When the new design is formally ready, map each visible control to an approved reference variant, exact endpoint and input, backend authorization, response schema, loading/error/blocked/empty/offline/reconnect/cancel states and specific test. Preserve all existing design inputs. Test keyboard focus/semantic labels, responsive behavior and assistive technologies; compare approved screenshots and external-asset behavior across supported environments. Count accepted controls only after test evidence at an exact commit, not static source references.

### Review boundaries

1. E6 backend test additions can run while UI is incomplete. **No claimed UI progress** results from their success.
2. API/CLI parity is narrower than UI or full product parity.
3. E6 and G01–G10 release gates remain open; no real scanner, live unauthorized target or production trust anchor was exercised.
4. Keep the existing one-E6-branch/one-PR model; document regressions and exact-head CI before any freeze.



---

# Part III — Baselines, current-head audits, evidence mapping and provider capabilities



## Source 2: ENGINE_V2_BASELINE_INVENTORY.md

**Provenance:** [Original source](#source-2-engine_v2_baseline_inventorymd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine v2 — E0 Repository Baseline & Execution-Path Inventory

**Review date:** 2026-11-01  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Branch / baseline:** `main` at `2263477b1a79c384bcadb1cc22fc032e38d0c745`  
**Architecture authority:** `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md`  
**Roadmap authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, §0 and §49  
**Review type:** Static source, test, configuration and repository-tree inspection. No runtime tests were executed in this inventory pass. No runtime code was changed.

> **Historical baseline (2026-11-01).** This is a point-in-time E0 inventory at the commit above. Its statements that Engine v2 contracts, scheduler, mission persistence or leases do not exist are superseded by the dated implementation update in master roadmap §49 and the current [Engine v2 crosswalk](#source-2-engine_v2_baseline_inventorymd). Use this file only to understand the migration starting point, not current implementation status.

## 1. Executive result

The repository has a substantial and useful execution foundation, but the current system is not yet a general-purpose, capability-driven mission engine. It is a composition of a low-level tool runner, a durable-but-minimal pending-job queue, event subscribers, a deterministic single-rule Automator, and a separate sequential AI action loop.

**Decision:** evolve the existing core behind stable application-service boundaries. Do not replace the runner, adapters, parsers, scope manager, SQLite store or event contracts wholesale. Add a mission/task-graph layer, typed capability/provider contracts, independent policy/approval services and a real durable scheduler. Migrate the existing paths incrementally and preserve their tested behavior.

### High-confidence current state

- The main execution path is traceable from CLI/web/AI into `Core`, `ToolRunner`, the event bus and SQLite persistence.
- Local process execution uses argument arrays through `create_subprocess_exec`, with process-group termination and output caps.
- Scope enforcement has strict defaults, DNS resolution checks, out-of-scope precedence and auditable CLI overrides.
- Existing adapter parsers and the catalog provide a reasonable migration base, but their contracts are tool-centric rather than capability-centric.
- Auto-chain jobs survive process exit as SQLite pending rows and are claimed atomically.
- AI is structurally separated from core execution: it proposes typed `Action` objects, while an executor validates them.
- Customer engagement execution, bug-bounty policy evaluation, and AI approvals are not yet unified under the target authorization model.
- There is no persisted mission/plan/task graph, scheduler lease model, budget ledger, durable event log/outbox, or plan-digest approval contract in the inspected schema.

## 2. Repository inventory

The recursive Git tree at the baseline contained 621 file paths and was not truncated. Relevant source areas include:

| Area | Existing implementation |
|---|---|
| Core execution | `core/runner.py`, `core/worker.py`, `core/automation.py`, `core/events.py` |
| Persistence | `core/store.py` (SQLite) |
| Tool discovery | `core/catalog.py`, packaged `data/tools.json` |
| Adapter integration | `adapters/base.py`, `adapters/registry.py`, per-tool adapters |
| AI planning | `ai/actions.py`, `ai/agent.py`, provider implementations |
| AI execution gate | `ai/executor.py`, `core/ai_bridge.py` |
| Scope / authorization | `core/scope.py`, `core/override_log.py`, `core/program_policy.py` |
| Session / pivot | `core/msf.py`, `core/msf_tracker.py`, `core/routes.py`, `core/pivot.py`, `core/portfwd.py`, session adapters |
| Findings / verification | `core/findings.py`, `core/correlator.py`, `core/validator.py`, `core/reproduce.py` |
| Recon / enrichment | `core/recon.py`, `core/recon_checks.py`, `core/suggester.py` |
| Interfaces | CLI, Flask web server, GUI and TUI |
| Setup / readiness | `core/dependencies.py`, `core/dependency_jobs.py`, installer and setup modules |

The packaged tool catalog currently contains 24 entries: 16 local CLI tools and 8 session-transport entries (MSF, SSH, SMB and WMI). The adapter registry autoloads built-ins and supports Python entry points. These are valuable provider foundations, but the catalog's `Tool` record currently describes executable details and transport, not a complete capability contract.

## 3. Current end-to-end execution paths

### 3.1 Direct CLI tool execution

`whaxon run` → construct `Core` → `Core.initialize(drain=False)` → `ToolRunner.run_tool` → scope check → catalog lookup / argv construction → `ToolRunner.run` → subprocess → typed job events → SQLite store → adapter parse / fallback parser → findings events → correlator, suggester and Automator.

The CLI captures pending IDs before its primary run, yields to event subscribers, and calls `drain_async` excluding work that was already pending. This ensures it drains follow-up work created by the current run without unexpectedly executing old pending work. Regression coverage exists in `tests/test_run_cmd.py`.

### 3.2 Durable follow-up execution

`JobFindings` → `Automator._on_findings` → detect Nmap `open_port` findings for a fixed HTTP service/port list → check Nikto presence and recent history → `jobs.status='pending'` row → worker `claim_pending` → `ToolRunner.run_tool`.

The worker claims one row at a time and drains serially, with a default maximum of 50 jobs per invocation. The durable queue is a good stepping stone, but it is not yet a task graph or a general workflow scheduler.

### 3.3 Long-lived interface execution

The Flask server exposes run APIs and uses an `AsyncRunner` background thread/event loop to execute jobs. Web routes perform their own fail-closed scope check and reject free-form extra arguments. `Core.initialize(drain=True)` reconciles stale jobs and drains pending work at initialization. GUI/TUI and other interfaces share `Core` and runner services to varying degrees; interface-level ownership and lifecycle need a complete integration audit during E5.

### 3.4 AI execution

AI provider → `Agent.next_action` → one typed `Action` proposal → `Executor` → catalog lookup, target lock, scope check, duplicate-action check and session checks → injected runner callable → persisted AI step/history.

This planner/executor split is worth preserving. The limitation is that the planner emits one action at a time and the executor serially executes it. It cannot compile, validate, approve, schedule, checkpoint or recover a versioned DAG. `ExecutorLimits.max_wall_seconds` is declared but is not enforced in the inspected `Executor.run` loop.

### 3.5 Bug-bounty path

The program-policy loader validates a policy document and resolves a host to one matching program. The CLI checks tool allow/deny policy, then explicitly prints that dispatch is not wired in v1. The program-policy gate is therefore not yet a full campaign execution service. It must remain separate from customer-engagement policy when dispatch is implemented.

### 3.6 Session execution

The runner currently supports MSF, SSH, SMB and WMI session transports. Session state is observed by `MSFTracker` and stored in SQLite. SSH/SMB/WMI transport helpers extract a host and perform a scope check. The MSF session execution path checks that the session exists and optionally matches a required session type, but the inspected `run_in_session` / `_run_msf_session` path does not re-check the stored session host against engagement scope immediately before execution. The AI session executor checks liveness but does not bind the session host to its target lock. This boundary must be fixed before autonomous session chaining.

## 4. Persistence and event model

### 4.1 Existing SQLite tables

The inspected schema contains:

- `jobs`: job ID, tool, target, status, exit/error, start/finish and duration.
- `lines`: ordered stdout/stderr lines.
- `findings`: normalized finding fields, raw line, enrichment JSON and verification status.
- `coverage`: skipped/blocked coverage records.
- `sessions`: session identity, host/type, info and lifecycle timestamps.
- `evidence`: evidence kind/name/path/note and timestamp.
- `ai_runs`, `ai_run_steps`, `approvals`: sequential AI run history and human answers.

SQLite WAL and synchronous=NORMAL are enabled. Existing migrations add columns idempotently.

### 4.2 Missing engine-level persistence

No tables/contracts were found for Mission, Plan, Task, TaskAttempt, capability/provider manifest snapshots, policy decisions, plan-bound approvals, worker leases/heartbeats, budget reservations/consumption, durable event/outbox records, independent verification runs, or immutable evidence metadata/content hashes.

The current `evidence` table stores path-oriented references; it is not yet the architecture's content-addressed evidence vault. The current audit trail is distributed across job rows, AI steps, override log and operational logs rather than one causally linked, tamper-evident event history.

### 4.3 Queue and recovery limitations

- `claim_pending` atomically changes a pending row to running, but there is no lease owner, lease token, heartbeat or expiry.
- `reconcile_stale` marks every running row older than 60 seconds failed. It cannot distinguish a dead worker from a legitimate long-running job owned by another process. A second process starting while a scan runs longer than the threshold can therefore misclassify that active job.
- Recovery changes the job to failed; it does not reconcile uncertain external side effects before retry.
- There is no retry policy, backoff, attempt history, idempotency key, per-mission/target concurrency, fairness, priority or resource budget.
- Drains are serial and bounded by a count, not a scheduler with a worker pool.
- Some initialization paths catch and ignore recovery/drain exceptions. That can conceal a failed recovery step from operators.
- The event bus is in-process pub/sub. It does not persist events, provide durable consumer offsets, or use an outbox to atomically couple state changes and event publication.

**Priority:** replace stale-age-only recovery with explicit worker leases and heartbeats before enabling multiple independent workers or headless multi-process operation.

## 5. Capability and adapter model

### What exists
- `ToolCatalog` loads a JSON catalog and checks local binary availability.
- The `Tool` dataclass includes binary, args template, package, transport, command, required session type and pivot capability.
- `Adapter` defines parsing and optional next-step/remediation/impact/CVSS hooks.
- Registry autoloads built-in adapters and discovers third-party Python entry points.
- `Suggester` exposes adapter-suggested next steps.
- Existing parser output is normalized into `Finding` objects and retained with raw lines.

### What is missing
- Stable capability IDs independent of tool names.
- Versioned input/output schemas and compatibility rules.
- Explicit target/protocol/platform/auth support and prerequisites.
- Permission and side-effect/impact classifications.
- Transport requirements and credential reference contracts.
- Timeout, cancellation, retry, idempotency and reconciliation declarations.
- Resource/rate/concurrency requirements.
- Evidence format and parser/normalizer version declarations.
- Readiness levels beyond a local binary-available boolean.
- Deterministic provider resolution and explainable fallback selection.

**Migration decision:** keep existing `Tool` and adapter interfaces behind a compatibility bridge initially. Add manifests and validate their truthfulness; do not rewrite parsers just to fit the new architecture.

## 6. Authorization and safety boundaries

### Existing strengths
- Scope defaults to a restrictive local/private-network allowlist.
- Malformed scope files and failed hostname resolution are rejected.
- Out-of-scope rules override in-scope rules.
- Hostnames are checked against resolved addresses, requiring all answers to satisfy scope.
- CLI overrides are explicit and logged; web tool-run routes reject out-of-scope targets and do not trust client-supplied override flags.
- Runner uses `create_subprocess_exec`, not a shell command string, and rejects common alternate-target flags/arguments.
- AI tool actions are catalog-checked and scope-checked; free-form AI extra arguments are rejected for ordinary tool execution.
- Bounty policy loading rejects missing/ambiguous matching policy and has a separate tool allow/deny check.

### Gaps requiring design/implementation

1. **DNS time-of-check/time-of-use:** scope resolves a hostname, but the external tool later resolves it independently. Pinning or enforcing the authorized resolved-address set at the actual network boundary is not yet provided by the generic runner.
2. **MSF session host binding:** session liveness/type is checked, but host-to-scope/target-lock revalidation is absent in the inspected MSF execution path.
3. **Pivot destination policy:** the runner can rewrite a pivot-capable tool's target to a local forwarded port after checking the original target. Route identity, pivot chain and authorization context need to be explicit and revalidated.
4. **Approval binding:** AI `ask_human` answers are associated with a run/sequence, not an immutable plan digest, target/parameters, impact, budgets, policy version and expiry. This is an interaction checkpoint, not the Engine v2 approval contract.
5. **Bounty policy semantics:** the current loader validates a subset of fields and the CLI gate does not dispatch. Source freshness, activation, exclusions, techniques, time windows, rate/impact limits and authorization decisions need their own validated contract.
6. **Explicit scope disable:** the operator can set `enabled:false`, which intentionally makes every target pass the scope manager. Preserve this as an explicit configuration capability only if the future policy model clearly labels and constrains it; it must never be an implicit fallback.
7. **Session command contracts:** session tools can represent remote commands. They need typed command/input schemas, transport-specific escaping and impact classification; do not treat a session command as an ordinary local tool invocation.

## 7. Findings, evidence and verification

Existing strengths:
- Raw stdout/stderr lines are persisted with sequence numbers (runner caps capture at 5,000 lines / 1 MB and caps individual lines).
- Adapters parse rich tool-specific findings; a legacy parser fallback exists.
- Findings retain source, raw line, data and enrichment, including request context.
- Verification states are persisted and validators conservatively keep unsupported/incomplete evidence as candidate.
- CoverageSkipped events are persisted.
- The validator has curated non-destructive HTTP probes and distinguishes candidate from verified.

Gaps:
- Evidence artifacts do not yet have content-addressed identity, cryptographic integrity, provenance chain, access/tenant boundary, redaction metadata and retention policy in the core schema.
- A job's terminal exit code and parsed findings are not a sufficient semantic task outcome contract.
- Verification is not yet represented as a first-class durable task/run with method, authorization snapshot, limitations and linked evidence.
- Coverage is currently mainly skip records; it does not represent planned/approved/attempted/completed/verified/inconclusive/blocked/skipped/untested graph nodes.
- Parser exceptions are caught and parsing can fall back to legacy logic; parser failure/partial parse needs explicit machine-readable outcomes while preserving raw output.

## 8. Current tests and verification posture

The repository has focused regression tests for:
- Runner argv construction, scope, subprocess output, timeout and cancellation.
- Durable pending rows, atomic single claims, stale recovery and process-separated queue/drain.
- CLI auto-draining newly created follow-ups while preserving older pending jobs.
- Scope malformed-config and DNS fail-closed cases.
- AI/core import boundary, unknown-tool rejection, out-of-scope rejection and session action checks.
- Approval storage/API behavior.
- Bounty policy validation and allow/deny checks.
- Adapter parsing, findings, verification, web routes and UI behavior.

Two previous reported defects are already represented as fixed in current source:
- `run_cmd.py` drains follow-ups generated by the initial CLI run; `tests/test_run_cmd.py` includes `test_run_automatically_drains_jobs_queued_by_automator`.
- `adapters/nikto.py` strips bracketed Nikto IDs and `See:` suffixes while parsing; this must remain protected by parser fixtures/regressions.

CI configuration declares Python 3.11/3.12/3.13, Ruff, mypy, full pytest, package build/metadata checks, wheel smoke tests and setup smoke across Ubuntu/macOS/Windows. **This E0 review did not execute the test suite or verify the latest remote CI run.** Current test and CI health must be established at the start of E1, not inferred from the workflow definition.

## 9. Prioritized gap register

| ID | Priority | Gap | Required response |
|---|---|---|---|
| E0-01 | Critical | Stale-age-only job recovery can misclassify a live long-running worker | Lease owner/token, heartbeat, expiry and safe reconciliation |
| E0-02 | Critical | Session host/target-lock scope binding incomplete for MSF | Revalidate session identity and host authorization at dispatch |
| E0-03 | Critical | DNS authorization can diverge from address used by external tool | Authorized resolution pinning/network-boundary enforcement and redirect checks |
| E0-04 | Critical | Approval is not bound to exact immutable plan/action | Digest-bound, expiring, revocable approvals |
| E0-05 | High | No persisted mission/plan/task/attempt graph | Versioned domain contracts and migration-safe schema |
| E0-06 | High | No generalized capability manifests/provider resolver | Capability IDs, typed I/O, compatibility and readiness metadata |
| E0-07 | High | Hard-coded Nmap→Nikto Automator | Declarative evidence/capability follow-up policies |
| E0-08 | High | No durable scheduler/worker leases, budgets, retry reconciliation or cancellation state | Durable scheduler with bounded concurrency and attempt ledger |
| E0-09 | High | Event bus is process-local and has no durable outbox | Schema-versioned events, transactional outbox and consumer cursors |
| E0-10 | High | Bounty policy validates but does not dispatch and is not an independent execution service | Separate bounty policy/mission lifecycle and activation/expiry checks |
| E0-11 | High | AI emits sequential single actions; wall-clock limit not enforced | Typed DAG proposals, compiler and enforced mission/task budgets |
| E0-12 | High | Evidence/audit lacks content integrity and causal provenance | Evidence vault, provenance graph and tamper-evident audit |
| E0-13 | Medium | Capability readiness is binary availability only | Dependency/readiness snapshots and verified capability states |
| E0-14 | Medium | Session/SSH/SMB/WMI transport contracts differ and are partly embedded in runner | Typed transport adapters and transport-specific lifecycle/security |
| E0-15 | Medium | Interfaces own different execution lifecycle details | Shared application services; CLI/web/UI/headless become clients |
| E0-16 | Medium | No comprehensive multi-target fan-out/fan-in, per-target isolation and aggregation | Bounded graph primitives and partial-failure semantics |

Critical here means a prerequisite to safe autonomous or multi-worker operation, not necessarily a blocker to current supervised local use.

## 10. What to preserve, wrap or replace

| Component | Decision | Reason |
|---|---|---|
| `ToolRunner` subprocess and output handling | Preserve and narrow | Strong low-level execution foundation; remove orchestration responsibilities over time |
| `build_argv` target-override protections | Preserve and expand tests | Important security boundary |
| Existing adapter parsers | Preserve | Domain knowledge and evidence parsing are valuable |
| `ToolCatalog` | Wrap with capability manifests | Current tool records are too implementation-specific |
| Adapter registry / entry points | Preserve behind trusted provider registration | Useful extensibility point; plugin trust/readiness must be explicit |
| `ScopeManager` | Preserve as one policy primitive; strengthen dispatch binding | Existing fail-closed behavior is useful but not a full engagement policy |
| `ProgramPolicy` | Evolve into separate bounty authorization domain | Current CLI is validation-only and incomplete for dispatch |
| `EventBus` | Preserve for local notifications; add durable event/outbox layer | In-process bus is not a workflow source of truth |
| `JobStore` | Migrate with additive/versioned schema | Existing operational history should remain readable |
| `worker.py` | Replace scheduler semantics; retain worker execution adapter | No lease/heartbeat/attempt model |
| `Automator` | Replace with declarative graph transitions | Fixed Nmap→Nikto branch cannot scale |
| `Agent` / providers | Preserve planner isolation; change output to typed plan proposal | AI must remain a proposer, not an authority |
| `Executor` | Replace sequential loop with graph compiler/orchestrator integration | Current one-action loop cannot represent workflows |
| CLI/web/UI/GUI/TUI | Keep as clients; migrate behind shared services | Avoid duplicate business logic and interface-owned job lifecycle |
| Validator / finding model | Preserve and evolve into verification/evidence contracts | Existing conservative verification is a foundation |

## 11. Implementation order derived from the baseline

This is the Engine-specific sequence, subordinate to roadmap §0 and all UI/release gates:

1. **E1 — Close and regression-protect correctness/security defects.** Fix the lease/recovery hazard before enabling concurrent workers; close session-host authorization and DNS/pivot boundary gaps; verify current Nikto and CLI drain behavior; test all failure paths. No broad refactor.
2. **E2 — Establish domain contracts and compatibility façade.** Introduce schema-versioned mission, authorization context, plan, task, attempt, manifest, provider, policy decision, approval, budget, execution context, observation, verification, evidence, audit and readiness models. Preserve current clients through a façade.
3. **E3 — Durable scheduler and state machine.** Add leases/heartbeats, attempts, idempotency/reconciliation, transactional state/events, bounded worker pools, cancellation, deadlines and budget accounting. Do not add multi-worker dispatch until lease/recovery tests pass.
4. **E4 — Capability migration.** Generate truthful manifests for current catalog entries and adapters. Resolve providers deterministically. Prove a new provider can be added without scheduler code changes. Convert Nmap→Nikto to a declarative rule and preserve current behavior.
5. **E5 — Shared application services and headless runtime.** Route CLI/web and later supplied UI through shared mission/task services. Support daemon lifecycle, health/readiness, restart and job continuation with no browser/TUI dependency.
6. **E6 — Solo v1.0 and supplied UI acceptance.** Respect the UI-first roadmap gate, exact supplied UI design and real backend functionality.
7. **E7 — Autonomous campaigns and bounty.** Introduce bounded autonomy only after customer/bounty policy isolation, exact approvals, evidence and recovery pass adversarial tests.
8. **E8/E9 — Multi-target and selective future transports/platforms.** Add fan-out, cloud/API/browser/code/container and team/enterprise extensions only against measured requirements and explicit acceptance.

## 12. E0 exit and limitations

**E0 static inventory is complete for the principal execution, persistence, provider, AI, scope, session, bounty, findings and CI paths listed above.** It is not a claim that every file in the 621-path repository has been manually audited. The remaining detailed call-site and adversarial review belongs to E1 before runtime changes.

Not performed in this pass:
- No local checkout or runtime test execution.
- No latest GitHub Actions run inspection.
- No exhaustive review of every web endpoint, UI page, individual adapter parser or all external-tool behavior.
- No live target or external tool execution.
- No schema migration or runtime code change.

The next code work should begin with E1's critical security/recovery defects and regression tests, not by introducing the DAG engine on top of unsafe multi-process recovery.


## E0 supplemental finding — Metasploit capability underuse and Armitage workflow gap

The baseline review identified a narrow Metasploit integration: basic RPC connectivity, a limited exploit/auxiliary/post adapter, console-based module launch, simple session command execution, polling, a fixed post-module auto-chain and partial pivot/port-forward support. This is not equivalent to exposing the Framework's supported capabilities.

The research crosswalk identifies the broader Framework surface: module discovery and metadata, option/target/payload compatibility, job lifecycle, consoles, sessions, payloads and handlers, plugin APIs, database records, Meterpreter capabilities and route-aware operation. The exact surface is version- and edition-dependent and must be discovered at runtime.

Armitage provides useful workflow precedents missing from WHAXON's current integration: attack-surface/session visualization, host/service-driven attack candidate discovery ("Find Attacks"), contextual session operations, pivot-aware network view and shared-session deconfliction. These are patterns to incorporate into WHAXON's existing engine and supplied UI—not a reason to add a separate UI or runtime dependency.

This is a static architecture/research finding, not runtime validation of every RPC method or a live Framework instance. Detailed requirements, source references, security decisions and acceptance tests are in `docs/METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md`.



---

## E0 supplemental finding — Tool Intelligence and onboarding gap

The repository has a catalog, adapter base contract, adapter registry/entry-point discovery and provider/transport integrations. These are useful extension points, but they do not constitute an end-to-end tool intelligence function.

The current design lacks one source-backed workflow to reconcile catalog entries, adapters, transports and dispatch paths; discover upstream capabilities; research candidate tools; compare upstream support with WHAXON implementation and verification; and produce an auditable, operator-reviewed onboarding proposal. Preliminary inspection also identified catalog/adapter inventory discrepancies. The exact complete mismatch set must be established by E4 reconciliation rather than inferred from catalog size.

No general candidate research/onboarding service, versioned capability report lifecycle or continuous upstream-delta assessment was identified in the reviewed baseline. Python entry points provide adapter discovery, not trust, compatibility, capability completeness or permission. Binary availability is not capability readiness.

**Required response:** implement roadmap §52 and docs/TOOL_INTELLIGENCE_AND_ONBOARDING.md using Engine v2 manifest, registry, readiness, scheduler, policy and evidence contracts. Keep discovery read-only and bounded; no auto-install, upgrade, plugin loading, credential use or operational execution. Define contracts in E2 and perform portfolio reconciliation/local discovery/gap analysis in E4, after E1 blockers and without disrupting the compatibility bridge.

This is an architecture/static inventory finding, not a claim that the proposed service already exists or that every repository file has been exhaustively audited.



---


## Source 3: ENGINE_V2_CODE_VS_ROADMAP_AUDIT_2026-11-03.md

**Provenance:** [Original source](#source-3-engine_v2_code_vs_roadmap_audit_2026-11-03md) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 — source versus roadmap audit (2026-11-03)

> **Later main reconciliation:** See [Current-head reconciliation](#current-head-reconciliation--2026-11-03-newer-than-the-audit-above) below: `f0b25d3629d776b433f72c83db679bb41313c812`, **33/48 (68.75%)** sampled source coverage. Original **25/40** is a preserved historical comparison, not a current engine-completion percentage.

**Audited main commit:** `781246b87575f6a7e5f7eea22e63aad789428894` (semantic provider migration, durable provenance and portfolio reconciliation).
**Authority:** master product roadmap §§0, 38, 49; `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md` §14; `docs/ENGINE_V2_ROADMAP_REQUIREMENTS.csv`.
**Method:** parallel read-only inspection of main Git tree, selected source, named test definitions, documentation and GitHub Actions check-runs. **No local tests, deployment, UI/browser acceptance or external-effect crash lab were executed for this audit.** GitHub check-runs for the exact inspected head were **9/9 successful**, including the three Python-version jobs and setup/headless jobs. A successful CI check is not universal acceptance.

## Three different metrics — never interchange them

- The pre-existing requirements index contains **75 source-level entries**, with **42/75 (56.0%)** linked to candidate implementation/document artifacts and **68/75 (90.7%)** linked to candidate tests, as recorded in `docs/ENGINE_V2_EVIDENCE_MATRIX.md`. Those are *mapping coverage*, not completed requirements; candidate tests may cover only a subset of a compound requirement.
- This report deliberately inspects **40 bounded and explicitly named implementation checkpoints** across E0–E6. **25/40 (62.5%) have a source-confirmed supporting implementation or documentation checkpoint**. This is an *observed-checkpoint coverage rate*, NOT percentage of an entire engine, weighted workload, remaining effort or production readiness. Selection is not exhaustive or equal-effort.
- **Formally accepted requirements: 0/75 recorded as accepted in the requirements CSV**. This measures *signed-off ledger entries*, not absence of implementation. Atomic, exact-SHA acceptance criteria have not been fully enumerated. The roadmap forbids portraying mapping or observed-checkpoint figures as Engine V2 completion percentages.

## Bounded checkpoint comparison

Symbols: **S** source/artifact and related test found; **G** gate incomplete or full requirement not demonstrated. Each row describes an independently scoped checkpoint, not necessarily the entire roadmap obligation.

| Phase | Observed checkpoints | Source-backed | Not demonstrated / remaining |
|---|---:|---:|---|
| E0 inventory | **2/5 (40.0%)** | S: dated architecture/baseline inventory exists; S: 75-entry requirement mapping/evidence index exists | G: fully current all-surface call graph; G: exhaustive tool/transport/UI control acceptance; G: reviewed migration/rollback/trust-anchor decision matrix |
| E1 security | **4/5 (80.0%)** | S: one-shot drain contract and regression; S: fail-closed IP/DNS scope tests; S: exact plan-bound approval tests; S: worker ownership/lease recovery tests | G: complete adversarial redirect/pivot/external DNS, audit-failure and exact candidate acceptance lab |
| E2 contracts | **4/5 (80.0%)** | S: versioned immutable DAG/task contracts; S: immutable manifest registry with deterministic resolution; S: durable scoped/revocable approval bindings; S: plan digest/integrity and compatibility tests | G: full canonical versioned domain contract set and backward-migration acceptance |
| E3 durability | **5/6 (83.3%)** | S: persisted mission/plan/task/attempt graph; S: atomic claims/leases/retries; S: mission budget/deadline/cost/rate limits; S: stop intent and uncertain outcome fencing; S: durable events and consumer cursors | G: real external-effect process-kill, multi-worker recovery, audit-store failure and outbox/independent integrity trust-anchor acceptance |
| E4 providers | **5/7 (71.4%)** | S: local catalog-adapter bridge; S: bound trusted provider router with provider selection; S: semantic operation aliases; S: read-only catalog/adapter portfolio audit; S: separately proposed evidence-driven follow-ups | G: exhaustive transport/catalog/CLI/UI parity and provider substitution acceptance; G: retirement of bypassable legacy autochains only after proven migration |
| E5 services | **3/6 (50.0%)** | S: durable acknowledged run-request queue; S: continuous headless request worker with stop controls; S: CLI/API/Core shared workflow surfaces | G: controlled real crash/restart with running external effect; G: daemon/systemd/container, backup/restore and supported platform acceptance; G: all service-client lifecycle and reconnect parity |
| E6 UI/release | **2/6 (33.3%)** | S: 22 UI-v2 routes/templates in the product; S: static source-control inventory with 793 controls | G: per-control real-service acceptance; G: visual/responsive/accessibility/offline parity; G: authorized seeded end-to-end solo lab; G: §38 G01–G10 release sign-off |
| **E0–E6 sampled total** | **25/40 (62.5%)** | Evidence of implementation, **not 62.5% completion** | No phase has full gate acceptance |
| E7–E9 | Excluded | Components or designs exist | Deferred P6–P8; do not penalize solo-v1.0 denominator |

### Concrete source and test references

- **E1** `tests/test_initialize_drain.py::test_initialize_drain_false_leaves_job_pending`; `tests/test_scope_failclosed.py::test_hostname_dns_failure_fails_closed`; `tests/test_providers.py::test_core_plan_bound_policy_requires_exact_unrevoked_approval`; `tests/test_worker.py::test_stale_reconciliation_fences_old_worker_token`.
- **E2** `src/whaxon/core/workflow.py`, `src/whaxon/core/capabilities.py`; `tests/test_workflow.py::test_plan_roundtrip_is_stable_and_digest_is_deterministic`, `test_workflow_approval_is_durable_exact_bound_and_revocable`; `tests/test_capabilities.py::test_capability_registry_persists_and_reloads_manifests`.
- **E3** `src/whaxon/core/scheduler.py`, `src/whaxon/core/store.py`, `src/whaxon/core/workflow_requests.py`; `tests/test_workflow.py::test_mission_wide_attempt_cap_applies_across_independent_plans`, `test_mission_rate_limit_serializes_claims_across_plans_and_restart`, `test_workflow_event_cursor_is_durable_monotone_and_plan_scoped`, `test_success_after_cancellation_is_recorded_uncertain_atomically`; `tests/test_workflow_run_requests.py::test_stale_run_is_uncertain_not_automatically_replayed`.
- **E4** `src/whaxon/core/providers.py`; `tests/test_providers.py::test_router_selects_explicit_provider_for_shared_semantic_capability`, `test_e4_portfolio_audit_reconciles_catalog_and_adapter_only`, `test_semantic_operation_and_legacy_alias_use_same_guarded_runner`; `tests/test_engine_v2_followups.py::test_e4_semantic_evidence_proposes_only_pinned_semantic_followup`.
- **E5** `src/whaxon/core/__init__.py`, `src/whaxon/core/workflow_requests.py`, `src/whaxon/interfaces/cli/workflow_cmd.py`, `src/whaxon/interfaces/web/server.py`; `tests/test_workflow_continuous_worker.py::test_headless_worker_polls_for_later_arrivals`; `tests/test_server_workflow_v2.py::test_api_202_is_persisted_before_worker_wakeup` is **not** defined there: the test actually lives in `tests/test_workflow_run_requests.py`. This cross-file distinction matters for exact traceability.
- **E6** `src/whaxon/interfaces/web/templates/ui_v2_*.html`, `docs/UI_CONTROL_INVENTORY.md`, `tests/test_web_ui_v2_*.py`. Static discovery does not establish every displayed control is wired.

## Documentation-versus-code discrepancies requiring reconciliation

1. **Stale evidence head:** `docs/ENGINE_V2_EVIDENCE_MATRIX.md` audits `c75c038...`, whereas inspected main is `781246b...`. Add verified source/test findings for subsequent commits without retroactively accepting previous requirements.
2. **E1 branch claim is historical:** `docs/ENGINE_V2_E1_ACCEPTANCE.md` says all E1 changes are on a working branch and instructs one future merge. Current main already contains many E1-related source changes and tests; acceptance remains OPEN, but the branch-only statement is not reliable current status.
3. **Old startup blocker retained in narrative:** `docs/STATE.md` lines describing `coverage/validate/retest/recon` as still draining unrelated jobs are superseded by its 2026-11-02 top note and the architecture continuation. Treat the fixed one-shot startup behavior as implemented, not an open code task; preserve wider E1 proof.
4. **E3/E5 under-described by dated snapshots:** actual main includes persisted run requests, continuous polling, mission-wide durable limits, cancellation fencing, event cursors, evidence cross-checks and local evidence seals. They close *implementation slices*, not process-kill and deployment acceptance.
5. **E4 snapshot lags main:** the existing dated E4 discussion still describes earlier unmerged/failed PRs; main now includes trusted alternative routing, bound provider identities, semantic operation aliases, a read-only portfolio audit and evidence-derived follow-up planning. Full transport parity is still not established.
6. **Audit integrity limitation:** `src/whaxon/core/store.py` explicitly describes its local SHA-256 evidence baseline as not a tamper-proof external audit signature. Do not label local digests an independent trust anchor.
7. **UI status must not be equated with working controls:** 793 statically inventoried controls across 22 templates, including unresolved/static examples, do not imply complete interaction, visual, accessibility or offline acceptance.

## Batches to turn observed-checkpoint coverage into genuine completion percentages

**Batch A (E0/E1, parallel):** Refresh all current callers/permission/transport inventory and acceptance traceability; adversarial startup/target/pivot/DNS/session/cancel/audit failure suites with exact negative assertions and network limitations.

**Batch B (E2/E3, parallel subject to stable interfaces):** Enumerate canonical schema/compatibility matrix; controlled subprocess hard-kill after external dispatch, two-worker contention, lost lease, injected audit/store failure, incomplete response and manual reconciliation; preserve uncertain effects without blind retries.

**Batch C (E4/E5, parallel):** Compare live catalog vs adapters vs normalized operations vs CLI/API/UI exposure and proofs; validate explicit provider substitution and migration parity; exercise headless service, foreground/daemon/container restart, backup/restore and clients reconnecting after restart.

**Batch D (E6, after service contracts):** Compare each visible supplied UI control against a real endpoint/permission/test; run browser visual/accessibility and controlled lab end-to-end/§38 release gates. Never redesign or invent functionality.

For **each atomic criterion**, store: requirement ID, scope/applicability, source path and symbol, test function plus exact assertion, observed command/environment/commit, result, limitation, reviewer and decision. Only then compute `accepted / applicable atomic criteria`. Review all new writes against current head to avoid overwriting concurrent work.

**Audit outcome:** code has advanced materially beyond several narrative status snapshots; 9/9 exact-head CI succeeded; **no credible full Engine V2 completion percentage is established yet**. This document supplies a reproducible checkpoint scope and explicit next evidence tasks rather than inventing a release percent.


## Current-head reconciliation — 2026-11-03 (newer than the audit above)

**Inspected main:** `f0b25d3629d776b433f72c83db679bb41313c812`. This section supersedes the 25/40 sampled checkpoint total above for current source reporting, but preserves the original 40 rows and their historical audited SHA. This review checks current GitHub source and named test definitions; **it does not execute pytest, deploy systemd, launch a browser or certify release acceptance**.

The checkpoint ledger has eight new bounded, separately identifiable source-backed checks. **33/48 = 68.75% sampled implementation coverage** across E0–E6. This is an unweighted presence ratio for selected checkpoints only; it is **not** the percent of the entire Engine V2 built, remaining engineering effort, operational readiness or release completion. Neither its denominator nor individual checkpoints are exhaustive/equal-sized.

| Phase | Source-backed / sampled | Sampled source implementation | Formal phase acceptance |
|---|---:|---:|---|
| E0 | 2/5 | 40.0% | Open |
| E1 | 5/6 | 83.3% | Open |
| E2 | 5/6 | 83.3% | Open |
| E3 | 7/8 | 87.5% | Open |
| E4 | 6/8 | 75.0% | Open |
| E5 | 6/9 | 66.7% | Open |
| E6 | 2/6 | 33.3% | Open |
| **E0–E6** | **33/48** | **68.75%** | **All open** |

The separate 75-row roadmap-index ledger still records **0/75 formally accepted requirement entries**. Those source-level rows combine multiple criteria, so this is a sign-off count, not proof that 0% is implemented. No credible full-engine percent-complete estimate can be computed solely from these ledgers. Deferred E7–E9 features are excluded from the sampled solo-v1.0 denominator.

### Reconciled current implementation, with exact limitations

- **E1:** Public queue enqueue, duplicate and status records redact private worker lease credentials. E1 branch-only wording is historical; current main already contains security corrections, but full adversarial acceptance is open.
- **E2:** Strict JSON task/plan construction rejects ambiguous unsupported values, cycles, nonfinite numbers and invalid mapping keys before digest/approval. Full backward schema migration remains open.
- **E3:** Lost worker leases and changed plan digests emit durable, bounded, idempotent uncertain-request audit events. A regression actually kills a Python child process after a synthetic callback writes a marker, manually ages its heartbeat and asserts uncertain/no automatic replay; this is **not** a real external-scanner effects test nor a complete independent integrity/outbox test.
- **E4:** Adapter disappearance, stale manifests and changed catalog bindings are checked at live resolution; this does not certify cross-transport provider substitution or retirement of all legacy execution paths.
- **E5:** PR #120 (squash `15fd5e4058377abaea2f0103f849f3817f050ba8`) merged a packaged, independently supervised *systemd unit candidate* and SQLite-only snapshot/restore tests. Health checks differentiate Core data/DB readiness from optional MSF. The crosswalk records 10/10 successful **pre-merge PR-head checks**, not verified runtime launch on an actual host or complete disaster recovery.
- **E6:** Source presence of 22 UI-v2 pages and a 793-control static inventory remains distinct from complete authorized per-control runtime, visual/accessibility and lab-release acceptance.

**Authoritative precedence:** master roadmap defines goals and gates; current source/tests establish code behavior; dated documents and branch/PR checkpoint notes are historical unless verified against main. Do not resurrect fixed one-shot startup issues or represent partial provider/service components as absent. Existing legacy worker/Automator/AI paths remain until migration, parity and rollback gates are passed.



---


## Source 15: ENGINE_V2_EVIDENCE_MATRIX.md

**Provenance:** [Original source](#source-15-engine_v2_evidence_matrixmd) · Snapshot at 2026-11-05 main baseline. **Interpretation:** Contains original dated claims; keep their stated commit and acceptance boundaries.

### Engine V2 — Roadmap requirement evidence matrix

> **2026-11-03 update:** Four bounded rows (P0-04, P1-01, P2-07, P4-01) now have ACCEPTED status on exact source `f0b25d3629d7`, backed by [acceptance reconciliation](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) and [CI #41642767222](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41642767222). This file's older `NOT_ACCEPTED` accounting is historical for its stated earlier baseline. All ten G gates remain open.

**Source of truth:** [master roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) and [architecture crosswalk](#source-15-engine_v2_evidence_matrixmd).  
**Original audited baseline:** `c75c03888e35f6147cfae3547f286202bb09fd6e` (main, 2026-11-03). **Current-head source reconciliation:** `f0b25d3629d776b433f72c83db679bb41313c812`; see [checkpoint audit](#source-15-engine_v2_evidence_matrixmd) and [48-row bounded checkpoint ledger](ENGINE_V2_AUDIT_CHECKPOINTS_2026-11-03.csv). The figures below remain a historical mapping of compound roadmap requirements, not current completeness.  
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

