# Engine v2 — E0 Repository Baseline & Execution-Path Inventory

**Review date:** 2026-11-01  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Branch / baseline:** `main` at `2263477b1a79c384bcadb1cc22fc032e38d0c745`  
**Architecture authority:** `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md`  
**Roadmap authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, §0 and §49  
**Review type:** Static source, test, configuration and repository-tree inspection. No runtime tests were executed in this inventory pass. No runtime code was changed.

> **Historical baseline (2026-11-01).** This is a point-in-time E0 inventory at the commit above. Its statements that Engine v2 contracts, scheduler, mission persistence or leases do not exist are superseded by the dated implementation update in master roadmap §49 and the current [Engine v2 crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md). Use this file only to understand the migration starting point, not current implementation status.

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
