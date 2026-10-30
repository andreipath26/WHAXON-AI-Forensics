# WHAXON

**A scope-controlled Python platform for authorized security assessments, with evidence-based finding validation and operator-governed execution.**

WHAXON brings security-tool orchestration, normalized findings, evidence, validation, and reporting into one local-first workflow. It provides a command-line interface, terminal UI, desktop UI, and browser interface. Optional AI-assisted planning can help choose next steps, but it does not replace operator authorization or determine whether a finding is verified.

WHAXON is designed for security practitioners working in systems they own or are explicitly authorized to assess. It is not a hosted scanning service, a guarantee of complete vulnerability coverage, or a substitute for a signed scope and rules of engagement.

[![CI](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml/badge.svg)](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/whaxon.svg)](https://pypi.org/project/whaxon/)
[![Python versions](https://img.shields.io/pypi/pyversions/whaxon.svg)](https://pypi.org/project/whaxon/)
[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)

## Current project status

The current `main` branch contains the core assessment workflow: tool catalog and adapters, scope checks, job execution, finding storage and correlation, conservative validation for supported finding types, retesting commands, coverage tracking, and report generation.

The package metadata in `pyproject.toml` currently declares version `1.0.0` and Python `>=3.11`. The main-branch CI workflow tests Python 3.11, 3.12, and 3.13 and runs the AI-boundary test, Ruff, mypy, the test suite, distribution build/metadata validation, and a clean-wheel smoke test. Check the live [CI results](https://github.com/andreipath26/WHAXON-AI-Forensics/actions) for the current status; a green run validates the tested code paths, not every possible target, tool, operating system, or deployment configuration.

Some capabilities remain partial or environment-dependent. In particular, not every web-interface page is backed by a live service: the interaction audit marks individual controls as passing, wired-but-not-yet-browser-verified, mockups, or hidden. See [Web UI interaction audit](docs/WEB_UI_INTERACTION_AUDIT.md) before treating the browser interface as feature-complete.

The dependency-readiness guided installer and URL-based bug-bounty program ingestion are active development workstreams. Their design and/or implementation review should not be mistaken for functionality already shipped on `main`; check the [open pull requests](https://github.com/andreipath26/WHAXON-AI-Forensics/pulls) for their integration status.

## What WHAXON does

- **Orchestrates security tools.** Runs supported command-line tools through a shared catalog and execution layer. External tools are not bundled with WHAXON and must be installed and configured separately.
- **Normalizes findings.** Adapters translate supported tool output into a common finding model while retaining source information.
- **Correlates observations.** Combines related results to help analysts investigate an asset or engagement without treating every scanner line as an independently confirmed vulnerability.
- **Enforces configured scope.** Uses explicit in-scope and out-of-scope rules, with out-of-scope rules taking precedence. Missing or malformed scope configuration does not silently authorize arbitrary targets.
- **Validates selected findings conservatively.** Deterministic checks cover only defined finding types and request shapes. Unsupported or inconclusive findings remain candidates for analyst review.
- **Preserves evidence and produces reports.** Stores engagement/job data locally and generates Markdown, HTML, PDF, JSON, and WHAXON-format engagement outputs where supported.
- **Supports optional AI planning.** Configurable providers can propose actions and next steps. Execution remains bounded by the platform's scope and approval controls; AI output is not itself proof of a vulnerability.

## Finding validation: what the verdicts mean

WHAXON deliberately avoids treating a failed replay as proof that a finding is false, fixed, or remediated.

The current validator has deterministic paths for selected injection findings (including SQL injection, XSS, and command injection) and read-only observation types such as open ports, missing HTTP security headers, invalid TLS certificates, and insecure cookie attributes. Coverage depends on the finding data, request context, target behavior, and the supported probe for that kind.

- `verified` means the configured check obtained the specific repeatable evidence required by that check. It is not a universal guarantee of exploitability or impact.
- `candidate` means the evidence is incomplete, the replay is unsupported, the request cannot safely be reproduced, or the result is inconclusive.
- A timing difference alone does not promote a finding to verified.
- A replay failure does not mean the vulnerability is absent.
- Findings outside the implemented validation coverage require human investigation.

The validator is deterministic; an LLM does not assign the validation verdict. Read [the experiment audit](docs/WHAXON_EXPERIMENT_AUDIT_2026-10-25.md) for counterexamples from an earlier snapshot, corrections made in current code, and limitations that remain.

## Scope, authorization, and network safety

WHAXON's default scope is restrictive: loopback, private IPv4 ranges, and selected local IPv6 ranges. Targets not explicitly permitted are denied. Explicit out-of-scope rules override in-scope rules, and malformed scope configuration is an error rather than a permissive fallback.

**Application-level scope checks are not a network firewall.** DNS answers can change after preflight checks, and external scanners may follow redirects or make secondary requests. A successful scope check therefore does not guarantee that every network connection made by every third-party tool remains inside the intended target boundary.

For any assessment beyond a disposable local lab:

1. Obtain written authorization and define the exact permitted assets, methods, time window, and request limits.
2. Review and verify the active scope configuration before running tools.
3. Enforce outbound network restrictions independently (for example, with an isolated scanner VM/container, firewall rules, or a scope-aware egress proxy).
4. Review each tool's behavior, options, credentials, and potential impact.
5. Preserve logs and evidence, and stop if the target or authorization boundary is uncertain.

Do not expose the web service to an untrusted network without reviewing authentication, host binding, TLS/reverse-proxy configuration, and deployment controls. Never use default credentials on an exposed instance.

See [Scope documentation](docs/scope.md) and [Security Policy](SECURITY.md).

## Interfaces

| Interface | Entry point | Notes |
| --- | --- | --- |
| CLI | `whaxon --help` | Primary command dispatcher for setup, scope, runs, findings, validation, retesting, reports, and related workflows |
| Terminal UI | `whaxon` or `whaxon tui` | Textual interface; install the `tui` extra |
| Desktop UI | `whaxon gui` | PySide6 interface; install the `gui` extra |
| Web UI | `whaxon web` | Browser interface for local use |
| Web service | `whaxon serve` | Service launch path; review deployment guidance before network exposure |

The browser interface is not yet feature-complete across every page. The interaction audit documents which controls are live, wired, mockups, or hidden. The CLI and documented APIs may expose workflows that are not yet represented by a complete browser experience.

## Tools and adapters

The packaged tool catalog currently includes entries for tools such as Nmap, Nikto, Gobuster, SQLmap, WHOIS, dig, Nuclei, Commix, ffuf, WPScan, Impacket, theHarvester, dnsrecon, NetExec, Arjun, and Hydra, along with selected Metasploit/session operations and test utilities.

Catalog presence does not mean the executable is installed, configured, licensed, or available on every operating system. Adapter support also varies: some tools have dedicated parsers, while other catalog entries may provide execution support without the same level of normalized finding enrichment. Consult [Tools](docs/tools.md) and [Adapters](docs/adapters.md) for details.

## Installation

WHAXON requires Python 3.11 or newer.

### Install the core package and terminal/web extras

```bash
python -m pip install --upgrade pip
python -m pip install "whaxon[tui,web]"
```

For the desktop interface:

```bash
python -m pip install "whaxon[gui]"
```

For development and tests, clone the repository and install the development extras:

```bash
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics
python -m pip install -e ".[tui,web,dev]"
```

External security tools are separate system dependencies. Install only the tools required for your authorized assessment and verify their versions and configuration independently.

## First run

Initialize local data, then inspect the scope before executing a tool:

```bash
whaxon init
whaxon scope --show
whaxon --help
```

Read [Scope](docs/scope.md) before launching an assessment. The default scope is intended for local/private lab use; public targets require explicit authorization and explicit scope configuration.

Useful command entry points include:

```bash
whaxon run --help
whaxon findings --help
whaxon validate --help
whaxon retest --help
whaxon coverage --help
whaxon report --help
whaxon jobs --help
whaxon ai --help
```

## Reports and evidence

WHAXON can produce per-job and engagement-level reports in supported formats, including Markdown, HTML, PDF, JSON, and the WHAXON engagement envelope.

Examples:

```bash
# Inspect report options
whaxon report --help

# Generate a report for a job
whaxon report JOB_ID --format html

# Generate an engagement report
whaxon report --all --format pdf
```

Replace `JOB_ID` with an actual job identifier. Report formats and options depend on whether the output is per-job or engagement-wide. Reports are decision-support artefacts: inspect the underlying evidence, scope, limitations, and tool output before sharing them with a client.

## AI and operator control

AI-assisted planning is optional and provider configuration is required. The AI layer can suggest actions, but suggestions are not authorization. The operator remains responsible for target selection, scope, approvals, and the impact of commands. Do not enable unattended execution unless its exact policy, allowed phases, and boundaries have been reviewed and tested in an isolated environment.

See [AI documentation](docs/ai.md) and [Agent architecture](docs/agent-architecture.md).

## Development and verification

The repository CI workflow currently runs:

1. The AI-boundary test.
2. Ruff linting.
3. mypy type checking.
4. The full pytest suite.
5. Source and wheel distribution build plus Twine metadata validation.
6. A clean-environment wheel smoke test on Python 3.12, including CLI startup, packaged resources, default scope behavior, and a local HTTP observation validation.

Run the principal checks locally:

```bash
ruff check src tests
mypy src
python -m pytest tests/ -q
python -m build
python -m twine check dist/*
```

Install the same optional dependencies used by CI before running the full suite. Browser tests require Playwright Chromium; PDF/report tests may require the system dependencies configured by CI.

See [Contributing](CONTRIBUTING.md) and the [Engineering Execution Model](docs/ENGINEERING_EXECUTION_MODEL.md).

## Documentation

- [Getting started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Agent architecture](docs/agent-architecture.md)
- [Scope and authorization](docs/scope.md)
- [Tools](docs/tools.md)
- [Adapters](docs/adapters.md)
- [Findings](docs/findings.md)
- [Reports and evidence](docs/reports-and-evidence.md)
- [Interfaces](docs/interfaces.md)
- [AI behavior and configuration](docs/ai.md)
- [HTTP API](docs/api.md)
- [Deployment](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Web UI interaction audit](docs/WEB_UI_INTERACTION_AUDIT.md)
- [Experiment audit and limitations](docs/WHAXON_EXPERIMENT_AUDIT_2026-10-25.md)
- [Engineering execution model](docs/ENGINEERING_EXECUTION_MODEL.md)
- [Changelog](docs/CHANGELOG.md)
- [Security policy](SECURITY.md)

## Roadmap and related projects

The roadmap is maintained separately from the implemented feature set. Items described in roadmap or design documents are plans until their code is merged, tested, and reflected in the current branch.

WHAXON is part of a broader set of independent projects:

- [KILN](https://github.com/andreipath26/KILN) — local LLM runtime.
- [Aletheia Framework](https://github.com/andreipath26/aletheia-framework) — local-first AI framework focused on governance and provenance.

They are separate repositories; integration between them should not be assumed unless a specific integration is implemented and documented here.

## Responsible use

Use WHAXON only on systems you own or are explicitly authorized to assess. You are responsible for obtaining permission, defining and respecting scope, complying with applicable law and program rules, and reviewing the impact of each tool and action.

## License

WHAXON is licensed under [AGPL-3.0-or-later](LICENSE). See [licensing documentation](docs/licensing.md). If you need different terms for a commercial deployment, review the repository's commercial licensing information and obtain independent legal advice.
