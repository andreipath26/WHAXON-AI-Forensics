# Dependency readiness and guided installation

## Current implementation status

The first dependency-readiness slice provides **read-only diagnostics**. It does not install, upgrade, remove or configure software.

Run:

```bash
whaxon doctor
whaxon doctor --json
whaxon doctor --core-only
whaxon doctor --check python
```

The JSON report uses schema version 1 and includes the runtime, active interpreter, virtual-environment state, required Python package metadata/import checks, optional Python extras and external executable discovery from the packaged tool catalog.

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

Remediation planning, OS-specific installation options, explicit per-operation approval, installer execution, transaction recovery, executable version probes, safe smoke tests, persisted readiness history, web API endpoints and the four approved-UI screens are still queued. Do not treat a diagnostic report as an installation plan or as proof that an external tool works.


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
