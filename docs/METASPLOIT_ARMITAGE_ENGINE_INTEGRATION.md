# Metasploit and Armitage — Engine Integration Design

**Status reviewed 2026-11-02:** Broader provider-level integration design and roadmap requirement; not fully implemented. A narrower Metasploit adapter, session operations and web API routes already exist on `main`. This document specifies the larger dynamic Framework/provider coverage and security guarantees; it must not be read as saying no Metasploit support exists.  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Architecture parent:** `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md`  
**Roadmap parent:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, §51  
**Historical baseline:** E0 static inventory at commit `71c3e8c2b73bf7f05bd0e064fa77c4aa81113802`; current implementation status must be checked against main and roadmap §51.

## 1. Product objective

Make the installed Metasploit Framework a first-class, dynamically discovered execution provider for WHAXON. WHAXON must be able to understand and orchestrate the supported capabilities of the actual connected Framework instance, not just call a narrow set of exploit, auxiliary and post modules.

Metasploit supplies the extensible security-testing and execution framework. Armitage contributes proven operator-workflow ideas: host/session visualization, attack candidate discovery, contextual session operations, pivot awareness and collaboration/deconfliction. WHAXON must combine those ideas with its own mission engine, deterministic authorization, evidence, verification, scheduler and supplied UI.

**Division of responsibility:**
- Metasploit owns its native modules, module semantics, Framework jobs, consoles, sessions, payload/handler mechanisms, plugins and native data.
- WHAXON owns mission intent, scope, policy, approvals, task graphs, provider selection, budgets, durable orchestration, evidence provenance, verification, reporting and operator experience.
- Armitage is a design reference, not a runtime dependency or a UI to clone.
- Metasploit Pro-only capabilities must never be assumed to exist in the open-source Framework. Detect edition and API capability, and implement WHAXON-native equivalents only where justified.

## 2. Architectural placement

Metasploit is a provider under Engine v2, not a second orchestration engine and not a collection of hard-coded entries in `data/tools.json`.

Target flow:

```text
CLI / supplied Web UI / API / headless
                |
        Shared application services
                |
          Mission Engine
   Plan -> Policy -> Approval -> Budget
                |
       Durable task scheduler
                |
     Capability / provider resolver
                |
        Metasploit provider
   +------------+-------------+
   |            |             |
Module       Runtime       Session &
intelligence lifecycle     maneuver
   |            |             |
   +------ Framework data ----+
                |
       Version-aware RPC bridge
                |
       Metasploit Framework
                |
   Events / observations / artifacts
                |
   WHAXON evidence + verification
                |
    mission graph / attack-surface view
```

The provider must use the existing versioned Engine v2 contracts: `Mission`, `AuthorizationContext`, `Plan`, `Task`, `Attempt`, `Manifest`, `Provider`, `PolicyDecision`, `Approval`, `Budget`, `ExecutionContext`, `Observation`, `Verification`, `Evidence`, `Audit` and `Readiness`.

The provider is responsible for adapting Framework-specific identifiers and semantics to these contracts. It must not bypass the shared scheduler, scope gate, policy engine, approval binding, audit or evidence service.

## 3. Framework capability coverage

Capability discovery is performed against the connected Framework version and actual RPC/API surface. No fixed module counts, static allowlists pretending to represent the installation, or assumptions that every version exposes identical methods.

### 3.1 Module families and intelligence

Discover and represent all installed and API-supported module families:
- auxiliary;
- exploit;
- post;
- payload;
- encoder;
- NOP;
- evasion.

For each module, capture a versioned metadata snapshot containing:
- canonical module type and full name;
- description, authors, references/CVEs and disclosure metadata where supplied;
- rank, reliability/stability/side-effect metadata where supplied;
- supported platform, architecture and target list;
- required, optional, advanced and evasion options, types, defaults and constraints;
- check support and check result semantics;
- compatible payloads and target-compatible payloads;
- compatible session types for post modules;
- prerequisites, dependencies and Framework version constraints;
- provider-reported availability and metadata retrieval time.

Module metadata is advisory input, not authorization. A high rank or successful check does not authorize execution. Unknown or conflicting metadata must be treated conservatively.

### 3.2 Module search, recommendation and validation

Provide structured search and filtering across module families, references, CVEs, platform, architecture, service/product, target compatibility and capabilities.

Build an Armitage-inspired **Find Attacks** workflow, extended beyond simple service-to-exploit matching:
1. correlate WHAXON asset/service observations and their confidence/provenance;
2. discover matching Framework modules and non-Metasploit validation providers;
3. check platform, version, target, options, prerequisites and compatible payload/session requirements;
4. distinguish confirmed evidence, plausible match and weak fingerprint correlation;
5. identify safe checks or independent non-invasive verification methods where available;
6. present candidates with reasons, limitations, impact class and missing information;
7. require policy evaluation and approval before any consequential action;
8. record the actual result and update the asset/vulnerability knowledge graph.

A module existing or matching a service banner is never proof that a vulnerability exists. A module's `check` method may be incomplete, unsupported or inconclusive; its result must be represented with those limitations and independently corroborated where possible.

### 3.3 Execution, jobs and consoles

Replace fixed sleeps and console-text parsing as the normal lifecycle mechanism with structured RPC methods wherever available.

Required operations:
- validate and prepare a module request;
- dispatch and persist Framework job/console identifiers;
- list, inspect, wait for and stop jobs;
- collect structured progress/output and bounded console output;
- classify success, failure, timeout, cancellation and unknown outcome;
- create, own, interact with, detach and destroy consoles;
- enforce concurrency, resource limits, output caps and deadlines;
- reconcile jobs after WHAXON restart before any retry;
- preserve the exact module metadata snapshot, normalized options and task-attempt association.

A lost RPC response after dispatch is an **unknown outcome**, not proof that the operation did not start. Reconcile Framework jobs, sessions and events before deciding whether retry is safe. Exploit and handler operations must never be blindly replayed.

Console interaction remains a bounded compatibility path for features without a supported structured API. It must have explicit ownership, command allowlisting or typed wrappers, output limits, timeout, audit and authorization. It must not become a free-form command path for the AI planner.

### 3.4 Payload and handler lifecycle

Model payloads and handlers as distinct capabilities with explicit relationships:
- staged/single payload semantics and platform/architecture compatibility;
- compatible payload selection for a particular module and target;
- handler configuration, start, status, stop and cleanup;
- correlation between module execution, handler, Framework job and resulting session;
- cleanup and orphan detection following failure or cancellation.

Payload generation, delivery, handler deployment and session establishment are consequential operations and must be separately authorized. A handler's listener configuration must be constrained to approved interfaces/ports and deployment policy.

### 3.5 Sessions and Meterpreter

A session is a durable Framework resource, not merely an integer ID or command string.

Session identity must include:
- Framework instance ID and Framework version;
- Framework-local session ID and stable UUID where available;
- type, platform, architecture and transport/tunnel metadata;
- peer/target host, local endpoint and route ancestry;
- originating module, payload, job and WHAXON task/attempt;
- user/privilege context where safely available;
- creation, last-seen and lifecycle state;
- discovered capabilities/extensions and their provenance.

Discover session capabilities by session type, platform, Framework version and loaded extensions. Provide typed operations where supported for:
- system and identity information;
- filesystem metadata and explicitly authorized file collection;
- process inventory and bounded process interaction;
- network interfaces, routes and connection information;
- channels and interactive I/O;
- supported Meterpreter extension capabilities;
- shell command execution as a separate, lower-level compatibility operation;
- session backgrounding, interaction and termination.

Do not conflate shell commands with Meterpreter APIs. Long-running operations require streaming, cancellation, output caps and durable ownership. Revalidate live session identity, host, route ancestry, task ownership and scope immediately before every consequential operation. An unknown or changed peer/host must fail closed.

### 3.6 Framework data and artifacts

Integrate supported Framework database services and records:
- workspaces/projects where exposed;
- hosts and host attributes;
- services and observed versions;
- vulnerabilities and references;
- credentials and login records;
- loot and artifact metadata;
- notes and other supported records.

WHAXON remains the canonical mission/evidence authority. Preserve Framework source IDs, workspace, instance identity, timestamps and original provenance. Use idempotent synchronization and explicit conflict rules; never overwrite stronger WHAXON evidence with weaker imported data.

Credentials and secrets must be stored as protected secret references, not copied into plans, ordinary logs, UI payloads or unredacted reports. Loot ingestion must record source, size, media type, integrity hash, access policy and retention classification. Do not silently collect or exfiltrate arbitrary files.

### 3.7 Pivoting and network maneuver

Extend the existing pivot, route and port-forward components into one route-aware network model. Represent:
- pivot session and Framework instance;
- route/subnet and forwarding mechanism;
- local/remote endpoints and protocol;
- route ancestry and path to destination;
- creation owner/task, policy decision and approval;
- health, expiry, teardown and last validation.

Include supported port-forward and SOCKS capabilities only after API/version discovery. Validate authorization both when creating a route and when using it. A route through an authorized foothold does not automatically authorize the newly reachable subnet. DNS resolution, redirects and actual network destination must remain bound to the approved scope; this integrates with Engine v2's DNS/TOCTOU controls.

### 3.8 Plugins and extensibility

Discover installed Framework plugins and their exposed capabilities, but do not load or execute arbitrary plugins automatically. Plugin installation/loading is an administrative operation with explicit trust, version, provenance and approval.

New Metasploit capabilities should be added by manifests/provider adapters, not changes to the mission engine or scheduler. Support version-specific adapters and capability negotiation. Unsupported methods must be reported explicitly.

## 4. Armitage patterns to adopt

### 4.1 Attack-surface and session graph

Extend WHAXON's existing asset and pivot graph rather than create a duplicate graph. Represent hosts, services, findings, Framework instances, jobs, sessions, handlers and routes as linked entities. Preserve provenance and confidence for each edge.

Provide graph and table projections from the same canonical data model. Graph selection should expose contextual, policy-filtered operations; it must not bypass the planner or authorization service.

### 4.2 Find Attacks

Adopt Armitage's host/service-to-module recommendation concept, but improve it with evidence quality, module compatibility, check availability, impact classification, alternative validation methods, policy decisions and explainable recommendations. Recommendations are not automatic dispatch.

### 4.3 Contextual session operations

Use session type and discovered capability to show relevant operations. The UI must not show actions the backend/provider cannot actually perform. Every operation uses shared application services and the same approval, task and evidence lifecycle.

### 4.4 Pivot awareness

Display how routes change reachability and which session provides each path. Route reachability is not scope authorization. Re-evaluate the route and destination before execution.

### 4.5 Collaboration and deconfliction

Armitage's shared-session/deconfliction concept should inform a future multi-operator design. Engine v2 should establish session leases/locks, operation ownership, command serialization where required, shared event streams and conflict detection. This is a future capability; do not add distributed collaboration complexity before the solo durable scheduler is correct.

### 4.6 UI integration constraint

Do not clone Armitage's Java UI, introduce a second UI, or redesign the supplied WHAXON UI. Add backend contracts and connect only existing supplied UI pages/components when the relevant functionality is truly implemented. Hide unavailable capabilities rather than showing mock controls. Keep the legacy UI untouched.

## 5. AI, automation and playbooks

AI may propose module candidates, task graphs, parameter suggestions and follow-up work. It may not directly issue unrestricted RPC calls, console commands, shell strings or Meterpreter commands.

Every proposed action must become a typed task and pass:
- schema and module-option validation;
- deterministic scope and target authorization;
- customer engagement or bug-bounty policy;
- operation/module/session risk classification;
- impact, rate, time and resource budgets;
- approval bound to immutable plan/task digest, target, parameters, Framework version, policy version and expiry;
- runtime revalidation at dispatch and on session/route actions.

Replace fixed `WHAXON_MSF_AUTOCHAIN` behavior and its hard-coded post-module list with declarative, evidence-driven graph transitions. A newly created session may trigger discovery and recommendations, but must not silently trigger post-exploitation. Every follow-up task is independently authorized. Bounty policy remains separate from customer-pentest policy; a program prohibition overrides Framework capability.

Playbooks should be reusable, versioned task-graph templates with typed parameters, preconditions, policy requirements, rollback/cleanup behavior and evidence expectations. They should support partial completion and safe resume, not a blind linear macro.

## 6. MCP and external interoperability

Keep the native WHAXON provider as the source of truth. Evaluate MCP as an optional interoperability surface for selected, already-authorized WHAXON capabilities and for compatible external clients. MCP tools must call the same application services and policy gates; they must not expose a second bypass around them.

Before depending on any Metasploit MCP server, verify its current maintainer, release status, supported Framework versions, tool coverage, authentication, transport security and dangerous-action defaults. Treat it as an optional adapter, not as a replacement for full provider coverage or durable orchestration.

## 7. Security and deployment requirements

- Remove weak built-in RPC credentials; require explicit secret configuration.
- Verify TLS certificates and hostnames by default. Insecure TLS is explicit development-only configuration, visibly warned and rejected by production policy.
- Prefer loopback/private network binding; remote RPC is opt-in, authenticated, network-restricted and encrypted.
- Store credentials in secret references and rotate them without exposing values.
- Enforce least privilege and Framework instance identity.
- Revalidate target/session/route scope immediately before dispatch.
- Enforce per-operation side-effect classifications; unknown impact is denied or requires human review.
- Keep customer and bounty policies independent.
- Record auditable plan, approval, RPC operation, job/session/handler, route, output and evidence correlations.
- Support optional Framework absence, truthful readiness and dependency diagnostics.
- Support headless Linux/server deployments with no GUI, desktop or interactive console requirement.
- Bound RPC timeouts, output size, concurrency, memory and orphan cleanup.

## 8. Implementation gates and sequence

This work is subordinate to roadmap §0 and the Engine v2 E1–E9 dependency sequence. It must not bypass the supplied UI gate or solo v1.0 acceptance.

| Engine stage | Metasploit deliverable | Exit condition |
|---|---|---|
| E1 — correctness/security | TLS/auth defaults, session-host authorization, RPC error handling, blocking/fixed-wait correctness, scope/route validation, regression tests | Critical security and lifecycle defects closed |
| E2 — contracts | Framework instance, module metadata, option schema, job, console, handler, session, route, loot, secret and readiness contracts | Versioned contracts and compatibility tests |
| E3 — durable runtime | Job/session/handler ownership, leases, heartbeats, event correlation, cancellation, restart reconciliation | No duplicate replay; recoverable operations |
| E4 — provider/capabilities | Dynamic discovery, search, metadata, compatibility, module families, typed session and database services | New capability added without scheduler changes |
| E5 — shared services/headless | CLI/API/UI/headless access through same services | Same policy and lifecycle across interfaces |
| E6 — solo v1.0/UI | Expose only implemented Metasploit functions in supplied UI; accurate readiness and diagnostics | UI and release acceptance |
| E7 — bounded autonomy | Find Attacks, explainable recommendations, safe checks, declarative follow-ups/playbooks | Adversarial policy and evidence acceptance |
| E8/E9 — scale/expansion | Multi-target fan-out, multiple Framework instances, deconfliction/collaboration | Measured concurrency and isolation acceptance |

Do not start broad feature implementation before E1 security and recovery gates are closed. Parallel work is permitted only where contracts and ownership boundaries are stable.

## 9. Acceptance matrix

1. Detect Framework version, edition where determinable, API namespaces and actual module-family availability.
2. Search and retrieve metadata for each supported module family without hard-coded module totals.
3. Retrieve required/advanced options, targets, references, check support and compatible payload/session data.
4. Validate options and reject incompatible or incomplete requests before dispatch.
5. Execute approved lab auxiliary and exploit test cases; track structured job state to terminal outcome without fixed sleeps.
6. Start/stop a handler and correlate it to the originating task and any resulting session.
7. Discover shell and Meterpreter sessions and verify typed capability discovery.
8. Exercise bounded session operations, streaming, timeout, cancellation and closure in an isolated lab.
9. Import and reconcile supported host/service/vulnerability/credential/loot records with source provenance and secret redaction.
10. Create, inspect and tear down supported forwards/routes; prove route use cannot exceed scope.
11. Restart WHAXON during a Framework job/session and reconcile state without duplicate dispatch.
12. Prove unknown, prohibited, out-of-scope and unapproved module/session/route actions are denied, including AI-proposed actions.
13. Prove customer and bounty policy differences are enforced.
14. Prove TLS verification, secret storage, authentication failures and unsafe remote configurations are handled correctly.
15. Run headlessly without desktop dependencies and report optional dependency readiness truthfully.
16. Verify all UI exposure uses existing supplied design and hides unsupported capabilities.
17. Add a provider capability without changing mission engine, scheduler or evidence core.
18. Verify Framework/Pro-only features are not falsely advertised as open-source Framework capabilities.

## 10. Research references

The following primary references informed this design. API behavior must still be verified against the actual installed Framework version during implementation.

- Rapid7, [Metasploit RPC API](https://docs.rapid7.com/metasploit/rpc-api/) — RPC services, handlers, authentication and Framework connectivity.
- Rapid7, [Standard API Methods Reference](https://docs.rapid7.com/metasploit/standard-api-methods-reference/) — module execution and structured job/session methods.
- Rapid7, [Metasploit Framework overview](https://docs.rapid7.com/metasploit/msf-overview/) — module families and Framework concepts.
- Rapid7, [Metasploit codebase architecture](https://docs.metasploit.com/docs/development/get-started/navigating-and-understanding-metasploits-codebase.html) — modules, libraries, plugins and scripts.
- Rapid7, [How payloads work](https://docs.metasploit.com/docs/using-metasploit/basics/how-payloads-work.html) — staged/single payloads and handler relationship.
- Rapid7, [Running modules](https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html) — module search and execution concepts.
- Rapid7, [MessagePack RPC guide](https://github.com/rapid7/metasploit-framework/blob/master/docs/metasploit-framework.wiki/How-to-use-Metasploit-Messagepack-RPC.md) — Framework RPC usage.
- Armitage, [source repository](https://github.com/rsmudge/armitage) — original client and workflow reference. Armitage-derived features must be re-evaluated against current WHAXON requirements rather than copied wholesale.

