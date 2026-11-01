# WHAXON Engine v2 — Architecture Specification & Roadmap Crosswalk

**Status:** Target architecture and implementation contract. This document does not claim the design is implemented.  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Authority:** The master roadmap remains authoritative. Its §0 dependency-driven order governs delivery; this specification does not reorder or bypass it.  
**Baseline:** Main at `b27d361e706bcea800300dcf3e8b2e094a429d42`; source and tests must be re-inventoried at implementation start.

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
