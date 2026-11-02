# WHAXON

**An evidence-first, scope-controlled platform for authorized security assessments.**

WHAXON brings security-tool execution, finding normalization, evidence collection, conservative validation, retesting and reporting into one operator-governed workflow. It is built for security practitioners who need more than a collection of scanner outputs: they need to understand what ran, what was observed, what could actually be reproduced, and where the evidence is incomplete.

The platform combines a Python CLI and shared assessment core with terminal, desktop and browser interfaces. Optional AI-assisted planning can suggest next actions; deterministic policy and execution controls remain responsible for authorization and execution. AI output is not evidence and does not decide whether a finding is verified.

WHAXON is intended for systems you own or are explicitly authorized to assess. It is not a hosted scanning service, a guarantee of complete vulnerability coverage, or a replacement for written authorization and rules of engagement.

[![CI](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml/badge.svg)](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/whaxon.svg)](https://pypi.org/project/whaxon/)
[![Python versions](https://img.shields.io/pypi/pyversions/whaxon.svg)](https://pypi.org/project/whaxon/)
[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)

---

## Why WHAXON

Security assessments often produce disconnected tool output, duplicate observations, uncertain findings and reports that are difficult to reproduce. WHAXON is designed to connect those steps while keeping the operator in control.

- **One execution workflow:** run supported external security tools through a shared catalog, runner and job lifecycle.
- **Structured findings:** normalize supported tool output into a common finding model while retaining source details and provenance.
- **Evidence-led validation:** use deterministic checks for selected finding types; preserve inconclusive and unsupported cases for analyst review.
- **Retesting:** revisit previously verified findings and distinguish fixed, still-vulnerable and inconclusive outcomes.
- **Scope controls:** apply explicit in-scope and out-of-scope rules, with restrictive defaults and fail-closed handling of invalid scope configuration.
- **Engagement reporting:** bring findings, evidence, verification state and coverage gaps into readable reports.
- **Operator-governed assistance:** optional AI planning can propose actions, but it cannot grant authorization or replace deterministic controls.

The aim is not to claim that every scanner result is a vulnerability. It is to make the assessment workflow more traceable, reviewable and reproducible.

## How it works

A typical workflow is:

1. **Prepare the environment.** Check Python dependencies and the availability of the external tools required for the assessment.
2. **Define authorization and scope.** Configure the permitted assets and exclusions before running tools.
3. **Execute selected tools.** Run supported tools through the shared runner and inspect job output.
4. **Review normalized findings.** Examine source observations, correlated results and preserved evidence.
5. **Validate where supported.** Run deterministic checks against selected finding types. Unsupported or inconclusive findings remain review candidates.
6. **Retest and report.** Revisit verified findings and generate job-level or engagement-level reports.

WHAXON stores its local job and finding data in SQLite by default. External security tools are separate dependencies: catalog entries do not mean a tool is installed, configured, licensed or supported on every operating system.

## Core capabilities

| Area | What is implemented |
| --- | --- |
| Tool execution | Shared catalog and execution layer for supported external command-line tools |
| Finding model | Normalized findings with source information and structured metadata |
| Correlation | Related observations can be grouped to support investigation |
| Scope | Explicit inclusion/exclusion rules, restrictive defaults and fail-closed configuration handling |
| Validation | Deterministic replay/observation checks for selected finding types and request shapes |
| Retesting | Retest workflow for previously verified findings, including inconclusive outcomes |
| Coverage | Records selected reasons why work was skipped or could not run |
| Evidence and reports | Local evidence storage and supported Markdown, HTML, PDF, JSON and WHAXON engagement outputs |
| Dependency readiness | Diagnostics, readiness checks and explicitly approved, allowlisted installation workflows |
| Bug-bounty intake | Review-only import of supported public YesWeHack programme information or supplied text; imports do not authorize testing |
| AI assistance | Optional planning suggestions with operator approval and deterministic execution boundaries |

This is a capability summary, not a promise that every external tool, finding type, interface control or deployment environment has identical support. See [Tools](docs/tools.md), [Adapters](docs/adapters.md), [Findings](docs/findings.md) and [Dependency readiness](docs/dependency-readiness.md).

## Finding validation: conservative by design

WHAXON distinguishes evidence obtained by a configured check from evidence that is incomplete or unsupported.

- **verified** — the implemented check obtained the repeatable evidence required for that specific check.
- **candidate** — evidence is incomplete, replay is unsupported or unsafe, or the result is inconclusive.
- **Retest outcomes** distinguish a finding that remains reproducible from one that appears fixed or cannot be conclusively retested.

A `verified` result is not a universal guarantee of exploitability, business impact or coverage. A failed replay does not prove that a vulnerability is absent. Findings outside implemented validation coverage require human investigation. The validator's verdict is deterministic; an LLM does not assign it.

Read the [experiment audit](docs/WHAXON_EXPERIMENT_AUDIT_2026-10-25.md) for research counterexamples, corrections and limitations. It is important context for understanding why WHAXON uses conservative verdicts.

## Interfaces

The same core is exposed through several entry points:

| Interface | Start |
| --- | --- |
| CLI | `whaxon --help` |
| Terminal UI | `whaxon tui` |
| Desktop UI | `whaxon gui` |
| Browser UI | `whaxon web` |
| Headless service | `whaxon serve` |

The default browser entry point redirects to the Obsidian Kinetic interface at `/ui-v2`. The previous `/ui` interface is retained as a compatibility/reference route. The new interface has 22 page routes and corresponding templates, with browser tests covering its major page workflows.

**UI status:** the new interface is implemented and has page-specific browser coverage, but it should not be described as fully accepted or universally production-ready yet. The current audit records remaining acceptance work, including visual-regression baselines, complete visible-control inventory, accessibility review, CLI/web service parity evidence and deployment treatment of externally loaded assets. Unsupported or simulated controls are intentionally hidden or disabled rather than presented as working features.

See the [new UI interaction and acceptance audit](docs/NEW_UI_INTERACTION_AUDIT.md) for the route map, tested workflows, disabled/reference-only controls and outstanding release gates.

## Installation

WHAXON requires **Python 3.11 or newer**. Use a virtual environment.

### Install from PyPI

For the core package with terminal and browser interfaces:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "whaxon[tui,web]"
```

For the desktop interface, install the `gui` extra:

```bash
python -m pip install "whaxon[gui]"
```

You can combine extras, for example:

```bash
python -m pip install "whaxon[tui,web,gui]"
```

External security tools such as Nmap, Nikto, Gobuster, Nuclei and SQLmap are installed separately. Check the [tool catalogue](docs/tools.md) for the available entries and platform notes.

### Install from source

```bash
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[tui,web,dev]"
```

Windows users should create and activate the environment with the appropriate `py -3.11` and PowerShell activation commands.

## First run

Initialize local data, inspect the active scope and review the available commands:

```bash
whaxon init
whaxon scope --show
whaxon --help
```

Before running an assessment, read [Scope and authorization](docs/scope.md). WHAXON's default scope is restrictive and intended for local/private lab use. Public or third-party targets require explicit authorization and explicit scope configuration.

Useful commands:

```bash
whaxon doctor
whaxon run --help
whaxon findings --help
whaxon validate --help
whaxon retest --help
whaxon coverage --help
whaxon report --help
```

If a particular command is not available in your installed version, consult `whaxon --help` for the actual command surface.

## Scope and network safety

WHAXON's application-level scope checks are an important guardrail, **not a network firewall**. DNS answers can change after preflight checks, and third-party scanners may follow redirects or make secondary requests. A successful scope check does not guarantee that every connection made by every external tool remains within the intended boundary.

For any assessment beyond a disposable local lab:

1. Obtain written authorization and define permitted assets, techniques, time windows and request limits.
2. Review the active scope configuration before execution.
3. Enforce outbound network restrictions independently, for example with an isolated scanner VM/container, firewall rules or a scope-aware egress proxy.
4. Review each tool's behavior, options, credentials and potential impact.
5. Preserve logs and evidence, and stop if the authorization boundary is uncertain.

Do not expose the web service to an untrusted network without reviewing authentication, host binding, TLS/reverse-proxy configuration and deployment controls. See [Security Policy](SECURITY.md) and [Deployment](docs/deployment.md).

## Dependency readiness

The `whaxon doctor` workflow checks the Python runtime, required and optional packages, packaged resources and selected external-tool availability. It can also prepare environment-bound remediation plans. Automated installation is deliberately restricted: eligible Python packages require explicit approval of the exact plan, and supported OS-tool installation uses a separate curated mapping and consent flow.

Diagnostics are read-only unless you explicitly request a supported installation action. The installer is not a general-purpose package manager, and it does not provide a hash-pinned, offline-reproducible deployment or automatic rollback.

See [Dependency readiness and guided installation](docs/dependency-readiness.md) for profiles, plan approval, verification, snapshots and limitations.

## Headless and server use

The web service can run without a desktop session and be accessed through a browser:

```bash
whaxon serve --daemon
```

The default bind is loopback. For a remote deployment, configure non-default credentials, use a trusted reverse proxy for HTTPS, restrict network access and review the deployment requirements before exposing the service.

See [Deployment](docs/deployment.md) for daemon operation, environment variables, systemd, Docker and reverse-proxy guidance.

## AI assistance and operator control

AI assistance is optional and requires provider configuration. It can suggest plans or next steps, but a suggestion is not authorization and model output is not proof. The operator remains responsible for target selection, scope, approvals and the impact of commands.

Do not enable unattended execution unless the exact policy, allowed phases, budgets and stop conditions have been reviewed and tested in an isolated environment.

See [AI behavior and configuration](docs/ai.md) and [Agent architecture](docs/agent-architecture.md).

## Development and verification

The repository includes tests and CI checks for the supported code paths, including linting, type checking, the test suite, package builds and clean-wheel smoke checks. CI success is useful evidence, but it does not prove safety or correctness for every target, external tool, operating system or deployment configuration.

Run the main checks locally:

```bash
ruff check src tests
mypy src
python -m pytest tests/ -q
python -m build
python -m twine check dist/*
```

Install the development dependencies and required browser-test tooling before running the full suite. See [Contributing](CONTRIBUTING.md) and the [Engineering Execution Model](docs/ENGINEERING_EXECUTION_MODEL.md).

## Documentation

- [Architecture](docs/architecture.md)
- [Scope and authorization](docs/scope.md)
- [Tools](docs/tools.md)
- [Adapters](docs/adapters.md)
- [Findings](docs/findings.md)
- [Reports and evidence](docs/reports-and-evidence.md)
- [Interfaces](docs/interfaces.md)
- [AI behavior and configuration](docs/ai.md)
- [HTTP API](docs/api.md)
- [Dependency readiness](docs/dependency-readiness.md)
- [Deployment](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)
- [New UI interaction and acceptance audit](docs/NEW_UI_INTERACTION_AUDIT.md)
- [Experiment audit and limitations](docs/WHAXON_EXPERIMENT_AUDIT_2026-10-25.md)
- [Engineering execution model](docs/ENGINEERING_EXECUTION_MODEL.md)
- [Changelog](docs/CHANGELOG.md)
- [Security policy](SECURITY.md)
- [Licensing](docs/licensing.md)
- [Commercial licensing](docs/commercial-licensing.md)

## Project direction

WHAXON's next architectural direction is documented in the [Engine v2 architecture and roadmap crosswalk](docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md). That document describes a target architecture and implementation contract; it is **not** a claim that Engine v2 is already implemented or ready for deployment. The current behavior remains defined by the code and tests on `main`.

WHAXON is developed in its own repository. Related projects such as [KILN](https://github.com/andreipath26/KILN) and [Aletheia Framework](https://github.com/andreipath26/aletheia-framework) are separate projects; do not assume they are integrated into WHAXON.

## Responsible use

Use WHAXON only on systems you own or are explicitly authorized to assess. You are responsible for obtaining permission, defining and respecting scope, complying with applicable law and programme rules, and reviewing the impact of each tool and action.

## License

WHAXON is licensed under [AGPL-3.0-or-later](LICENSE). Separate commercial licensing information is available in [the commercial licensing guide](docs/commercial-licensing.md). Review the applicable terms and obtain independent legal advice for your intended use.
