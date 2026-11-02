# Dependency readiness and guided installation

**Status reviewed 2026-11-02:** implementation exists on `main`; this document records behavior and remaining acceptance requirements. CI run #41313223574 is a specific passing run from 2026-11-01, not a guarantee that every later commit or current HEAD passed. Deployment gates below remain open unless the master roadmap records closure with evidence.

## Scope and status

This implementation adds dependency diagnostics, deterministic remediation planning, a tightly allowlisted Python-package installer, durable operation tracking, readiness history, authenticated web APIs, and the first UI integration in the existing Diagnostics page.

The Diagnostics page is the canonical entry point. Its profile planner (Core, Standard, Full and Custom) expands the selected capabilities against the live dependency inventory and requests a read-only remediation plan. Each action is listed with its automation eligibility. The operator can explicitly approve the exact complete plan and queue a sequential batch of eligible Python-package installs; the shared operation panel displays progress, cancellation and verification. Individual remediation review remains available.

The batch endpoint revalidates the exact plan ID, manifest policy, active virtual environment and every action before queueing. It acquires per-dependency locks, runs packages sequentially through the existing bounded installer, stops at the first failure or cancellation, and records the result. Completed packages are not rolled back. External-tool OS packages use a separate exact-plan-approved CLI path with a deliberately narrow apt/Homebrew package allowlist; unsupported tools and hosts remain manual.

The Diagnostics page has these states:
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

The versioned JSON report includes runtime details, active interpreter and virtual-environment state, required Python package metadata/import checks, optional extras, and external executable discovery from the packaged tool catalog. It also checks that packaged validation payloads are present, reports distinct PATH candidates for external executables, and records a local filesystem-metadata identity fingerprint. That fingerprint is not a content hash, publisher signature or supply-chain attestation.

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

Python automatic installation is enabled only for manifest-listed `python-package` dependencies. External-tool installation is a separate CLI workflow using fixed package IDs, exact-plan approval, explicit system-change consent, separate non-interactive elevation consent, shell-free package-manager invocation and trusted version probes. The initial allowlist covers apt/Homebrew packages for Nmap, Gobuster, SQLmap and ffuf, plus Nuclei through Homebrew. The UI cannot override the Python installer policy.

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
- `POST /api/dependencies/install-batch` — queues an exact plan-ID-approved profile batch, limited to manifest-allowlisted Python packages, and returns an operation ID.
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

**Recorded implementation and CI evidence (not full deployment acceptance):**
- CI run [#41313223574](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41313223574) passed Ruff, mypy, 1,322 tests (14 skipped) and wheel/sdist metadata checks on Python 3.11, 3.12 and 3.13. Its clean Python 3.12 wheel smoke test exercised `whaxon doctor --json`, the packaged catalog/resources, scope policy and a local HTTP observation.
- Setup preview and virtual-environment smoke checks run on Ubuntu, macOS and Windows CI runners. Actual curated package installation is exercised on Ubuntu/apt and Apple Silicon macOS/Homebrew for Nmap, Gobuster, SQLmap, ffuf and Nuclei, followed by trusted version probes and selected loopback functional checks.
- Restricted-host tests cover no supported package manager, no sudo for apt, and missing elevation consent. These are policy tests, not proof of physical offline-host provisioning.
- Read-only diagnostics cover packaged payload presence, executable filesystem identity, PATH ambiguity and curated manager/OS/architecture support.

**Still open; do not advertise as accepted or production-deployable:**
- Broader package mappings and clean-machine acceptance across explicitly supported Linux distributions, native Windows and WSL2 (which must be treated as a separate Linux environment).
- Physical offline-host acceptance, writable destination validation, resource integrity hashes, and a complete artifact/transitive-dependency integrity and pinning strategy.
- Complete functional verification for every advertised external tool; current loopback checks cover selected tools and scenarios only.
- Durable worker restart/recovery. Installation work runs in a background thread in the web process; a crash can interrupt an operation. Persisted state detects interruption but does not guarantee execution survives process restarts.
- Complete browser acceptance for responsive behavior, keyboard navigation, screen-reader announcements, cancellation races, empty/error/loading states and every UI-to-API flow.
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

Events must share stable plan, approval, operation and dependency identifiers so an auditor can reconstruct the complete sequence. Store append-only records with restrictive access, secret redaction and minimal personal data. Add a verifiable integrity mechanism (for example, a hash chain with a documented trust anchor); append-only JSONL and filesystem permissions alone do not prove tamper-evidence. Provide an integrity-check/export path. Never report a consequential operation as fully successful when required evidence could not be persisted or verified.

**Current implementation boundary:** the installer now records plan creation, plan-ID approval submission, action start and terminal outcomes in a sequenced SHA-256-linked local JSONL chain. The chain is checked before appending and can be verified through `GET /api/dependencies/audit`; corruption fails closed. This is tamper-evident against partial modification or reordering, not immutable against an attacker who can rewrite the complete file. The current web/CLI interface does not provide a verified human identity or cryptographic proof that the plan was displayed and understood. The chain has no independently stored trust anchor, and writers are serialized with a cross-process file lock. The lack of an independently stored trust anchor remains a deployment blocker for stronger audit assurance; do not describe the ledger as tamper-proof or complete.


## First-run installation redesign (v1.0)

The current `doctor` command is a diagnostic, not a first-run installer. A clean-machine user must not be expected to interpret dependency IDs, create a virtual environment manually, or translate generic remediation advice into package-manager commands.

### Product behaviour

The first-run entry point is `whaxon setup`. It must be usable by a non-expert and must never silently elevate privileges or run a scanner against a target.

1. **Preflight:** identify OS family/version, CPU architecture, Python runtime, active environment, writable locations, available package managers, network reachability (only after consent), and whether WHAXON is installed in an isolated environment.
2. **Capability selection:** offer Core, Standard, Full and Custom profiles. Explain each capability in plain language. Core must launch without optional scanners; missing optional tools degrade only their own capabilities.
3. **Plan:** produce one reviewable installation plan, grouped by runtime, Python packages, external tools, wordlists/resources and optional integrations. Show exact package IDs, sources, commands, expected disk/network impact, privilege requirements and unsupported items. Plan generation is read-only and deterministic.
4. **Approval:** require explicit approval for each privilege boundary. Never accept arbitrary shell commands from the UI, catalog, or user input. Do not use `sudo`, UAC elevation, or administrator access without a separate clear consent step.
5. **Execution:** run only allowlisted platform-specific package-manager operations, without a shell, with bounded timeouts, cancellation, captured/redacted output, and per-operation audit records. Never execute scanner commands or contact assessment targets during installation.
6. **Verification:** check executable resolution, version, expected resources and safe local smoke tests. A package-manager exit code alone is not success.
7. **Recovery:** identify partial changes, offer precise repair guidance, and never claim rollback unless it was actually performed and verified. Persist the installation report.

### Platform policy

- **Linux:** support explicitly tested distributions and package-manager adapters (initially Debian/Ubuntu and Kali where package IDs are confirmed). Detect apt/dpkg; do not assume every Linux distribution is apt-based.
- **macOS:** use Homebrew only when installed and supported; otherwise provide the official project installation route. Never install Homebrew implicitly without consent.
- **Windows:** winget/Chocolatey/Scoop may be detected, but no native Windows package IDs are currently enabled for automatic installation; the current path is manual guidance. WSL2 is a separate Linux environment and must be detected/reported as such; do not pretend native Windows executables and WSL executables are interchangeable.
- Unsupported OS/package-manager combinations remain diagnosable and receive a precise manual route. No guessed package IDs.

### Dependency classes

- **Runtime blockers:** Python and WHAXON's mandatory runtime resources. Resolve these before installation of WHAXON itself where possible.
- **Core Python requirements:** installed by the package installer from the published wheel metadata; doctor verifies them and should explain how to repair a broken environment.
- **External security tools:** catalogued individually with platform package IDs, official source, supported architectures, version probes and safe functional verification. An unknown package mapping is never auto-installed.
- **Optional integrations:** install only when selected. They must not block core use.
- **Resources:** wordlists, templates and other data assets must have explicit source, licence, integrity hash, destination and verification. Never silently download arbitrary lists.

### Non-negotiable acceptance tests

- Fresh supported Linux, Windows and macOS environments with no optional tools installed.
- Core install, Standard install, Full install and Custom install, including cancellation and rerun.
- No-root/no-admin and unsupported-package-manager paths.
- Offline mode and interrupted/failed package-manager operations.
- No command execution during diagnostics or plan preview.
- Exact plan-to-execution binding; changed manifest, host or package selection invalidates approval.
- Audit integrity and secret redaction on success, failure, timeout and cancellation.
- Post-install verification catches missing binaries, wrong versions, broken PATH and missing resources.
- Wheel and sdist contain all manifests, adapters and required resources.
- Browser and CLI setup flows share the same backend policy and operation model.

### Current boundary and implementation sequence

This document defines the full v1.0 target; it is not a claim that every target capability is implemented. The current branch has the canonical dependency/capability manifest, read-only platform detection, deterministic profile planning, an approval-bound sequential Python-package batch engine, CLI setup command, Diagnostics profile planner and explicit profile-batch UI approval. In addition, `whaxon setup` has a separate exact-plan-approved external-tool installation path using a conservative curated package-ID allowlist on supported Linux package managers and Homebrew. This is a limited supported-platform slice, not broad cross-platform coverage. `whaxon doctor --install` remains a narrow Python-package installer and `whaxon install` remains an apt-only legacy command.

Remaining work is not the initial creation of package-manager adapters: it is extending and validating the curated mappings and sources, adding integrity and functional verification coverage, consent-bound network/offline and recovery handling, full clean-machine acceptance across explicitly supported Linux distributions/Windows/WSL2/macOS, independent audit trust anchoring, worker-restart recovery, and packaging/accessibility/end-to-end regression gates. Do not infer platform support from package-manager detection alone. Each capability requires clean-machine evidence before it is advertised as deployment-ready.


### Current `whaxon setup` command implementation

The current branch adds a read-only host detector, deterministic profile planner, approval-bound Python-package batch installation and an explicit virtual-environment bootstrap. Package-manager executables are detected read-only. A separate, exact-plan-approved CLI path now installs a conservative allowlist of external tools from curated package IDs on supported Linux managers and Homebrew; unsupported combinations remain manual. External-tool plan previews only resolve executable paths and do not run version-probe subprocesses. An already-detected executable is not treated as missing or reinstalled; trusted version probes run only after explicit submission of the reviewed plan or through `whaxon doctor --verify`.

```bash
# Create a new .venv without overwriting an existing directory
whaxon setup --create-venv

# Or choose another destination
whaxon setup --create-venv --venv-path .venvs/whaxon

# Activate the environment using the command printed by setup, then:
whaxon doctor
whaxon setup --profile core
whaxon setup --profile standard
whaxon setup --profile full
whaxon setup --profile custom --capability core --capability tui
```

After activating the newly created environment, install WHAXON into that environment with `python -m pip install --upgrade whaxon`, then run `whaxon doctor`. The setup preview prints an approval ID bound to the selected dependency set, manifest and observed environment. The current explicit installation path is:

```bash
whaxon setup --profile core
# Review the plan and its network/transitive-dependency impact.
whaxon setup --profile core --install --approve PLAN_ID
```

The Python-package batch path executes only missing, manifest-allowlisted Python packages. It requires the active virtual environment, uses the bounded pip transaction, verifies installed versions/imports and records audit events. The separate external-tool path is restricted to its curated package IDs and supported package managers. Cancellation or failure stops the batch; already completed package operations are not rolled back. A failed batch must be followed by `whaxon doctor`.

**Still open:** broad package coverage for the full tool catalog; native Windows package-manager mappings; consent-bound network preflight and offline recovery; independent audit trust anchoring; durable worker recovery across process restarts; and full clean-machine acceptance beyond the currently recorded selected Linux/macOS/Windows wheel-and-venv and package-manager smoke checks. Package-manager detection alone does not imply that an operating system is supported. The master roadmap §38 controls release acceptance; no draft-PR status is implied by this document.


### Headless Linux server acceptance

The CLI setup and doctor paths do not require a TTY, X11, Wayland, Qt, or a desktop session. The production WSGI entry point is `whaxon serve` (Waitress); the headless CI gate installs the web extra, removes display/session variables, runs setup preview and doctor, then starts Waitress and performs an HTTP request against loopback. This verifies a no-GUI/no-TTY server process, not a hardened public deployment. Remote deployments must configure explicit non-default authentication credentials and a protected data directory; do not expose the development `whaxon web` server or default credentials.
