# WHAXON

**Evidence-led security assessment orchestration.**

WHAXON brings authorized security testing into a traceable workflow: execute security tools, normalize and correlate their observations, validate selected findings with deterministic checks, preserve supporting evidence, retest verified issues, and produce assessment reports.

It is designed for independent security practitioners, penetration-testing teams, and internal security groups that need more than a collection of scanner outputs. The objective is to make assessment activity easier to review: what was authorized, what ran, what was observed, what could be reproduced, and what remains uncertain.

[![CI](https://img.shields.io/github/actions/workflow/status/andreipath26/WHAXON-AI-Forensics/ci.yml?branch=main&label=CI)](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/whaxon?label=PyPI)](https://pypi.org/project/whaxon/)
[![Python](https://img.shields.io/pypi/pyversions/whaxon?label=Python)](https://pypi.org/project/whaxon/)
[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue)](LICENSE)
[![Maturity](https://img.shields.io/badge/maturity-Beta-blue)](#product-maturity)

[Product workflow](#product-workflow) · [Capabilities](#capabilities) · [Architecture](#architecture) · [Quick start](#quick-start) · [Maturity](#product-maturity) · [Documentation](#documentation)

---

## The problem WHAXON addresses

Security assessments commonly involve multiple independent tools, inconsistent output formats, duplicated observations, uncertain findings, and reports that are difficult to reproduce. A scanner's result is not automatically a verified vulnerability, and a successful command is not proof that the assessment was complete.

WHAXON is being developed around a simple distinction:

**An observation, a finding, a verification result, and a remediation outcome are different things.**

The platform connects those stages while keeping authorization and consequential decisions under operator control.

## Product workflow

1. **Define the assessment boundary.** Configure explicit in-scope and excluded assets before execution.
2. **Check the environment.** Inspect Python dependencies and external-tool readiness; review installation plans before approving any system changes.
3. **Execute selected tools.** Run supported tools through a shared runner and job lifecycle.
4. **Normalize and investigate.** Convert supported tool output into structured findings while retaining source details and evidence.
5. **Verify where supported.** Apply deterministic, finding-specific checks. Unsupported or inconclusive findings remain candidates for analyst review.
6. **Retest and report.** Revisit eligible verified findings and produce job-level or engagement-level reports with documented limitations.

## Capabilities

| Capability | Current implementation |
|---|---|
| Tool execution | Shared catalog, runner, job lifecycle and adapters for supported external tools. External tools are installed and licensed separately. |
| Finding normalization | Common finding records with source, structured data, raw output and request context where available. |
| Correlation | Groups related observations to support investigation while retaining source records. |
| Scope enforcement | Explicit inclusion and exclusion rules, restrictive defaults, and fail-closed handling of invalid scope configuration. |
| Deterministic verification | Selected SQL error, reflected-XSS and command-injection checks, plus read-only observations for supported network and web findings. |
| Retesting | Retest workflow for previously verified findings, with `fixed`, `still_vulnerable` and `inconclusive` outcomes. |
| Evidence and reporting | Local evidence persistence and job/engagement reporting in supported Markdown, HTML, PDF and JSON formats. |
| Dependency readiness | Read-only diagnostics, capability-profile planning and approval-gated installation for a limited allowlist. |
| Bug-bounty intake | Review-only import of supported public YesWeHack programme information or supplied text. Import does not authorize testing. |
| AI-assisted planning | Optional proposals and recommendations. AI does not grant authorization, approve its own actions, or assign verification verdicts. |

A catalog entry is not a guarantee that a tool is installed, licensed, compatible with the host, fully adapted, or validated end to end. Consult the tool and adapter documentation before relying on an integration.

## Evidence and verification model

WHAXON deliberately avoids treating every scanner result as a confirmed vulnerability.

| State | Interpretation |
|---|---|
| `verified` | The implemented check obtained the repeatable evidence required for that specific check. |
| `candidate` | Evidence is incomplete, the check is unsupported or unsafe, or the result is inconclusive. Analyst review is required. |
| `refuted` | A replay ran but the expected evidence did not appear. This does not prove that the vulnerability is absent. |

Verification is deterministic; an LLM does not set the verdict. Timing differences alone remain inconclusive. Retesting is limited to eligible verified findings and records whether the issue appears fixed, remains vulnerable, or cannot be determined.

A verified result is bounded by the check that produced it. It is not a guarantee of exploitability, business impact, or complete coverage.

## Architecture

The current platform combines a shared Python core with CLI, terminal, desktop and browser interfaces. The core coordinates scope checks, tool execution, adapters, persistence, validation and reporting. Local assessment data is stored in SQLite by default.

```mermaid
flowchart LR
    OP[Operator] --> IF[CLI / TUI / Desktop / Web]
    IF --> CORE[Shared Python core]
    CORE --> POLICY[Scope and execution controls]
    POLICY --> RUN[Runner and job lifecycle]
    RUN --> EXT[External security tools]
    EXT --> ADP[Adapters and parsers]
    ADP --> FIND[Normalized findings]
    FIND --> STORE[(SQLite and evidence)]
    STORE --> VERIFY[Deterministic verification]
    VERIFY --> RETEST[Retest]
    STORE --> REPORT[Assessment reports]
    AI[Optional AI planning] -. proposals only .-> IF
```

### Engine v2

Engine v2 is the migration toward capability-driven, durable mission and task-graph execution. The current branch contains versioned task/plan contracts, persistence, scheduler and recovery primitives, and an initial read-only scanner-provider integration slice.

This is an incremental implementation, not a completed general-purpose autonomous mission engine. Security acceptance, production recovery guarantees, broader provider migration, shared CLI/API/headless lifecycle, and integration with the supplied UI remain in progress. The architecture crosswalk and master roadmap describe the target and the outstanding gates.

## Interfaces

| Interface | Entry point | Notes |
|---|---|---|
| Command line | `whaxon --help` | Primary operator interface and command reference. |
| Terminal UI | `whaxon tui` | Optional `tui` extra. |
| Desktop UI | `whaxon gui` | Optional `gui` extra. |
| Browser UI | `whaxon web` | Flask development-server entry point; redirects to the new `/ui-v2` interface. |
| Web service | `whaxon serve` | Waitress-based WSGI entry point; daemon mode is available on supported POSIX hosts. |

The supplied Obsidian Kinetic browser interface currently has 22 page routes/templates and page-specific browser tests. Its implementation is not yet fully accepted: visual-regression baselines, a complete visible-control inventory, accessibility review, CLI/web parity evidence and external-asset deployment checks remain open. Controls without a supported backend are hidden or disabled; their visual presence is not a delivered capability. The former `/ui` interface is retained as a compatibility/reference surface.

## Quick start

**Requirements:** Python 3.11 or newer. A virtual environment is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "whaxon[web]"
```

Prepare and inspect the local environment:

```bash
whaxon setup --profile core   # read-only plan; installs nothing
whaxon doctor                 # inspect Python packages and external tools
whaxon init                   # initialize local data
whaxon scope --show           # review the active scope
whaxon --help                 # commands in the installed version
```

The setup preview does not install software. Installation requires a separate review and explicit approval of the exact eligible plan. See [Dependency readiness](docs/dependency-readiness.md).

### Install from source

```bash
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[web,dev]"
```

### Deployment

Use `whaxon serve` for the production-oriented Waitress entry point. The `whaxon web` command starts the Flask development server and should remain local.

The default web credentials are demonstration defaults, not suitable for a network-facing deployment. Configure a unique username and strong password (or supported password hash), bind appropriately, and use a trusted HTTPS reverse proxy. Read [Deployment](docs/deployment.md) before exposing the service.

## Scope and operational boundaries

WHAXON is for systems the operator owns or is explicitly authorized to assess.

Scope checks are application-level controls, not a network firewall or a guarantee that every connection made by an external scanner remains in scope. DNS answers can change after preflight checks; third-party tools may follow redirects or make secondary requests. Enforce outbound restrictions independently through an isolated environment, firewall or scope-aware egress proxy.

Other important boundaries:

- External scanners are separate dependencies; WHAXON does not bundle every tool in its catalog.
- Verification covers selected finding types and request shapes, not every possible vulnerability class.
- Unsupported, skipped and inconclusive work must not be represented as tested or verified.
- AI output is a proposal, not authorization, execution evidence or a verification verdict.
- Dependency installation is allowlisted and approval-gated, but completed package changes are not generally rolled back.

See [Scope and authorization](docs/scope.md) and [SECURITY.md](SECURITY.md).

## Product maturity

WHAXON is currently a **Beta** software project.

- **Published package:** `0.11.16` on PyPI. The current `main` branch contains development beyond that published package; do not assume every main-branch capability is present in the wheel.
- **v1.0:** not released. The master roadmap's v1.0 acceptance checklist (§38) remains open.
- **Engine v2:** foundations and an initial provider integration are present; security, recovery, provider coverage and shared-client acceptance remain incomplete.
- **Browser UI:** implemented across 22 routes, but the formal acceptance gaps listed above remain open.
- **CI:** use the live workflow badge and the Actions history for the exact commit being evaluated. A passing run on an earlier commit is not evidence that the current branch is green.

WHAXON should not be represented as a fully accepted v1.0 release or a production-ready autonomous assessment platform at this stage. The roadmap distinguishes implemented code, tested behavior and release acceptance.

## Documentation

| Subject | Reference |
|---|---|
| Getting started | [Getting started](docs/getting-started.md) |
| Architecture | [Architecture](docs/architecture.md) |
| Scope and authorization | [Scope](docs/scope.md) |
| Tool catalog and adapters | [Tools](docs/tools.md) · [Adapters](docs/adapters.md) |
| Findings and verification | [Findings](docs/findings.md) |
| Reports and evidence | [Reports and evidence](docs/reports-and-evidence.md) |
| Dependency readiness | [Dependency readiness](docs/dependency-readiness.md) |
| Interfaces and API | [Interfaces](docs/interfaces.md) · [HTTP API](docs/api.md) |
| Deployment | [Deployment](docs/deployment.md) |
| AI planning | [AI behavior](docs/ai.md) · [Agent architecture](docs/agent-architecture.md) |
| Engine v2 | [Architecture and roadmap crosswalk](docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md) |
| UI acceptance | [UI interaction and acceptance audit](docs/NEW_UI_INTERACTION_AUDIT.md) |
| Project roadmap | [Master roadmap](<WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md>) |
| Security and contribution | [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md) |

## Licensing

The community code is licensed under [AGPL-3.0-or-later](LICENSE). A separate commercial licence may be discussed for use cases that cannot comply with the AGPL, but no additional rights exist without a separate written agreement. There is currently no separately published enterprise edition or standard enterprise agreement. See [commercial licensing](docs/commercial-licensing.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

---

**WHAXON — evidence first. Operator in control.**
