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
