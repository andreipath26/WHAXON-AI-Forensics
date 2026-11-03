# Engine V2: Provider and Capability Abstraction

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
