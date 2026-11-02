# Getting Started

This guide describes the current `main` checkout of **andreipath26/WHAXON-AI-Forensics**. The PyPI package is version 0.11.16; the repository may contain unreleased changes. Use `whaxon --help` to confirm the commands available in your installed copy.

## Requirements

- Python 3.11 or newer (Python 3.13 is included in CI).
- Linux, macOS or Windows; external tool installation support varies by OS.
- External security tools are separate dependencies. See [Tools](tools.md) and [Dependency readiness](dependency-readiness.md).

## Install from source

```bash
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[tui,web]"
```

For PowerShell, create the environment with `py -3.11 -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1`. Install the `gui` extra separately if you need the PySide6 desktop interface:

```bash
python -m pip install -e ".[gui]"
```

## Install the published package

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "whaxon[tui,web]"
```

The latest published version recorded on PyPI is **0.11.16 (October 23, 2026)**. The repository's `main` branch includes work beyond that published artifact; do not assume every current-main feature is present in the PyPI wheel.

## First run

```bash
whaxon init
whaxon doctor
whaxon scope --show
whaxon --help
```

Review the generated data directory and the active scope before running anything. The default scope is restrictive and covers loopback and private address ranges; it is not authorization to assess every host in those ranges.

## Run an authorized lab assessment

1. Create or select a lab target that you own or are explicitly authorized to test.
2. Add only the approved target(s) to the scope configuration. See [Scope and authorization](scope.md) for the configuration format and CLI.
3. Confirm the target with `whaxon scope --check <target>`.
4. Inspect the tool's supported arguments with `whaxon run --help` and the catalog documentation.
5. Run the selected tool and review the resulting job, findings and evidence.

Do not use `scanme.nmap.org` or another public test host as a default first-run target: it is outside the generated default scope and requires explicit scope configuration and compliance with the host owner's current testing terms. Never widen scope merely to make a tutorial command work.

## Browser interface

Start the local development server in the foreground:

```bash
whaxon web
```

Open [http://127.0.0.1:5001/](http://127.0.0.1:5001/). The root route redirects to the current Obsidian Kinetic interface at `/ui-v2`; `/ui` is retained as the legacy interface.

Loopback requests use the local-peer authentication shortcut, subject to Host and cross-origin protections. Remote requests require explicit non-default authentication credentials. Never expose the default local configuration to an untrusted network. See [Deployment](deployment.md).

## Useful data locations

Paths are relative to the configured `WHAXON_DATA` directory (default: `data/`):

- `whaxon.db` — SQLite job, finding, evidence and workflow state.
- Tool catalog and packaged resources — see [Tools](tools.md) and [Dependency readiness](dependency-readiness.md).
- Scope and other runtime configuration — see [Scope](scope.md) and [Deployment](deployment.md).

Report output locations depend on the selected command and options; consult `whaxon report --help`.

## Next

- [Scope and authorization](scope.md)
- [Tool catalog](tools.md)
- [Interfaces](interfaces.md)
- [Dependency readiness](dependency-readiness.md)
- [Deployment](deployment.md)
- [Troubleshooting](troubleshooting.md)
