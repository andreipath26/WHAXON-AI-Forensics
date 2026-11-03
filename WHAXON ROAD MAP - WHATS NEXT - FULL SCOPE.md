# WHAXON — Product trajectory and release gates

## Engine V2 E0–E9 phase-freeze policy (operator decision, 2026-11-03)

For **every Engine V2 phase E0–E9**, engineering completion, phase merge and freeze are distinct from final integrated-engine deployment acceptance. A phase may be frozen after its required implementation and interfaces are complete, applicable automated unit/integration/adversarial/security tests and supported exact-head CI pass, residual integration obligations are recorded, and engineering sign-off is documented. Preserve the one-phase/one-branch/one-PR/one-final-merge rule. Do not infer acceptance from source presence or older CI.

**Deferred to the final full Engine V2 deployment gate, not waived:** authorized real-scanner controlled-target laboratory runs, externally protected audit-anchor/witness and retention validation, production-like service and multi-worker operation, host/network crash and recovery, backup/restore, complete cross-client end-to-end validation, and deployment/operator sign-off. These remain explicitly **NOT PASSED** until evidenced. No frozen phase, green CI or mock test implies production readiness or closes the overall release gates. Security authorization, fail-closed behavior, uncertain-effect reconciliation and audit integrity remain mandatory implementation requirements. Reopen a frozen phase only for evidenced correctness/security defects or necessary cross-phase integration repairs with regression coverage.

This operator decision supersedes earlier requirements to finish deployment-level tests *before phase engineering freeze*, but does not supersede final release safety and acceptance gates.

> **Engine V2 current-head evidence note (2026-11-03):** At main `f0b25d3629d776b433f72c83db679bb41313c812`, the [dated source audit](docs/ENGINE_V2_CODE_VS_ROADMAP_AUDIT_2026-11-03.md) and [checkpoint ledger](docs/ENGINE_V2_AUDIT_CHECKPOINTS_2026-11-03.csv) reconcile 33 source-backed of 48 *selected unweighted checkpoints* (68.75% sampled presence), including newer E2–E5 changes and merged E5 service-unit work. This is **not** a whole-engine completeness or v1.0 release percentage. The roadmap's priority/acceptance requirements below remain authoritative and no E0–E6 phase has formal full-gate sign-off. The earlier 25/40 audit is historical.

> **Integration update — 2026-11-02, supersedes affected baseline statements below:** Four one-shot CLI commands now use `initialize(drain=False)` with regression coverage. Desktop startup targets `/ui-v2`. Test catalog consumers use the packaged seed; the duplicate tracked root catalog and unused qasync requirement/manifest entry are removed, while operator catalogs and protected legacy designs remain preserved. See [UI control inventory](docs/UI_CONTROL_INVENTORY.md) for 793 source controls across 22 templates; static coverage does not establish complete runtime wiring, visual fidelity, accessibility or service parity. Local browser execution is blocked by unavailable Chromium downloads. The earlier CI/source records below describe their stated baseline, not acceptance of this integration.


**Reviewed:** 2026-11-02 · **Repository:** `andreipath26/WHAXON-AI-Forensics`
**Inspected baseline:** `6fa1fa5f9bcff9b7afffb87ca908b0f78562fa3b` · **Package:** `0.11.16`, Beta
**Decision:** finish and accept one reliable solo assessment product before expanding the platform. **v1.0 acceptance is OPEN.**

This is the single active work order. It replaces the accumulated schedules, session diaries, tool-count targets and contradictory status snapshots in the previous roadmap. It does not erase approved deferred scope or turn implemented components into accepted product workflows. Current source/tests establish behavior; this file establishes priorities and acceptance; operator guides explain use. [Due diligence](docs/DOCUMENTATION_RECONCILIATION.md) records removal and retirement decisions; [baseline register](docs/V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) records source/test/CI evidence.

## 0. How to use this trajectory

Read the current baseline, follow P0–P5 in dependency order, and close §38 with evidence. A mapped critical correctness/security defect may move immediately into P1 while independent P0 inventory continues; P0 is not a serial waiting gate for a known bounded repair. P6–P8 are gated expansion. Work on independent tasks concurrently only when contracts, ownership, integration order and tests are agreed; follow [the engineering execution model](docs/ENGINEERING_EXECUTION_MODEL.md). Do not spawn work merely to increase concurrency.

Status meanings:

| Status | Meaning |
|---|---|
| Implemented | Source and regression coverage exist for the named behavior; acceptance may remain open |
| Partial | Some required behavior exists; specific gaps remain |
| Accepted | Named workflow passed its full gate on an exact revision/environment with retained evidence |
| Open | Required work or acceptance evidence is missing |
| Deferred | Approved direction outside the current release critical path |
| Retire after migration | Consumers/contracts must be migrated before removal |
| Remove after checks | No required behavior is lost; follow the due-diligence removal conditions |
| Excluded | Outside WHAXON's product boundary |

Do not derive a project-completion percentage from test counts, page counts, old DONE labels or merged PRs. There is no validated remaining-hours estimate. An accepted milestone needs commit, environment, commands/checks, result, limitations and evidence links. A failed, skipped or unavailable check is never a pass.

### Non-negotiable product rules

1. Deterministic plans and policy checks; AI proposes or explains, never grants authority or sets verification status.
2. Explicit consent bound to scope, exact plan/parameters, impact and expiry. An activated campaign may authorize routine in-envelope work; material changes and consequential actions need separate approval.
3. Bounded, allowlisted execution with least privilege, time/output/resource/rate ceilings, cancellation and fail-closed scope checks at dispatch and follow-up boundaries.
4. Independent verification. Tool output, exit zero, an installer result, a model assertion or a rendered page is not proof of success.
5. Attributable, timestamped, durable and tamper-evident evidence linking proposal, approval, action, observation, verification and recovery with stable operation/event IDs, plan/policy versions and digests, actor/approval identity and evidence hashes. Provide export and integrity checking through a verifiable hash chain or equivalent with an explicit trust anchor and stated limitations. Record denial, cancellation, timeout, crash, audit failure and uncertain effects. Hash chaining without an independent trust anchor is not immutability.
6. ZERO REDESIGN. Use the supplied `web ui files and rendering/` design inputs; preserve layout, typography, colors, spacing, components, icons, navigation, animations and responsive behavior. Keep unsupported features hidden/disabled without deleting distinct supplied reference designs or inventing backend success. Preserve legacy design source unchanged.
7. CLI/API/headless services own behavior; clients do not own durable jobs or implement independent authorization rules. Preserve tested parsers, scope checks and data compatibility during migration.
8. No universal zero-false-positive, unlimited-scale, fully air-gapped or production-ready claims without evidence for the stated scope.

## 1. Where the project stands

The product has substantial implementation. The remaining release work is correctness, consolidation, durable shared lifecycle and integrated acceptance—not rebuilding the existing Trust Layer or replacing the supplied UI.

| Workstream | Current evidence | Remaining boundary |
|---|---|---|
| Package and quality | `0.11.16`; baseline CI [#41488450899](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41488450899) passed all nine jobs; Python 3.11/3.12/3.13 each report **1,408 passed, 14 skipped** | CI certifies that baseline and its checks, not v1.0 acceptance or a later commit |
| Runner, adapters, persistence | Shared `Core`, ToolRunner, SQLite store, 24 packaged catalog entries, registered parsers and session integrations | Reconcile catalog/adapter/provider/readiness distinctions and each advertised support combination |
| Existing correctness fixes | CLI `run` drains its own follow-ups while preserving older pending jobs; Nikto current-format parser; worker leases and session/pivot identity guards | Do not reopen fixed bugs from historical notes; audit other entry points and boundary races |
| Trust Layer | Request-context replay, deterministic validation, observation/blind checks, retest, reproduction helpers, coverage persistence/reporting | Prove evidence completeness, conservative outcomes, meaningful coverage and report reproducibility end to end |
| Supplied UI | 22 production templates/routes; 23 UI-v2 test modules; web root redirects to `/ui-v2` | All-control inventory, visual fidelity, accessibility, service parity, external assets and desktop entry-point acceptance |
| Setup/readiness | Packaged manifest, doctor, profiles, approval-bound Python install, curated apt/Homebrew plans, operation/history APIs | Platform/upgrade/offline/partial-failure/restart acceptance; native Windows tool install remains manual |
| Engine v2 | Immutable versioned DAG/approval/manifest contracts; persisted missions/tasks/attempts; scheduler, bounded concurrency, deadlines, retries/fencing; initial catalog-provider bridge | Campaign-wide durable budgets/cancellation/audit/reconciliation; full service lifecycle and portfolio migration |
| Headless | Waitress/CLI service entry points; clean-wheel/headless Linux and setup smoke on Ubuntu/macOS/Windows in baseline CI | Service-mode, crash/restart, backup/restore and supported deployment acceptance |
| Expansion | Bounty ingestion/policy primitives and detailed approved designs exist | Full bounty autonomy, multi-target, broad Metasploit/provider coverage, patch application and enterprise are not delivered merely because designed |

The old Route/session-host collection failure is **closed at this baseline**: `routes.py` carries `session_host`, the live resolver supplies peer identity, regression tests cover drift/missing identity and the exact-baseline matrix passes. The historical approvals-browser failure is not a current red-CI blocker either. Keep security acceptance open without pretending these earlier failures still occur.

### Newly identified correctness dependency

`Core.initialize(drain=True)` may dispatch pending jobs. `coverage_cmd.py`, `validate_cmd.py` and `retest_cmd.py` call it with the default, as does `recon_cmd.py`; `run_cmd.py` and `workflow_cmd.py` explicitly use `drain=False`. This is a source-confirmed startup side-effect risk, not an executed exploit demonstration. A coverage read or rejected validation/retest request must not trigger unrelated historical work. Audit and repair the one-shot command contract in P1; test that pending work is untouched unless explicitly selected, while long-lived worker behavior remains intentional.

## 2. Critical path and active workstreams

| ID | Outcome | Status at baseline | Depends on | Acceptance / owner boundary |
|---|---|---|---|---|
| P0 | One trustworthy baseline and cleanup decisions | Partial; this review refreshes evidence and dispositions | Current main/CI | Full advertised-capability/control inventory remains open; docs/inventory integration owner |
| P1 | Correct execution, scope and Trust Layer semantics | Partial | Affected P0 boundary mapped; remaining inventory may continue | No unrelated startup dispatch; adversarial authorization/evidence checks; core/CLI/security owner |
| P2 | Shared durable lifecycle and compatibility seams | Partial | Stable P1 contracts | CLI/API/UI parity, bounded cancellation/recovery, no unsafe replay; core/service integration owner |
| P3 | Truthful first run and headless deployment | Partial | P2 lifecycle for affected operations | Clean supported environments, failure/recovery and resource/secret handling; setup/deployment owner |
| P4 | Supplied UI accepted against real services | Partial | P2 contracts; relevant P3 readiness | Every exposed control accounted for, zero redesign, visual/accessibility/parity evidence; page owner + one UI integrator |
| P5 | Solo end-to-end v1.0 and release | Open | P1–P4 integrated | All §38 gates; one release integrator |
| P6 | Programme policy and bounded autonomy | Deferred full subsystem; primitives present | P5 and policy/authorization gates | Isolated customer/bounty policies and audited in-envelope operations |
| P7 | Multi-target and competitive measurement | Deferred | P4 and P5 accepted | Per-target policy, bounded fan-out, seeded lab comparison |
| P8 | Selective platform/business expansion | Deferred | Accepted need and prerequisite contracts | Per-capability business case, unique value, license/support/test evidence |

**Immediate implementation queue:** (1) one-shot initialization side effects; (2) complete the capability/control and execution-boundary inventories; (3) durable lifecycle and evidence gaps from that inventory; (4) supported install/headless recovery and supplied-page acceptance; (5) integrated release proof. Safe documentation/file cleanup may proceed independently under its own checks. Never remerge old branch tips as a shortcut.

### P0 — Baseline and repository simplification

- Maintain the exact source/CI baseline and capability states: implemented, integrated, partial, planned, unverified, unsupported, blocked.
- Inventory every advertised tool/adapter/provider, CLI verb, API route, UI control, worker, transport and deployment mode; record source, authorization, persistence, tests and limitations. This review maps principal paths; it does not close an exhaustive security or per-control audit.
- Execute only independently reviewable cleanup batches from the [disposition register](docs/DOCUMENTATION_RECONCILIATION.md). Preserve Git history; no history rewrite or automatic branch deletion.
- Keep one maintained tool-catalog seed after migrating root-catalog consumers. Research inventories must not masquerade as runtime support.
- Retire historical implementation plans as active instructions. Keep unique rationale/evidence where necessary, with corrected links. Do not create another competing roadmap or a new archive full of duplicate files.
- Recheck `main` and exact branch tips before any later deletion. An ancestry-contained branch can be retired after reference checks; a diverged/squashed branch needs content/PR reconciliation.

**Exit:** one current baseline, disposition/retirement list, complete capability inventory, dependency map, work ownership and acceptance plan. This review does not mark the entire P0 exit accepted.

### P1 — Existing execution correctness and Trust Layer

- Repair one-shot initialization as described above. Preserve own-follow-up draining for `run`; do not restore global draining as its fix.
- Verify fail-closed scope for original/redirected/resolved/replayed/follow-up/pivot/session targets, and recheck immediately before consequential dispatch. Cover ownership races, closed/drifted sessions, cancellation and descendants. Document external-tool DNS/secondary-request and egress limitations.
- Enforce approved action identity, permissions, scope, expiry and impact independently of AI/UI. Host/programme authorization and external RPC/TLS transport checks must not weaken during refactoring.
- Retain deterministic request-context replay for supported methods/headers/bodies and authenticated contexts without leaking secrets. Current security guards refuse POST and other state-changing replay until a separately authorized safe-replay contract exists; request-context storage is not proof that every method is replayable. Validate SQL/error markers, reflected XSS, blind timing, observation probes, malformed inputs and changed scope; state timing limitations.
- Retest only eligible previously verified findings; keep `fixed`, `still_vulnerable`, `inconclusive` and reasons distinct. Network failure or changed evidence alone is not proof of a fix. This is narrower than the future remediation lifecycle.
- Preserve raw request/response or timing/baseline evidence, target identity, artifact/reproduction provenance and state transitions. AI may triage/summarize only; human review does not turn ambiguity into deterministic proof.
- Coverage discloses skipped, failed, unrequested, inaccessible and unsupported work from persisted records. A heuristic confidence number must not imply measured recall, endpoint completeness or certainty.
- Prove audit/evidence behavior on success, refusal, cancellation, timeout, interruption, recovery and audit-write failure. Document remaining integrity/trust-anchor limits.

**Exit:** controlled workflows do not silently dispatch unrelated work, bypass authorization, fabricate success/verification or omit material coverage/evidence gaps.

### P2 — Shared services and Engine v2 migration

- Use one versioned domain/service boundary for missions, plans, tasks/attempts, approvals, progress, findings, evidence, coverage, verification, reports and errors; CLI/API/web/headless are clients.
- Preserve existing ToolRunner, parsers, store compatibility and safe transport behavior behind façades. The worker/Automator/sequential AI executor are still live; remove them only after caller and persisted-state migration, parity, no-bypass and rollback evidence.
- Extend implemented scheduler bounds to durable mission-wide rate/resource/cost/time/concurrency accounting and cancellation. Persist stop intent and recover without repeating uncertain external effects. Existing per-run task/concurrency limits are implemented, not a missing feature to rebuild.
- Complete crash/restart reconciliation, worker leases, graceful shutdown, independent task failures, durable progress and audit/outbox guarantees. Do not promise exactly-once external side effects.
- Replace fixed Automator branches with evidence/capability-driven follow-ups only after equivalent behavior is tested. Feed AI proposals through the same plan/policy/approval services; no second scheduler or execution authority.
- Define common versioned provenance, capability-report and onboarding/readiness-state models for existing-portfolio reconciliation before adding candidate automation. Reconcile catalog-only, adapter-only, import-only and session integrations; use bounded read-only discovery/extraction and deterministic gap/compatibility analysis in P0/P2, rather than deferring migration prerequisites to P8. Manifests describe actual target/protocol/platform/auth/input/output, dependency, impact/permission, timeout/cancellation, readiness, parser/evidence and reconciliation support. Registration never authorizes execution.
- The initial provider bridge is constrained to an allowlist and catalog defaults, with no dynamic task inputs; its manifest readiness is `registered`. Do not advertise all providers as generally safe or fully verified.

**Exit:** a supported job can be created, authorized, observed, cancelled and recovered through shared services independently of a browser, with audit and coverage intact.

### P3 — Setup, readiness and headless deployment

- Maintain the schema-validated dependency manifest and deterministic environment/readiness evaluator. Missing optional dependencies degrade only dependent capabilities. Distinguish presence, version verification, functional smoke-test evidence and actual runtime readiness.
- Keep Core/Standard/Full/Custom preview read-only. Use exact-plan approvals and separate system/elevation consent for curated OS tools. No commands copied from AI/tool output, silent elevation or arbitrary installer execution.
- Verify clean and partial installs, optional extras, wheel/sdist resources, venv/no-admin behavior, upgrade, offline/manual fallback, PATH conflicts, missing assets, wrong versions, partial changes, cancellation, interruption, restart and audit failures. Disclose that completed package changes are not generally rolled back.
- Curated apt support is restricted to recognized Debian/Ubuntu/Kali combinations; Homebrew is the supported curated macOS path. Treat native Windows and WSL as distinct environments with separate support/test records. Native Windows package-manager installation stays manual until separately implemented/accepted. Setup-preview smoke is not full platform acceptance.
- Make first-run, doctor, administration, job/campaign/status and approval workflows usable without desktop/TUI/browser. Test foreground first, then advertised daemon/systemd/Docker modes, health/readiness, secrets/auth/TLS/reverse proxy, restricted permissions, persistent volumes, resource limits and backup/restore.
- Consolidate installation/readiness operations onto the durable lifecycle rather than assuming operation files/process-local workers guarantee every restart/multi-process case.

**Exit:** a clean supported host installs a truthful profile, runs headlessly and retains/reconciles supported jobs/approvals/evidence across disconnects and restarts; unsupported combinations are explicit.

### P4 — Supplied UI integration and acceptance

- Use the 22 current production routes/templates and named supplied designs. The baseline package contained 32 HTML and 32 PNG files. Cleanup removes five exact loose copies of each type, leaving 27 HTML and 27 PNG named inputs including distinct alternatives; counts are not accepted product workflows.
- Complete one page/workflow at a time against real service contracts. Every visible control must be recorded as real, hidden or disabled with its endpoint, permission, loading/empty/error/progress/cancel/reconnect behavior and test. A passing route is not acceptance of all its controls.
- Account for dashboard, scope, run, findings, report, reports, history, diagnostics, evidence, AI, retest, chains, adapters, settings, audit, monitoring, BAS, bounty, compliance, PTaaS, threat intelligence and approvals. Pages may present supported subsets; future capabilities stay inaccessible.
- Run visual regression against approved supplied references, responsive checks, keyboard/focus/non-color/screen-reader acceptance, and CLI/API/UI service parity or documented deliberate differences.
- Resolve external Tailwind/font/icon/image dependencies and verify the supported deployment/offline policy without altering the supplied design. Current CDN-dependent pages do not prove air-gap readiness.
- Correct desktop `embed.URL` from legacy `/ui` to the accepted new default, then test desktop startup/navigation. Preserve old UI templates/CSS/JS/screenshots and the legacy audit unchanged; reference-only retirement and public route deprecation need compatibility evidence.
- Distinct `_forensics_hardened` and `_v0.11.16` source variants require a canonical mapping/difference review. Do not delete them because their names look old. Exact loose duplicates are a different disposition.

**Exit:** every exposed page/control has real authorized behavior; unsupported features remain inaccessible; design, accessibility, parity and deployment acceptance pass on the candidate.

### P5 — Solo v1.0 proof and release

One operator must complete an authorized controlled-lab chain: scope/recon → enumeration → discovery → supported initial access where in scope → independent validation → findings/evidence → honest coverage/report → remediation retest. Declare which stages/targets/transports were exercised and which were not. Demonstrate reproducibility and false-positive handling against known ground truth; never generalize a clean lab result to all targets.

Use existing hydra/session/validator/report/retest primitives where supported; a fixed six-new-tool list is not an unconditional release gate. Add a provider only when a measured gap blocks the agreed proof. Business-logic/browser inference and AI-system testing are conditional workstreams, not assumed existing capabilities; explicitly scope/defer them when the proof target has no such surface.

Close all §38 gates. Capture current reports, inspect HTML/PDF/Markdown/JSON behavior and evidence/redaction differences, then refresh state/operator docs and version/tag/build/publication evidence. Launch activity and commercial claims follow acceptance. Deferred team/enterprise/bounty/platform breadth is not a hidden v1.0 prerequisite.

## 3. Expansion after the solo foundation

### P6 — Programme policy, bounty and bounded campaigns

Retain the detailed [bounty design](docs/bounty-addon.md) and original §§26, 45–46 as requirement sources, subordinate to this order:

1. Source-backed programme ingestion and policy versioning, uncertainty, review/activation, dual programme+host gates, staleness/change suspension and audit. Import or URL availability never authorizes testing.
2. Controlled-lab plan/execution with separate customer/bounty policy/state, exact permission envelope, expiry, rate/concurrency/request/cost limits and emergency stop.
3. Provenance-preserving asset graph and monitoring; proposals never expand scope automatically.
4. Independent verification, evidence vault/reproduction, correlation and attack-path analysis.
5. Programme knowledge, measured prioritization and differential sessions/invariant/workflow inference. Managed-browser capture and identities use explicit authorization and deterministic boundaries.
6. Platform-specific report drafts, redaction, integrations and isolated multi-programme orchestration. Disclosure/submission requires separate explicit approval.

Manual/guided/supervised/autonomous modes share one controller. Routine activated in-envelope actions need no repetitive confirmation; scope ambiguity/expansion, increased limits, intrusive/destructive tests, sensitive-data access, identities/accounts, third-party testing, disclosure and paid actions pause for approval. Defend ingestion against prompt injection, SSRF, unsafe redirects/DNS, size/time/content limits and untrusted downloads. Do not assume third-party API/terms access.

### P7 — Multi-target, subnets and measurement

After P4/P5 acceptance, support domain/IP/URL/CIDR/mixed inputs with canonical assets, explicit authorization/provenance and exclusions; no discovery-driven scope expansion. Bound fan-out/per-target budgets and concurrency, isolate failures, preserve cancellation/recovery, deduplicate without losing per-asset evidence, and report partial/non-tested outcomes. Network discovery and transport/pivot behavior require separate accepted lab coverage.

Build a sourced competitor capability matrix and reproducible seeded-lab benchmark: ground truth, false positives/negatives, coverage, time/resource/cost, evidence quality, installability, usability and retest outcomes. Retain version/date/environment and uncertainty. Feature counts and vendor claims are not superiority evidence. Keep this work after the supplied UI/solo gate.

### P8 — Selective tools, Metasploit, remediation and business platform

| Direction | Retained scope and admission rule |
|---|---|
| Tool intelligence/onboarding | [Detailed design](docs/TOOL_INTELLIGENCE_AND_ONBOARDING.md): source-backed capability/gap/risk report, bounded read-only introspection, overlap/license/maintenance/platform assessment, proposed→researched→assessed→approved→integrated→validated→enabled/deprecated lifecycle; no auto-install/enable/plugin execution; monitoring reports deltas only |
| Tool portfolio | Evaluate unique capability and measurable value; reconcile catalog/adapters/providers before adding breadth. Keep CLI-native tools native; adopt structured harness/verification/discovery methodology on touch; GUI/Burp control is a separate integration. No 120-tool quota or old hour estimates |
| Recon/API/cloud/code | Preserve provenance/scope for recon; design authenticated API/OpenAPI contracts and typed cloud-SDK/account/region/IAM scope; distinguish source/SARIF, container/dependency/SBOM, Kubernetes and secrets inputs. Prefer supported unique providers over overlapping frameworks; maintenance substitutions require current evidence |
| Metasploit/Armitage | [Detailed design](docs/METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md): full module metadata/search/options/payload/compatibility/job/session/route/pivot coverage and collaborative-workbench patterns inside the supplied UI, through the same Engine v2 services; individual operations require scope, impact/privilege, approval, timeout, cleanup and lab acceptance. Existing RPC support is not full integration |
| Remediation | [Approved detailed addendum](WHAXON%20Competitor%20Capability%20and%20Remediation%20Roadmap%20Addendum.md): native/imported finding normalization → root cause/context → reviewable patch → isolated validation → separately authorized application → rollback/recovery → original-check retest and before/after evidence. Current `core/remediation.py` is dependency remediation planning, not this vulnerability patch engine |
| AI/business-logic/AIRT | Provider-neutral proposal interface; budgets/backoff/resume/escalation/dry-run and confidential-data policy; differential sessions, workflow/invariant checks and AI-surface adapters only with evidence and demand. No fixed free-tier/pricing/privacy assumptions from historical notes |
| Small teams/MCP | Shared workspaces, delegated roles/approvals, graph, retrieval and separate multi-agent roles after stable services and demonstrated demand. MCP metadata never grants permission; no mandatory new runtime dependency |
| Company/platform | Tenant/RBAC/SSO isolation, engagement lifecycle, collaboration, HA/observability, deployment/secrets/upgrade, billing/support only after validated customer need; preserve actor/tenant seams without pretending enterprise exists |
| Business capabilities | PTaaS, broader remediation lifecycle, ASM, report versioning/templates/redaction, compliance mapping, threat intelligence, training, CSPM/CIEM, SIEM/ticketing/CI/CD/webhooks/SDK, internationalization, offline bundles and responsive/PWA client remain deferred. BAS/AEV needs its own bounded scope and evidence. Mobile client support does not mean mobile application pentesting |
| Research | Fact-Intent Graph, hints/RAG/governed replanning, app-to-backend chains and full proof-driven remediation are post-foundation hypotheses. KILN, Aletheia, SYBIL and other portfolio projects are separate products, not WHAXON dependencies or release tasks |

Each addition needs source/license/version/platform, overlap/replacement, permissions/impact, parser/evidence, install/readiness, timeout/cancellation/recovery and test/rollback decisions. Discovery/research is not approval to install or execute. Credential access, poisoning, C2 and post-exploitation are separate high-impact capability classes, never ordinary unattended scanners.

## 4. Exclusions and retirement boundaries

The repository name does not expand scope into forensic tooling. Preserve original exclusions: wireless/SDR/hardware, digital forensics, reverse engineering, malware analysis, social engineering, mobile-app pentesting, honeypots, unsupported commercial scanners without CLI parity, and unstructured protocol-attack tooling. No unapproved/non-consenting activity, automatic scope expansion or bypass of the deterministic executor. Retain existing explicitly approved session/transport scope; this list is not permission to broaden it.

Safe removal is distinct from product retirement. The [disposition register](docs/DOCUMENTATION_RECONCILIATION.md) identifies exact duplicate/no-consumer candidates, dependency-bound removals, retained evidence/design/legal resources and migration gates. Cleanup removes only verified loose copies and superseded non-runtime artifacts; named design originals, runtime code, evidence and branch refs remain intact.

## 38. Solo v1.0 release acceptance — OPEN

This section retains the established release-gate number so references to §38 remain meaningful. Every item requires exact-candidate evidence; prior implementation markers or green CI alone do not close it.

| Gate | Required evidence | Baseline state |
|---|---|---|
| G01 Capability/workflow crosswalk | All advertised CLI/API/UI/tool/transport/deployment surfaces, source/tests, supported limits and complete controlled-lab chain | Partial; principal-path register exists, exhaustive inventory open |
| G02 Authorization/execution | No unrelated initialization dispatch; fail-closed target/scope/auth/approval, session/pivot/DNS/redirect/follow-up boundaries, ownership races and cancellation/descendants | Partial; substantial regression coverage, new startup issue open |
| G03 Independent validation/retest | Supported replay/SQL/XSS/timing/observation paths; candidate/inconclusive never promoted by AI/UI; eligible retest and conservative outcomes with reasons | Implemented components; integrated acceptance open |
| G04 Evidence, coverage and reports | Reproducible raw proof/provenance, honest skipped/failed/unrequested disclosures, redaction/format review, timestamped audit IDs/digests, export/integrity verification, explicit trust anchor/limits and audit failure/crash/recovery behavior | Partial; no universal confidence/immutability claim |
| G05 Shared durable lifecycle | CLI/API/web/headless service parity; persisted jobs/approvals/progress; budgets, cancellation, restart/reconciliation and no unsafe replay | Partial |
| G06 Supplied UI | All controls accounted for; exact design, responsive/visual/keyboard/accessibility/parity checks; truthful unsupported features; desktop default and external-asset policy | Partial |
| G07 Installation/deployment | Clean wheel/sdist/core/extras install and upgrade; catalog/payload resources; safe doctor/setup; supported platform/service modes, offline/partial failure, secrets, backup/restore and restart tests | Baseline CI smoke passes; complete acceptance open |
| G08 Candidate CI | Required Python 3.11–3.13 tests/static/build, browser and supported-platform checks green on exact release candidate; skips/limitations recorded | Baseline run green; future candidate must be checked again |
| G09 Release identity | Matching intended version/tag/commit, successful release workflow and verified expected index publication | OPEN; package baseline remains 0.11.16 Beta |
| G10 Documentation and decision | Updated state, capability/control/UI records, reproducible acceptance record, known risks/unsupported combinations and explicit release decision | OPEN |

Any unmet correctness, safety, user-visible workflow, report-honesty or installability requirement blocks a readiness claim. Deferred expansion does not. Change release scope explicitly with rationale and evidence; never hide a blocker by changing a status label. After acceptance: controlled dogfooding and reproducible report examples, then launch material and publication. Patch/minor versions reflect actual change scope; bumping to 1.0 is a release decision, not a document revision.

## 49. Engine architecture authority and specification boundaries

Keep [Engine v2 architecture/crosswalk](docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md) as the detailed architecture source, subordinate to this trajectory. E0 inventory is historical; E1 guards, E2 contracts, E3 scheduler primitives and initial E4 providers exist. E1 acceptance, durable mission-wide guarantees, broad E4 reconciliation, E5 shared lifecycle and E6 product/UI acceptance remain open. E7 autonomy, E8 multi-target and E9 expansion follow P6–P8.

Required contracts remain Mission/AuthorizationContext/Plan/Task/TaskAttempt/CapabilityManifest/ProviderRegistration/PolicyDecision/Approval/BudgetLedger/ExecutionContext/Observation/Finding/VerificationRun/EvidenceArtifact/AuditEvent/ReadinessSnapshot, delivered only where implemented and tested. Local process, session, API, browser, cloud SDK and local analysis are separate execution kinds—not automatically supported transports. No manifest, AI agent, plugin or browser becomes a second authority.

## 50. Previous-roadmap reconciliation and retained scope

The complete pre-rewrite text is retained in [Git at the inspected baseline](https://github.com/andreipath26/WHAXON-AI-Forensics/blob/6fa1fa5f9bcff9b7afffb87ca908b0f78562fa3b/WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md). No duplicate 296 KB archive is added to the working tree. Its detailed requirements remain reference material where not superseded below; its priorities, estimates, current-state assertions and implementation instructions are superseded by this file. Detailed future scope is retained without enabling it or turning it into a v1.0 prerequisite.

| Previous section(s) | Disposition and destination |
|---|---|
| Foundations, §0, engineering rule | Consolidated into §0 and P0–P8; five principles and dependency-driven work retained |
| §§1–4 | Completed phase/migration/small-fix history → baseline/changelog; no rebuild queue |
| §§5–6, 10 | Revalidate medium/large/AI gaps against source; correctness/durable bounds → P1/P2, broader AI/objectives/streaming → P8 |
| §§7, 39 | Tool candidates/substitutions and harness requirements → P2 portfolio reconciliation/P8 admission; quotas, old totals and fixed estimates retired |
| §§8–9 | Cloud and platform scope → P3 supported-platform acceptance/P8 typed expansion; old Kali-only assumptions superseded |
| §§11–12 | Obsolete time/version schedules retired; evidence-based gates replace session forecasts |
| §§13–16 | Exclusions/invariants → §0/§4; companion index → docs index; MCP/competitor/vendor references are research, not dependencies or facts to repeat without rechecking |
| §§17–18 | Solo validation → P1; team/MCP/enterprise → P8. Old “solo complete” and MCP-first priorities superseded |
| §19 | Supplied UI integration → P4. Old redesign alternatives/effort proposals retired; legacy designs preserved |
| §20 and remediation addendum | Narrow existing retest/report correctness → P1/P5; full business/remediation platform → P8; old PTaaS-urgent priority retired |
| §§21–22, 25 | Report fixes/session diaries/PR plans → historical Git/changelog; current report acceptance → P1/P5/G04 |
| §§23–24 | Adversarial evidence/scope/prompt-injection concerns → P1/P2/P6; speculative triage/research → P8, not new implemented capabilities |
| §26 | Programme policy/ingestion/browser/differential analysis/reporting → P6 and detailed bounty design; partial primitives remain implemented, full subsystem deferred |
| §§27–31 | No numbered sections existed in the baseline; no scope inferred |
| §32 | Solo chain → P5; validation/coverage/retest → P1; business logic/browser/AIRT conditional/deferred → P6/P8. Three-tab/UI restructure and fixed six-tool quota superseded by supplied-design/no-expansion gates |
| §33 | Trust Layer → P1; reproduction/evidence/coverage → G03/G04; local/privacy constraints → P3/P8. No simplistic response-change=fixed or universal confidence claim |
| §34 | Solo foundation/launch/versioning → P5/§38; stale remaining-session estimates and earlier sequencing retired |
| §35 | Portfolio R&D remains separate/post-foundation; do not restore excluded adversary archive or add portfolio products as WHAXON modules |
| §36 | Existing passive recon → baseline/P5; bounded enrichment and new data providers → P8 |
| §37 | Graph/hints/governance/A2B/full remediation hypotheses → P8 |
| §38 | Preserved and consolidated as G01–G10 above |
| §§40–41, 47 | Dependency manifest/doctor/setup/readiness/four existing UI states → P3/P4; old provisional module layouts and branch-only status snapshots superseded by actual source |
| §§42–44 | Multi-target and measured competition → P7; existing UI and solo release prerequisite retained |
| §§45–46 | Bounty phases/campaign autonomy/transport and evidence requirements → P6; older unconditional approval or no-autonomy statements superseded by exact activated envelope |
| §48 | Full capability inventory → P0/G01; shared headless/deployment/transport acceptance → P2/P3/§38 |
| §§49–50 | Engine specification → §49/P2; E0 findings are historical and must not reopen already-fixed defects |
| §51 | Full Metasploit/Armitage integration → P8 and its detailed design; current RPC/session primitives retained |
| §52 | Existing-portfolio audit, provenance/report/readiness contracts and bounded discovery/gap analysis → P0/P2; broader candidate onboarding/upstream monitoring → P8 and its detailed design. No competing manifest/scheduler or automatic upstream changes |

When a historical requirement is ambiguous or conflicts with a later approved decision, record a decision at the affected gate before implementation. Do not silently drop scope, treat historical prose as current evidence, or restart obsolete plans.
