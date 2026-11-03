# WHAXON Engine v2 — Architecture Specification & Roadmap Crosswalk

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


### 14.13 E3/E5 follow-up batch — stop-aware durable claim barrier (2026-11-03)

**Active implementation branch:** `engine-v2/e3-e5-stop-aware-worker-batch`, based on the already-merged PR #98 continuous worker. Previously the signal-aware worker stopped only **between** calls to `drain_workflow_run_requests(max_runs=20)`. A stop arriving during the first request could allow the remaining 19 requests in that batch to be claimed, violating the intended graceful shutdown boundary. The Core draining method now accepts an optional, validated stop-event and checks it **before each new claim**. The continuous service passes its same stop-event to the shared drain. The API and one-shot drain callers retain unchanged behavior when no event is supplied. A signalled worker does not claim queued requests; already claimed effects are neither killed nor falsely reported cancelled. Added three regression tests: stop after first job of a multi-request batch, pre-set stop leaving the queue unchanged, and malformed stop-event refusal. An absolute zero-race guarantee against signals coinciding exactly with the atomic claim is not claimed; the existing durable lease and uncertain-effect recovery still apply.

**Verification/next-session gate:** Run Ruff, mypy and full Python 3.11–3.13, cross-platform and headless CI on the exact branch head; merge only after passing checks. This is an independent E3/E5 batch and must not silently overwrite the E4 PR #96 provider/semantic work. Rebase onto up-to-date main before merge if the E4 PR lands first. Remaining E3/E5 work includes task-outcome reconciliation, service supervision, health/readiness and audited resource/stop guarantees.
