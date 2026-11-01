# WHAXON Tool Intelligence & Controlled Onboarding

**Status:** Architecture specification — implementation queued behind Engine v2 dependency gates  
**Scope:** andreipath26/WHAXON-AI-Forensics  
**Authority:** Roadmap §0 and §52; Engine v2 architecture crosswalk

## 1. Purpose

WHAXON needs a repeatable way to understand tools it already integrates and tools it may add later. A catalog entry or adapter is not proof that WHAXON exposes the upstream tool's full capability set. An upstream feature is not proof that WHAXON implements, validates or is permitted to execute it.

Tool Intelligence provides two entry points:
- **Audit portfolio:** inspect installed/registered tools, adapters, transports and providers; compare upstream functionality with WHAXON's actual implementation and verification.
- **Research candidate:** investigate a proposed tool from authoritative sources; determine distinct value, overlap, integration cost, risk and a controlled onboarding path.

The subsystem produces evidence-backed reports and proposals. It does not silently expand execution authority.

## 2. Architectural placement

Tool Intelligence belongs beside the Engine v2 capability registry and provider resolver. It is not a replacement and must not create a parallel manifest, scheduler, policy engine or execution path.

Portfolio audit and candidate intake share:
discovery → source research → capability extraction → normalization → gap/overlap analysis → compatibility/risk assessment → versioned report → operator decision → integration → validation.

The implementation may split responsibilities into modules for discovery, research, documentation ingestion, extraction, gap analysis, compatibility, risk, onboarding and reports. These are logical boundaries, not a mandate to create every file independently.

## 3. Shared pipeline

### 3.1 Discovery

For the existing portfolio, collect:
- catalog records and aliases;
- built-in and entry-point adapters;
- session transports, RPC integrations and non-CLI providers;
- executable identity/version and bounded readiness checks;
- dispatch wiring, parser/normalizer, evidence path and interface exposure;
- tests and the exact version/platform they cover.

For a candidate, capture canonical identity, publisher, official repository/docs, release channel and candidate version. Discovery must not operationally exercise the candidate.

### 3.2 Source-backed research

Prioritise official documentation and API specifications, official source/tagged releases, release notes/advisories/support matrices, maintainer statements and authoritative package metadata. Community sources are supplementary and labelled as such.

Record URL, source type, retrieval date, relevant version, extracted claim, confidence and contradictions. Unknown claims remain unknown. Research licensing, redistribution, maintenance, supported platforms, dependency footprint, privilege, credential model, remote services and supply-chain risks.

### 3.3 Capability extraction and normalization

Extract capabilities into the existing Engine v2 model with stable IDs independent of executable names. Record version/edition constraints and source provenance for each material claim.

Useful sources include CLI version/help/subcommand and documented machine-readable introspection; REST/OpenAPI descriptions and authentication schemes; JSON Schema; MCP tools/list metadata; Python package metadata/entry points; plugin/module inventories; and CycloneDX SBOM/component metadata.

These are evidence sources, not trust roots. MCP annotations are hints, not authorization. OpenAPI/JSON Schema describes an interface but does not prove safe behavior or WHAXON implementation. CycloneDX complements but does not replace the capability manifest.

### 3.4 Gap and overlap analysis

For every upstream capability, classify WHAXON status as absent; implemented but not registered; registered but not dispatchable; dispatchable but not exposed; partial; implemented but untested; tested in a named environment/version; verified and ready; intentionally excluded; deprecated or incompatible.

Identify duplicate capabilities, existing alternatives, migration impact, parser/evidence gaps and distinct value. Never count an upstream feature as a WHAXON feature merely because the tool supports it.

### 3.5 Compatibility and risk

Assess runtime and OS/architecture support, target/protocol coverage, authentication, session/transport model, dependencies, licensing, maintenance, API stability, concurrency, resource use, cancellation, idempotency, output stability and evidence quality.

Classify side effects and impact. Unknown impact or uncertain authorization is denied or sent for explicit review. Candidate safety labels are untrusted until independently checked.

## 4. Capability manifest additions

Extend the canonical Engine v2 manifest; do not create a second schema.

| Dimension | Required information |
|---|---|
| Identity | Stable provider/tool ID, publisher, upstream repository, version and supported range |
| Capability | Stable capability ID, operation, family and deprecation |
| Interface | CLI, library, REST/OpenAPI, RPC, MCP, plugin, session or other transport |
| Schemas | Versioned typed inputs/outputs, validation and compatibility |
| Applicability | Targets, protocols, platforms, architectures, authentication/session requirements |
| Prerequisites | Dependencies, permissions, environment and secret references |
| Behavior | Preconditions, postconditions, state changes, external effects and impact |
| Execution | Timeout, cancellation, concurrency, resource/rate limits, idempotency and reconciliation |
| Evidence | Raw formats, parser/normalizer versions, provenance, redaction and retention |
| Readiness | Capability-specific state, environment, verification time and evidence |
| Provenance | Source URLs/version, retrieval time, confidence and deprecation |

Suggested readiness states: discovered, researched, installed, registered, smoke-tested, lab-validated, verified, degraded and unsupported. Attach readiness to a capability and environment/version. A tool-level available boolean is insufficient.

**Trust invariant:** a manifest describes a capability; it never grants permission. Engagement/bounty policy and runtime authorization remain separate and deterministic.

## 5. Tool Capability Report

Each assessment creates an immutable, versioned report; revisions supersede rather than overwrite. Include:
1. Executive decision and assessment scope.
2. Identity, version, publisher and provenance.
3. Source-backed upstream capability inventory.
4. WHAXON catalog/provider/adapter/dispatch/exposure inventory.
5. Gap and overlap matrix.
6. Compatibility, prerequisites, licensing and maintenance.
7. Security, side-effect, privilege, credential and data-handling assessment.
8. Evidence/parser/normalization implications.
9. Required code, schema, migration and service/UI changes.
10. Test and controlled-lab plan.
11. Recommendation: integrate, extend, replace, defer, reject or investigate.
12. Unknowns, confidence and acceptance criteria.

Explicitly separate upstream capability, WHAXON implementation, WHAXON verification/readiness and current authorization to execute.

## 6. Existing portfolio reconciliation

The first audit reconciles data/tools.json; built-in and Python entry-point adapters in adapters/registry.py; adapters/base.py; actual runner dispatch and dependency checks; session transports/RPC providers; CLI/API/UI exposure; parser/evidence paths; and tests.

Detect catalog-only, adapter-only, duplicate, stale, missing-binary, unsupported-transport, unreachable-dispatch, parser-gap and advertised-but-unverified cases. Preliminary baseline inspection found catalog/adapter discrepancies; E4 must generate the complete mismatch set rather than assume counts from a partial inspection.

Migration is additive and compatibility-preserving. Keep ToolCatalog, existing parsers and ToolRunner behind a bridge until manifest-backed provider resolution passes regression tests. Do not silently drop or rename definitions.

## 7. Candidate onboarding lifecycle

Persist explicit states:

| State | Meaning |
|---|---|
| proposed | Candidate and reason recorded |
| researched | Source-backed upstream/operational research completed |
| assessed | Gap, overlap, compatibility and risk completed |
| approved_for_implementation | Operator accepts bounded proposal; not installation/execution permission |
| integrated | Provider, schemas, parser/evidence path and service wiring implemented |
| validated | Declared tests passed with environment/version evidence |
| enabled | Available for deterministic resolution, still subject to runtime policy |
| rejected | Declined with rationale |
| deprecated | Retired with migration/replacement details |

Record actor, timestamp, report version, decision and evidence on every transition. Approval for implementation is not approval to install, load plugins, use credentials or execute. Decisions are revocable. Material upstream changes trigger reassessment and may invalidate readiness.

## 8. Safe discovery and operational boundary

Discovery is read-only and bounded: inspect local metadata, entry points, executable identity/version and documented help/list commands; use allowlisted introspection with timeout/output/resource limits; research public docs, source, releases, advisories and licensing.

Discovery must not run scans, exploits, listeners, post-exploitation, arbitrary RPC/session commands or downloaded code; install/upgrade packages; load/enable plugins; use credentials; contact arbitrary endpoints; or alter system state.

Each later install, plugin load, credential use, networked test or consequential validation needs separate explicit approval, a bounded plan and deterministic policy authorization. Remote descriptions, MCP annotations, schemas and generated manifests are untrusted. AI can extract and recommend, not authorize, enable or execute.

## 9. Continuous upstream monitoring

After provenance and registry contracts stabilize, compare releases, version support, capability additions/removals/deprecations, API/schema/output changes, plugins, advisories, ownership/maintenance, platform and licensing changes.

Create versioned delta reports and proposed manifest/parser/test updates. Never auto-upgrade, change provider selection, load plugins, enable or execute. Affected readiness becomes stale until revalidated.

## 10. Dependencies and implementation sequence

| Stage | Work | Gate |
|---|---|---|
| Architecture | Specify pipeline, trust boundary, report and acceptance | No competing contracts |
| E1 | Close current correctness/security blockers | Scope, DNS, session, RPC/TLS, recovery and evidence safety |
| E2 | Define manifest, provenance, readiness, report and lifecycle contracts | Shared versioned domain model and compatibility façade |
| E3 | Persist reports/lifecycle events; later schedule monitoring | Durable leases, idempotency, cancellation and recovery |
| E4 | Reconcile portfolio; migrate manifests; local discovery, extraction and gap analysis | Deterministic registry/provider resolution and regression |
| E4/E5 | Candidate research and operator-reviewed onboarding | Shared services and auditable transitions |
| After registry stabilizes | Upstream monitoring and revalidation | Provenance, readiness and durable scheduler |
| E6 onward | Expose only implemented, verified, authorized capabilities | Supplied UI and release gates |

Do not move ahead of E1, bypass E2/E3 contracts, delay solo v1.0/UI work, or introduce a second scheduler/manifest/policy implementation.

## 11. Proposed logical module boundaries

Possible modules:
- intelligence/discovery.py — safe local portfolio discovery;
- intelligence/research.py — source collection and version-aware research;
- intelligence/documentation.py — docs/spec ingestion and provenance;
- intelligence/capability_extractor.py — normalized capability claims;
- intelligence/gap_analyzer.py — upstream/WHAXON comparison;
- intelligence/compatibility.py — platform/version/schema fit;
- intelligence/risk_assessment.py — side effects, privilege and trust;
- intelligence/onboarding.py — persisted candidate lifecycle and decisions;
- intelligence/reports.py — versioned reports and deltas.

Exact paths are implementation decisions. Modules consume canonical contracts and shared services; they do not own execution, authorization, scheduling or a second registry.

## 12. Acceptance test matrix

- Full reconciliation across catalog, adapters, transports, dispatch, interfaces and tests.
- Detection of catalog-only, adapter-only, duplicate, stale and unreachable entries.
- Safe discovery without operational execution or system mutation.
- Reproducible reports from versioned source-backed evidence.
- Explicit upstream/implemented/tested/authorized separation.
- Compatibility and licensing/maintenance risk detection.
- Malicious descriptions, malformed schemas, prompt injection and untrusted annotations cannot execute or grant permission.
- No automatic install, upgrade, plugin load, credential use or operational invocation.
- Auditable/revocable transitions and stale-report invalidation.
- Upstream drift reports without runtime changes.
- New provider registration without mission, policy, scheduler or evidence core rewrites.
- Existing catalog, adapter, runner, CLI/API and end-to-end regressions remain green.

## 13. Definition of done

An operator can audit the current portfolio or assess a new candidate and receive a reproducible, source-backed capability, gap, compatibility and risk report with an implementation proposal. Approved providers are integrated and validated through the same versioned Engine v2 contracts as existing and future tools. Discovery never silently becomes executable authority.
