Warning: truncated output (original token count: 30404)
Total output lines: 1079

Warning: truncated output (original token count: 60794)
Total output lines: 2154

# WHAXON — ENGINE V2 MASTER DOCUMENT

> **Current code and delivery sequence (2026-11-06; implementation baseline at main `0cef416155623199d8cb551b809dd469d62b4778`):** Exact-head CI run [42253317306](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42253317306) passed 20/20. Bounded G01–G05 and G07–G09 records are engineering evidence, not full release approval. The tree includes the G01 CLI inventory/AST guard, PR #144 report overhaul, and PR #143 upgrade smoke. Remaining implementation includes exhaustive legacy caller coverage, V2 lifecycle/client parity, complete UI behavior/control wiring, and integrated recovery work. UI implementation continues. Run internal tests during development. Defer additional real-target validation, external review, manual accessibility review, and production-like deployment/rollback exercises until the agreed V2 engine, V2 UI, and remaining solo-v1.0 scope are complete and internal checks pass. The [G10 record](ENGINE_V2_G10_RELEASE_DECISION.md) remains HOLD — NOT READY TO DEPLOY.

**Consolidation date:** 2026-11-06. **Historical consolidation baseline:** `6a41f626536be917e12acd175ffffad716132823`; current status is reconciled to the exact `main` SHA in the audit banner above.

> **Authority and interpretation:** This is the single consolidated Engine V2 architecture, implementation, acceptance and evidence reference. The root [master product roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) remains authoritative for product priorities, release requirements and scheduling. Current source plus exact-head test/CI evidence determine implemented behavior; the historical records below are not independent current-status claims. A phase's implementation evidence is not production approval. Never infer production deployment readiness from a dated green run, merge, or design.

## Delivery sequence

Finish the agreed V2 engine, V2 UI, and remaining solo-v1.0 implementation before final external validation. Keep unit, integration, static, security, and browser tests active throughout development. After the complete agreed scope passes internal checks, perform authorized real-target testing, independent review, manual accessibility/security review, and production-like install/upgrade/rollback/recovery qualification. Production rollout follows a passing exact-candidate qualification. Deferred P6–P8 / E7–E9 expansion is outside this completion scope.

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
| §20 market/platform coverage | Extension seams for PTaaS, remediation, ASM, compliance, collaboration, threat intel, training, cloud posture, APIs, i18n, air-gap and desktop-only deployment |
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

**Scope and delivery sequence:** This section consolidates the full-engine direction across E0–E9. Implementation remains active across the agreed V2 engine and UI scope; no repository freeze should block that work. Reuse correct, tested code; do not rebuild working components. Internal checks run continuously. Final external validation and deployment qualification begin only after the agreed implementation scope is complete and internal checks pass. No phase is considered accepted merely because its code or tests exist.

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
| Multi-target / subnet work | Canonical assets, scope proofs, bounded graph fan-out/joins, …404 tokens truncated…ain jobs survive process exit as SQLite pending rows and are claimed atomically.
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
| E6 UI/release | **2/6 (33.3%)** | S: 22 UI-v2 routes/templates in the product; S: static source-control inventory with 793 controls | G: per-control real-service acceptance; G: desktop visual/accessibility/offline parity; G: authorized seeded end-to-end solo lab; G: §38 G01–G10 release sign-off |
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

## G01 controlled-lab candidate — 2026-11-05

PR #132 extends the capability/interface crosswalk with a fixed, opt-in
Metasploitable2 Samba access provider and an isolated Compose acceptance chain.
The seeded SQLi fixture shares the target's `.10` network namespace so recon,
enumeration, initial access, verification and retest use one normalized target.
Mission aggregation now rejects plans whose task targets do not resolve to the
same host. The provider persists its local job before Metasploit dispatch,
records the remote job ID, refuses to reuse existing matching sessions and
stops a newly opened session if evidence persistence fails. The CI harness
closes its session in `finally` and uploads the report with a SHA-256 sidecar.

Rapid7 Framework 6.5.4 source was checked for the pinned Samba module,
`cmd/unix/reverse_netcat` payload, session RPC fields, stop call and daemon
flags. This confirms API compatibility only, not exploit success on the pinned
target image. Local workflow/Engine V2 regression tests pass (422 tests), as do
Ruff, mypy, Python compilation and `git diff --check`. Earlier exact-head CI
found and exposed fixes for Compose credential ordering and SQLmap fixture
confirmation. Actual Docker image startup, callback/RPC, new session, full
chain and retained evidence remain to be proven by exact-head CI. Timing and
observation verification are explicitly unsupported in this crosswalk and
remain a separate G03 gap. G01 remains open and unfrozen; G02 stays parked.

## Desktop terminal client migration — 2026-11-11

The TUI catalog's primary Run action now hands the selected fixed-argument tool
and exact target to the Engine V2 workflow screen. The operator must select or
create a mission, save a reviewable plan, inspect its task binding, grant the
required approval, and submit a durable request before execution can begin.
Free-form extra arguments are refused because they cannot be safely represented
by the fixed V2 capability binding. The TUI screen no longer contains a direct
ToolRunner call. Other legacy direct callers remain inventoried and open until
their V2 parity and rollback criteria are demonstrated.

The workflow screen also lists persisted queued, running and uncertain run
requests from the shared Core queue. Selecting one reconnects the TUI to its
plan and request status after reopening the screen; cancellation stays a
request and does not claim that an external effect stopped. Regressions cover
the catalog-to-plan handoff, rejection of free-form arguments, queue reconnect,
explicit approvals and cancellation. Local verification: 26 TUI and dispatch
inventory tests passed, Ruff passed, and mypy passed. The Chromium browser binary is unavailable in
this local environment, so the Retest browser regression relies on exact-head
CI. This closes one TUI dispatch path and one client reconnect gap only; web
and GUI legacy dispatch, remaining CLI/AI/session/provider parity, recovery and
release acceptance remain open.

