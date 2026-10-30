# Dependency readiness and guided installation

## Scope and status

This implementation adds dependency diagnostics, deterministic remediation planning, a tightly allowlisted Python-package installer, durable operation tracking, readiness history, authenticated web APIs, and the first UI integration in the existing Diagnostics page.

The Diagnostics page is the canonical entry point. Its four states are:
1. Environment overview.
2. Dependency inventory.
3. Guided fix / plan review.
4. Installation progress and post-install verification.

The implementation reuses the existing `/ui-v2/diagnostics` page shell and design tokens. It does not add navigation or a replacement design system.

## Diagnostics

Run:

```bash
whaxon doctor
whaxon doctor --json
whaxon doctor --core-only
whaxon doctor --check python
whaxon doctor --verify
whaxon doctor --snapshot
whaxon doctor --drift
```

The versioned JSON report includes runtime details, active interpreter and virtual-environment state, required Python package metadata/import checks, optional extras, and external executable discovery from the packaged tool catalog.

`--verify` runs only manifest-curated, bounded external-tool version probes. It does not run arbitrary tool commands or target scans.

### Status meanings

- `READY`: the declared Python minimum is met and the package import specification is resolvable, or the runtime meets the Python minimum.
- `MISSING`: a distribution or executable could not be found.
- `INCOMPATIBLE`: an installed package or Python runtime is below the declared minimum.
- `BROKEN`: package metadata/import or a required packaged resource could not be read.
- `DETECTED`: an external executable resolves on PATH but has not passed a trusted version probe.

An overall `BLOCKED` result means a required runtime/package/resource is not READY. `DEGRADED` means optional integrations or external tools are missing or unverified. Optional tools do not block unrelated core functionality.

Diagnostics themselves do not install software, invoke package managers, access the network, use privilege escalation, or change PATH. Explicit external verification is a separate action.

## Manifest and policy

The packaged source of truth is `src/whaxon/data/dependencies.json`. It records the Python runtime, core packages, optional extras, profiles, curated external-tool probes and installation policy.

Automatic installation is enabled only for manifest-listed `python-package` dependencies. External security tools remain manual-only until their platform-specific installation sources and functional verification contracts are curated. The installer independently enforces the manifest policy; the UI cannot override it.

## Remediation preview

Generate a read-only plan:

```bash
whaxon doctor --plan
whaxon doctor --plan --check textual
```

A plan includes a deterministic plan ID, selected dependency, exact proposed argument array and display command, package source, network/privilege impact, virtual-environment requirement, and whether automation is enabled. A plan is not authorization. No command is run while preparing it.

The plan ID is bound to the current environment, manifest and action details. If those change, the previous approval is rejected.

## Explicitly approved Python-package installation

For an eligible package, first review the complete plan, then run:

```bash
whaxon doctor --install --check textual --approve PLAN_ID
```

Replace `PLAN_ID` with the exact ID from the reviewed plan.

The installer:
- Requires an activated Python virtual environment; it will not modify a system Python installation.
- Installs only a Python distribution declared in the packaged dependency manifest.
- Enforces the manifest's `automatic_installation_enabled` and allowed-kind policy.
- Uses the active interpreter's pip with isolated pip configuration and a fixed official PyPI index.
- Accepts binary wheels only; it does not execute source build scripts.
- Does not use a shell, sudo/admin elevation, or user-supplied executable/arguments.
- Has a 15-minute timeout and supports cancellation.
- Re-checks the installed distribution version and import after installation. A pip exit code of zero is not sufficient.
- Writes a local JSONL audit record under `~/.whaxon/audit/dependency-install.jsonl` with restrictive file permissions where supported.

**Important package impact:** pip may install or update transitive dependencies required by the approved package. The plan identifies this behavior, the configured PyPI source, and the exact command before approval. The operation is not a fully hash-pinned, offline-reproducible deployment. Do not use it where a locked, hash-verified software supply chain is mandatory.

## Web API and operation lifecycle

The authenticated API exposes:
- `GET /api/dependencies` — read-only diagnostics.
- `POST /api/dependencies/verify` — explicit curated version probes.
- `POST /api/dependencies/plan` — read-only plan preview.
- `POST /api/dependencies/install` — queues an exact plan-ID-approved package operation and returns an operation ID.
- `GET /api/dependencies/install/<operation-id>` — operation state, progress and verification result.
- `POST /api/dependencies/install/<operation-id>/cancel` — request cancellation.
- `POST /api/dependencies/snapshots` and `GET /api/dependencies/history` — local readiness history.
- `GET /api/dependencies/drift` — compare current readiness with the latest snapshot.

Operation state is stored under `<data-dir>/.whaxon/dependency-operations/` with restrictive permissions where supported. Per-dependency locks prevent concurrent installs; periodic progress updates support stale-worker detection. Cancellation terminates the package-manager process where possible.

The worker currently runs as a background thread in the web process. A process crash can interrupt an install; the persisted operation will be marked interrupted after its heartbeat expires. This is not a distributed job queue and does not guarantee survival across process restarts.

## Readiness snapshots and drift

The CLI supports `--snapshot` and `--drift`. History is bounded to 100 snapshots and stored under `<data-dir>/.whaxon/dependency-readiness.json`. Snapshots omit the current working directory and raw executable paths; paths are represented by one-way fingerprints so drift can be detected without persisting personal directory names.

## Failure recovery

A failed, timed-out or interrupted pip operation may have partially changed the active virtual environment. WHAXON does not claim rollback. Re-run `whaxon doctor`; if the environment is inconsistent, recreate the virtual environment and reinstall the approved dependency set. Audit and operation records include outcome and recovery guidance.

## Remaining deployment gates

This feature is not considered production-deployable until all of the following are verified:
- Full CI passes on Python 3.11, 3.12 and 3.13: Ruff, mypy, full pytest, browser tests, distribution build, metadata validation and clean-wheel smoke test.
- The manifest, tool catalog and required payload resources are present in both wheel and sdist.
- Clean installation and operation are tested on Windows, macOS and supported Linux distributions, including no-root and offline cases.
- Every external-tool readiness claim is backed by a curated version and functional smoke-test contract.
- Resource paths, conflicting binaries, writable locations and package-manager availability are checked without weakening read-only diagnostics.
- Installation artifacts and transitive dependencies have a documented integrity/pinning strategy before any claim of reproducible or high-assurance installation.
- Responsive behavior, keyboard navigation, screen-reader announcements, cancellation races, empty/error/loading states and all UI-to-API flows pass browser regression tests.
- Worker restart behavior, concurrent operations, lock recovery, cancellation and partial-install recovery are validated under realistic deployment process models.

Until these gates pass, keep the pull request in draft and do not publish this feature as a finished product update.


## Evidence principle and audit lifecycle (mandatory)

WHAXON follows five mandatory operating principles: deterministic plans, explicit informed consent, bounded execution, independent verification, and **leave evidence**. Evidence is the accountability layer that makes the first four independently enforceable.

For dependency readiness, the audit lifecycle must cover:
- Plan created or regenerated: plan ID, canonical digest, manifest/policy version, environment binding, exact proposed action and impact disclosure.
- Approval or rejection: actor, decision, timestamp, exact plan digest, approval context and expiry/revocation where applicable. A submitted plan ID alone is not proof that an informed approval occurred.
- Action lifecycle: queued, started, parameters actually passed, process identity where available, progress/state transitions, cancellation, timeout, exit/result and finish time.
- Verification: verifier identity/version, inputs, checks performed, observed distribution/version/import state, evidence digest and explicit pass/fail/inconclusive outcome.
- Recovery: trigger, diagnosis, actions recommended or taken, operator decision, resulting state and follow-up verification.
- Exceptional paths: denied approval, stale/changed plan, audit failure, worker crash/interruption, lock recovery and partial installation.

Events must share stable plan, approval, operation and dependency identifiers so an auditor can reconstruct the complete sequence. Store append-only records with restrictive access, secret redaction and minimal personal data. Add a verifiable integrity mechanism (for example, a hash chain with a documented trust anchor); append-only JSONL and filesystem permissions alone do not prove tamper-evidence. Provide an integrity-check/export path. Never report a consequential operation as fully successful when required evidence could not be persisted or verified.

**Current implementation boundary:** the installer now records plan creation, plan-ID approval submission, action start and terminal outcomes in a sequenced SHA-256-linked local JSONL chain. The chain is checked before appending and can be verified through `GET /api/dependencies/audit`; corruption fails closed. This is tamper-evident against partial modification or reordering, not immutable against an attacker who can rewrite the complete file. The current web/CLI interface does not provide a verified human identity or cryptographic proof that the plan was displayed and understood. The chain has no independently stored trust anchor, and writers are serialized with a cross-process file lock. The lack of an independently stored trust anchor remains a deployment blocker for stronger audit assurance; do not describe the ledger as tamper-proof or complete.
