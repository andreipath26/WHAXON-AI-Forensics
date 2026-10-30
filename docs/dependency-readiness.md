# Dependency readiness and guided installation

## Current implementation status

The first dependency-readiness slice provides **read-only diagnostics**. It does not install, upgrade, remove or configure software.

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

The JSON report uses schema version 1 and includes the runtime, active interpreter, virtual-environment state, required Python package metadata/import-resolvability checks, optional Python extras and external executable discovery from the packaged tool catalog. `--verify` runs only the small set of version probes explicitly curated in `src/whaxon/data/dependencies.json`; it does not run arbitrary tool commands or target scans.

## How to interpret statuses

- `READY`: the declared Python minimum is met and the package import succeeded, or the Python runtime meets the declared minimum.
- `MISSING`: the distribution or executable could not be found.
- `INCOMPATIBLE`: an installed Python distribution is below the declared minimum.
- `BROKEN`: package metadata/import or a required packaged resource could not be read.
- `DETECTED`: an external executable resolves on PATH. This is deliberately **not** equivalent to verified readiness; version and safe smoke-test checks are not yet implemented.

An overall `BLOCKED` result means a required runtime/package/resource is not READY. `DEGRADED` means optional integrations or external tools are unavailable or have not yet been verified. Missing optional tools must not block unrelated core functionality.

## Safety guarantees in this slice

- The command is read-only.
- It does not access the network.
- It does not invoke package managers or external security tools.
- It does not use sudo/admin elevation.
- It does not change PATH or other machine configuration.
- It reports external executables as DETECTED, not READY, until their version and smoke-test contracts exist.

## Manifest

The packaged source of truth is `src/whaxon/data/dependencies.json`. It currently records the Python runtime, core packages, optional extras and installation profiles. The manifest is schema-versioned and rejects duplicate or incomplete dependency records.

## Not implemented yet

The deterministic remediation planner is available with `whaxon doctor --plan`; it produces a plan ID and never executes commands. One manifest-listed Python package can be installed only with `whaxon doctor --install --check ID --approve PLAN_ID`, after a fresh plan has been reviewed. This operation requires an active virtual environment, uses a fixed PyPI index and binary wheels, and records an operation audit.

The CLI also supports `--snapshot` and `--drift`. The local history is bounded to 100 snapshots and stored under `<data-dir>/.whaxon/dependency-readiness.json` with restrictive file permissions where supported. Snapshots omit the current working directory and record only the dependency/environment fields needed for drift detection.

The authenticated web API exposes:
- `GET /api/dependencies` — read-only diagnostics.
- `POST /api/dependencies/verify` — explicit curated version probes.
- `POST /api/dependencies/plan` — read-only plan preview.
- `POST /api/dependencies/install` — exact plan-ID approved package installation.
- `POST /api/dependencies/snapshots` and `GET /api/dependencies/history` — local history.
- `GET /api/dependencies/drift` — compare against the latest snapshot.

External-tool version probes currently cover only entries explicitly configured in the manifest. A version probe is not a full functional smoke test. Other external tools remain DETECTED rather than READY. OS-native installers, offline bundles, complete recovery/rollback, broader external-tool smoke tests and the four approved-UI screens are still outstanding. The UI must not be implemented until the active checked-in UI source is inspected and the exact components/navigation are identified. Do not treat a diagnostic report or version probe as proof that every tool feature works.


## Remediation preview and explicitly approved Python package installs

Generate a read-only plan:

```bash
whaxon doctor --plan
whaxon doctor --plan --check textual
```

The plan includes a deterministic plan ID, affected dependency, proposed argument array, display command, source, network/privilege impact and whether automation is supported. Review the complete plan before proceeding. A plan ID is bound to the current environment, manifest and exact action details; if those change, the old approval is rejected.

For an eligible Python package, the explicit installation invocation is:

```bash
whaxon doctor --install --check textual --approve PLAN_ID
```

Replace `PLAN_ID` with the exact ID from the reviewed plan. The installer is deliberately restricted:

- Requires an activated Python virtual environment; it will not modify a system Python installation.
- Installs only a Python distribution explicitly declared in the packaged dependency manifest.
- Uses the active interpreter's pip, a fixed official PyPI index URL, binary wheels only, no shell, no sudo/admin, no user-supplied command, and a 15-minute timeout.
- Requires a fresh plan ID at execution time; changed manifest/action/environment invalidates the approval.
- Writes a local JSONL audit trail under `~/.whaxon/audit/dependency-install.jsonl` with restrictive file permissions where supported.
- Re-checks the installed distribution version and import after installation. Installer exit code zero is not sufficient.

External security tools are **not** automatically installed in this release slice. Their platform-specific installation sources and verification contracts have not yet been curated. The planner supplies manual guidance rather than inventing package-manager commands.

### Failure recovery

A failed, timed-out or interrupted pip operation may have partially changed the active virtual environment. WHAXON does not claim rollback. Re-run `whaxon doctor`; if the environment is inconsistent, recreate the virtual environment and reinstall the approved dependency set. The audit record includes the operation outcome and recovery guidance.
