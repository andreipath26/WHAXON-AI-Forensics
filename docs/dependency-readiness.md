# Dependency readiness and guided installation

## Scope and status

This implementation adds dependency diagnostics, deterministic remediation planning, a tightly allowlisted Python-package installer, single-package and profile-batch operation tracking, readiness history, authenticated web APIs, and a first-run profile planner in the existing Diagnostics page.

The Diagnostics page is the canonical web entry point; `whaxon setup` is the CLI first-run entry point. Both expose Core, Standard, Full and Custom profiles. The operator can review a read-only plan, explicitly approve the complete eligible Python-package batch, and track the sequential operation through verification. Individual package review remains available. External-tool OS packages are not part of the Python profile batch. A separate CLI flow supports exact-plan-approved apt/Homebrew installation for Nmap, Gobuster, SQLmap and ffuf, plus Nuclei through Homebrew only; unsupported combinations remain manual.

Its four states are:
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

The versioned JSON report includes runtime details, active interpreter and virtual-environment state, required Python package metadata/import checks, optional extras, and external executable discovery from the packaged tool catalog. Mandatory packaged validation payloads are checked for presence and non-empty contents. External executable records include the selected path, distinct PATH candidates, a local filesystem-metadata identity fingerprint, and a PATH-ambiguity flag. This fingerprint helps detect a changed local file; it is not a publisher signature, content hash, or supply-chain attestation.

`--verify` runs only manifest-curated, bounded external-tool version probes. It does not run arbitrary tool commands or target scans.

### Status meanings

- `READY`: the declared Python minimum is met and the package import specification is resolvable, or the runtime meets the Python minimum.
- `MISSING`: a distribution or executable could not be found.
- `INCOMPATIBLE`: an installed package or Python runtime is below the declared minimum.
- `BROKEN`: package metadata/import or a required packaged resource could not be read.
- `DETECTED`: an external executable resolves on PATH but has not passed a trusted version probe. Multiple distinct PATH candidates are explicitly flagged for operator review.
- `BROKEN`: an executable resolves but its filesystem identity cannot be inspected; WHAXON will not run its version probe.

An overall `BLOCKED` result means a required runtime/package/resource is not READY. `DEGRADED` means optional integrations or external tools are missing or unverified. Optional tools do not block unrelated core functionality.

Diagnostics themselves do not install software, invoke package managers, access the network, use privilege escalation, or change PATH. Explicit external verification is a separate action.

## CLI first-run setup

Use `whaxon setup` to inspect the host and build a deterministic capability-profile plan without requiring the browser Diagnostics page:

```bash
# Read-only profile previews
whaxon setup --profile core
whaxon setup --profile standard
whaxon setup --profile full
whaxon setup --profile custom --capability core --capability tui

# Machine-readable preview
whaxon setup --profile core --json
```

The preview prints the exact plan ID and selected dependency actions. A profile selection does not install packages or grant permission. After reviewing the complete plan, the eligible Python-package batch can be approved explicitly:

```bash
whaxon setup --profile core --install --approve PLAN_ID
```

Replace `PLAN_ID` with the exact ID from the plan you reviewed. The batch is restricted to manifest-allowlisted Python packages, requires an active virtual environment, runs sequentially and stops on failure or cancellation. Already completed package operations are not rolled back.

External tools are a separate operation. Preview a curated OS-package plan, then approve that exact plan with explicit system-change consent:

```bash
whaxon setup --tool nmap
whaxon setup --tool nmap --install-tools --approve-tools PLAN_ID --allow-system-changes
```

Add `--allow-elevation` only when the reviewed plan requires a non-interactive privilege elevation. Automated OS-tool installation is limited to the supported apt/Homebrew mappings described above; other tools, distributions and platforms remain manual. The CLI does not install arbitrary catalog entries.

If a working `whaxon` command is already available, `whaxon setup --create-venv` can create a new `.venv` without overwriting an existing directory and prints activation instructions. Otherwise, create the virtual environment with Python's `venv` module before installing WHAXON.

For one dependency rather than a whole profile, `whaxon doctor --plan --check DEPENDENCY_ID` and the exact-plan `whaxon doctor --install --check DEPENDENCY_ID --approve PLAN_ID` path remain available. The older `whaxon install` command is a legacy apt-only installer; prefer `whaxon setup` for current guided setup.

## Manifest and policy

The packaged source of truth is `src/whaxon/data/dependencies.json`. It records the Python runtime, core packages, optional extras, profiles, curated external-tool probes and installation policy.

Python automatic installation is enabled only for manifest-listed `python-package` dependencies. External-tool installation uses a separate fixed package allowlist in `setup_installers.py`, exact-plan approval, explicit system-change consent, separate non-interactive elevation consent, shell-free package-manager invocation and trusted post-install version probes. The mapping is intentionally limited to apt on Debian/Ubuntu/Kali and Homebrew on supported macOS architectures; Windows package managers are detected for diagnostics only and remain manual because native Windows package IDs have not passed acceptance. Unsupported architectures and distributions remain manual even if a package manager binary is present. The UI cannot override the Python installer policy.

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
- `POST /api/dependencies/install` — queues an exact plan-ID-approved single-package operation and returns an operation ID.
- `POST /api/dependencies/install-batch` — queues an exact plan-ID-approved profile batch, restricted to manifest-allowlisted Python packages, and returns an operation ID.
- `GET /api/dependencies/install/<operation-id>` — operation state, progress and verification result.
- `POST /api/dependencies/install/<operation-id>/cancel` — request cancellation.
- `POST /api/dependencies/snapshots` and `GET /api/dependencies/history` — local readiness history.
- `GET /api/dependencies/drift` — compare current readiness with the latest snapshot.

Operation state is stored under `<data-dir>/.whaxon/dependency-operations/` with restrictive permissions where supported. Per-dependency locks prevent concurrent installs, including conflicts between single-package and profile-batch operations; periodic progress updates support stale-worker detection. Cancellation terminates the package-manager process where possible.

The worker currently runs as a background thread in the web process. A process crash can interrupt an install; the persisted operation will be marked interrupted after its heartbeat expires. This is not a distributed job queue and does not guarantee survival across process restarts.

## Readiness snapshots and drift

The CLI supports `--snapshot` and `--drift`. History is bounded to 100 snapshots and stored under `<data-dir>/.whaxon/dependency-readiness.json`. Snapshots omit the current working directory and raw executable paths; paths are represented by one-way fingerprints so drift can be detected without persisting personal directory names.

## Failure recovery

A failed, timed-out or interrupted pip operation may have partially changed the active virtual environment. WHAXON does not claim rollback. Re-run `whaxon doctor`; if the environment is inconsistent, recreate the virtual environment and reinstall the approved dependency set. Audit and operation records include outcome and recovery guidance.

## Remaining deployment gates

**Verified implementation and CI evidence (not full deployment acceptance):**
- CI run [#41307525558](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41307525558) passed Ruff, mypy, pytest and distribution build/metadata validation on Python 3.11, 3.12 and 3.13. Its clean Python 3.12 wheel smoke test exercised `whaxon doctor --json`; the sdist check verified the dependency manifest, tool catalog and payload files.
- Setup preview and virtual-environment smoke checks run on Ubuntu, macOS and Windows CI runners. Actual curated external-tool installation is exercised on Ubuntu/apt and Apple Silicon macOS/Homebrew, with trusted version probes and loopback-only functional checks for the selected tools.
- Restricted-host policy tests verify read-only planning when no supported package manager is present, manual-only apt plans without sudo, and rejection when elevation consent is missing.
- The manifest, packaged tool catalog and required validation payload resources are checked in wheel/sdist workflows.

**Still open; do not advertise as accepted or production-deployable:**
- Full clean-machine acceptance for each explicitly supported OS/distribution/architecture, including native Windows and WSL2 as separate environments. Windows package managers are diagnostic-only; their package IDs are not enabled for automatic installation.
- Physical offline-host acceptance, writable destination validation, resource integrity hashes, and a complete artifact/transitive-dependency integrity and pinning strategy.
- Full functional verification coverage for every advertised external-tool capability; the existing loopback checks cover only the selected curated tools and scenarios.
- Worker restart/recovery guarantees. The installer worker is a background thread in the web process; a process crash can interrupt an operation. Persisted state detects interruption but does not provide durable execution across restarts.
- Complete browser acceptance for responsive behavior, keyboard navigation, screen-reader announcements, cancellation races, empty/error/loading states and all UI-to-API flows.
- Independent audit trust anchoring and realistic failure/recovery acceptance.

These are roadmap/release gates, not an instruction to keep a pull request in draft. The repository currently has no open pull request for this work. Do not publish dependency readiness as a finished production feature until the outstanding gates are closed with evidence.


## Evidence principle and audit lifecycle (mandatory)

WHAXON follows five mandatory operating principles: deterministic plans, explicit informed consent, bounded execution, independent verification, and **leave evidence**. Evidence is the accountability layer that makes the first four independently enforceable.

For dependency readiness, the audit lifecycle must cover:
- Plan created or regenerated: plan ID, canonical digest, manifest/policy version, environment binding, exact proposed action and impact disclosure.
- Approval or rejection: actor, decision, timestamp, exact plan digest, approval context and expiry/revocation where applicable. A submitted plan ID alone is not proof that an informed approval occurred.
- Action lifecycle: queued, started, parameters actually passed, process identity where available, progress/state transitions, cancellation, timeout, exit/result and finish time.
- Verification: verifier identity/version, inputs, checks performed, observed distribution/version/import state, evidence digest and explicit pass/fail/inconclusive outcome.
- Recovery: trigger, diagnosis, actions recommended or taken, operator decision, resulting state and follow-up verification.
- Exceptional paths: denied approval, stale/changed plan, audit failure, worker crash/interruption, lock recovery and partial installation.

Events must share stable plan, approval, operation and dependency identifiers so an auditor can reconstruct the complete sequence. Profile batches additionally record acceptance of the exact parent profile plan and a terminal batch outcome; each child package operation retains its own plan/action evidence. Store append-only records with restrictive access, secret redaction and minimal personal data. Add a verifiable integrity mechanism (for example, a hash chain with a documented trust anchor); append-only JSONL and filesystem permissions alone do not prove tamper-evidence. Provide an integrity-check/export path. Never report a consequential operation as fully successful when required evidence could not be persisted or verified.

**Current implementation boundary:** the installer now records plan creation, plan-ID approval submission, action start and terminal outcomes in a sequenced SHA-256-linked local JSONL chain. The chain is checked before appending and can be verified through `GET /api/dependencies/audit`; corruption fails closed. This is tamper-evident against partial modification or reordering, not immutable against an attacker who can rewrite the complete file. The current web/CLI interface does not provide a verified human identity or cryptographic proof that the plan was displayed and understood. The chain has no independently stored trust anchor, and writers are serialized with a cross-process file lock. The lack of an independently stored trust anchor remains a deployment blocker for stronger audit assurance; do not describe the ledger as tamper-proof or complete.


### Headless server support

WHAXON's CLI setup/diagnostics and production `whaxon serve` entry point are designed to run without a desktop session or terminal interaction. The Linux CI workflow removes DISPLAY/Wayland/session variables, executes setup and doctor, starts the Waitress server with stdin detached, and confirms an HTTP response on loopback. This does not replace remote deployment hardening: configure explicit credentials, TLS/reverse proxy, firewall rules, backups and a persistent protected data directory before network exposure.
