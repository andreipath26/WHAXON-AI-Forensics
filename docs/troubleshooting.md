# Troubleshooting

This guide applies to the current `main` checkout. Package wheels may lag behind main; use `whaxon --help` and each command's `--help` to confirm the installed version's command surface.

## Installation and Python environment

### `ModuleNotFoundError: No module named 'whaxon'`

Activate the virtual environment used for installation and install the project into that interpreter:

```bash
source .venv/bin/activate
python -m pip install -e ".[tui,web]"
python -c "import whaxon; print(whaxon.__file__)"
```

On PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[tui,web]"
```

### `externally-managed-environment`

Do not use system pip. Create and activate a virtual environment, then use `python -m pip` from that environment.

### Optional interface dependency is missing

Install only the extra you need:

```bash
python -m pip install -e ".[tui]"   # terminal interface
python -m pip install -e ".[web]"   # browser interface
python -m pip install -e ".[gui]"   # desktop interface
```

PySide6 wheel availability depends on the Python version and platform. WHAXON requires Python 3.11+; if a GUI dependency has no compatible wheel for your interpreter, use a supported Python release or install the TUI/web extras instead. Do not change Python versions without recreating the virtual environment.

## Dependency diagnostics and installation

### A dependency is MISSING, INCOMPATIBLE or BROKEN

Run:

```bash
whaxon doctor
whaxon doctor --json
```

Check which interpreter is active, whether the dependency is required or optional, and whether a packaged resource is missing. A BLOCKED result concerns a required runtime/package/resource; DEGRADED can mean an optional integration or external tool is unavailable.

### An external tool is DETECTED but not READY

Run `whaxon doctor --verify` to perform only the curated, bounded version probes. Review multiple PATH candidates and the resolved executable path. A catalog entry does not mean the executable is installed, licensed or compatible.

### A remediation plan cannot be approved

Generate a fresh plan with `whaxon doctor --plan` and approve only its exact current plan ID. Approval is bound to the environment and manifest; a changed plan must be reviewed again. Python-package automation requires an active virtual environment and manifest allowlisting. OS-tool installation has a separate limited apt/Homebrew allowlist; unsupported platforms remain manual.

### An installation failed or was interrupted

Rerun `whaxon doctor` and inspect the operation/audit record. A failed pip operation may have partially changed the virtual environment; WHAXON does not promise rollback. If the environment is inconsistent, recreate the virtual environment and reinstall the required approved extras. See [Dependency readiness](dependency-readiness.md).

## Tool execution and scope

### `binary not found` or a tool is unavailable

Run `whaxon doctor` and `whaxon doctor --verify`, then check the tool's entry in [the packaged catalog](tools.md). Install external tools separately using the documented supported method for your OS. The catalog's package hint is not an installation command or permission.

### A target is rejected

Inspect the active configuration with `whaxon scope --show` and check the exact target with `whaxon scope --check <target>`. The default scope is restrictive (loopback and private ranges); it is not authorization to test every address in those ranges. Do not disable scope to work around an unexpected denial. Review [Scope and authorization](scope.md).

### A tool appears to run but no findings are produced

Not every catalog tool has a finding parser, and parser coverage differs by tool and output version. First inspect the persisted job output and exit status:

```bash
whaxon jobs --help
whaxon findings --help
whaxon report --help
```

Check [Tools](tools.md) and [Adapters](adapters.md) for the current catalog and registered parser inventory. An empty finding list is not proof that the target is free of vulnerabilities. Preserve raw output and report unsupported or unparsed output as a coverage limitation.

### A scan hangs or cancellation does not complete

Use the cancellation control in the active interface or the supported job-cancel API. The runner uses process-group handling for subprocess termination on POSIX; behavior can vary by platform and by external tool. Check the job state and operating-system process list before starting a duplicate scan.

### A follow-up tool did not run

The CLI `whaxon run` drains Automator follow-up jobs queued by that invocation's initial findings. It deliberately leaves jobs that were already pending before the invocation untouched. Inspect `whaxon jobs` and the persisted job history if a follow-up is missing or failed.

## Web interface and authentication

### The browser interface is unavailable

Start the foreground server with `whaxon web` and use the address printed at startup (default `http://127.0.0.1:5001`). The root route redirects to `/ui-v2`; `/ui` is the legacy/reference interface.

### Authentication fails

Loopback requests use the local-peer shortcut after Host and cross-origin checks. Remote requests require explicit non-default Basic-auth credentials. Review `WHAXON_AUTH_USER`, `WHAXON_AUTH_PASS` or `WHAXON_AUTH_PASS_HASH`, restart the service after changing environment variables, and clear cached browser Basic-auth credentials if necessary. Never expose the loopback demo defaults remotely. See [Deployment](deployment.md).

### A remote deployment rejects startup

Set a non-default username and strong unique password or a supported bcrypt password hash. Install the web extra and review trusted-proxy and allowed-host configuration before exposing the service. Keep the application bound to loopback behind a reverse proxy where practical.

## Docker and persistence

### Container exits during startup

Run the container in the foreground and inspect its logs. Confirm the mounted data directory is writable by the container process and that `WHAXON_DATA` points to that mount. The hardened image uses a read-only root filesystem; provide the documented writable tmpfs and persistent data volume.

### Jobs or history appear to disappear

Confirm all workers use the same `WHAXON_DATA` path and SQLite database. Check file ownership, permissions, and the database/WAL files before restarting or deleting anything. Do not remove the database as a first troubleshooting step.

## Database inspection and reset

Inspect the local database read-only where possible:

```bash
sqlite3 data/whaxon.db
sqlite> .tables
sqlite> SELECT id, tool, target, status FROM jobs ORDER BY started_at DESC LIMIT 10;
sqlite> .quit
```

Deleting `whaxon.db`, its WAL/SHM files or the configured data directory destroys local history and evidence references. Back up the complete data directory first and only reset it when loss of that data is intended.

## Getting help

Open an issue in the active repository: https://github.com/andreipath26/WHAXON-AI-Forensics/issues. Include the operating system, Python version, WHAXON package/source revision, exact command, relevant diagnostic output and job ID. Redact credentials, tokens, private target data and other sensitive evidence before sharing.
