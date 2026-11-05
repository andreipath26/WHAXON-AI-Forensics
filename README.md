# WHAXON

**A scope-controlled security assessment workspace: orchestrate tools, validate findings, preserve evidence, and retest fixes.**

[![CI](https://img.shields.io/github/actions/workflow/status/andreipath26/WHAXON-AI-Forensics/ci.yml?branch=main)](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue)](LICENSE)

WHAXON brings the operational parts of an authorized security assessment into one workflow. Instead of treating a scanner result as the final answer, it connects **execution, findings, validation, evidence, reporting and retesting**—with explicit scope and approval checks controlling what may run.

It is designed for practitioners who need to understand **what was tested, what was actually observed, which findings were verified, and what changed after remediation**.

**Project status:** Beta, source version **0.11.16**. Active Engine V2 development is underway; **v1.0 is not yet accepted or released as production-ready**. The [roadmap](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) defines the remaining release gates.

## The assessment workflow

1. **Define scope and authorization.** Specify permitted targets and review the execution boundary before running a tool.
2. **Execute supported tools.** WHAXON uses a shared runner and registered adapters to collect jobs, outputs and structured observations.
3. **Examine and validate findings.** Supported deterministic checks distinguish verified results from candidates and inconclusive observations.
4. **Preserve evidence.** Retain relevant tool output, context, findings, status and coverage information for review.
5. **Report and retest.** Produce assessment reports and recheck eligible findings after remediation, keeping the result and its limitations visible.

The central principle is that **a tool's output is evidence to evaluate—not automatic proof of a vulnerability**. Optional AI assistance can help propose steps or summarize information, but cannot grant permission, override execution policy or independently verify a finding.

## What you can use today

| Capability | What WHAXON provides |
|---|---|
| Tool orchestration | A shared execution path, tool catalog, adapter integration and persisted job history for supported tools |
| Assessment policy | Scope checks and explicit authorization boundaries, including fail-closed decisions in supported paths |
| Finding handling | Normalized observations, correlation, request context and verification states |
| Validation and retesting | Deterministic checks for supported cases, plus tracked retests with fixed, still-vulnerable or inconclusive outcomes |
| Evidence and reporting | Persisted findings and coverage, with HTML, PDF, Markdown and JSON reporting paths |
| User interfaces | Command-line operation, a browser workspace at `/ui-v2`, and optional terminal/desktop interfaces |
| Engine V2 foundation | Versioned workflow and capability contracts, persistent missions and execution intents, bounded scheduling, approvals, events and provider routing |

These are **implemented capabilities, not claims of universal scanner support or completed end-to-end certification**. Some integrations require external binaries; parser coverage, supported validation contexts and output fidelity depend on the tool and workflow. The [tool documentation](docs/APPLICATION_ARCHITECTURE_MASTER.md) and [adapter documentation](docs/APPLICATION_ARCHITECTURE_MASTER.md) explain the integration boundaries.

### How Engine V2 fits

Engine V2 is the ongoing work to make the execution system **one durable, capability-driven engine** rather than a collection of independent tool-specific flows.

Its foundations include versioned plans and task contracts, deterministic provider selection, durable queue ownership, leases, bounded concurrency, policy-bound approvals, cancellation barriers and reconciliation states. Newer implementation slices also provide semantic operation aliases, provider inventories and reviewable evidence-derived follow-up plans.

The hard remaining work is proving these mechanisms together under real service restarts, external-tool failures, transport changes and multi-client workflows. **An accepted queued request must not vanish, and an uncertain external effect must not be blindly replayed.** See the [Engine V2 architecture](docs/ENGINE_V2_MASTER.md) for the detailed contracts and outstanding gates.

## Get started

**Requirements:** Python 3.11 or newer. Use a virtual environment. WHAXON's Python package does not automatically install every external security tool.

```bash
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[web]"

whaxon --help
whaxon setup --profile core
whaxon doctor --json
```

The setup command above **previews** the core dependency plan; it does not silently install all proposed tools. Review the plan and required approvals before making changes. Windows PowerShell users can activate the environment with `.venv\Scripts\Activate.ps1`. See [Getting started](docs/OPERATIONS_MASTER.md) and [dependency readiness](docs/OPERATIONS_MASTER.md) for platform-specific instructions.

### Launch the browser workspace

```bash
whaxon web
```

Open **http://127.0.0.1:5001/**, which routes to the supplied WHAXON workspace at `/ui-v2`.

The browser interface is under active integration. A visible page does not mean that every proposed workflow or interaction is already supported. WHAXON retains the supplied design; functionality is connected to real service contracts as it becomes available.

### Prepare an authorized assessment

```bash
whaxon init --help
whaxon scope --help
whaxon run --help
whaxon report --help
```

Inspect your configuration, set the targets covered by written authorization, and review what a command will do. **Default scope rules are not proof that a network belongs to you.** Start with [scope and policy](docs/APPLICATION_ARCHITECTURE_MASTER.md).

For service operation and remote-access considerations, read the [deployment guide](docs/OPERATIONS_MASTER.md). Do not expose an assessment service to an untrusted network without suitable authentication and transport protection.

## Current maturity and boundaries

WHAXON is an **actively developed beta**, not a finished autonomous penetration-testing platform.

- **Verification is deliberately limited.** Supported checks produce specific outcomes; unsupported, ambiguous or unreproducible findings must not be presented as independently verified. Stateful POST replay and arbitrary authenticated request replay are not generally supported.
- **Scope controls do not replace network isolation.** External tools may perform additional network operations; application-level checks are not a firewall or a connection-time DNS pin.
- **Evidence integrity is not the same as an external trust anchor.** Local digests and consistency checks can detect some changes, but do not themselves prove independent, tamper-proof custody.
- **Durability is being hardened.** Queue persistence, lease fencing, budget and cancellation controls exist, while full external-effect crash recovery, daemon/container operation and backup/restore acceptance remain open.
- **Interface and installation acceptance is incomplete.** The supplied UI, supported external tools, cross-platform installation, accessibility and end-to-end deployment still need exact-environment verification.
- **Larger expansions remain gated.** Broad autonomous bounty campaigns, multi-target orchestration, advanced session/Metasploit breadth and enterprise integrations are not part of the accepted solo-v1.0 baseline.

For the latest tested commit and outstanding release criteria, use [GitHub Actions](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml), the [project state](WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md) and the [v1.0 acceptance register](docs/V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md). CI passing does not mean every external tool or security claim is validated.

## Documentation

| Start here | Details |
|---|---|
| [Getting started](docs/OPERATIONS_MASTER.md) | Installation and first use |
| [Scope](docs/APPLICATION_ARCHITECTURE_MASTER.md) | Assessment boundaries and authorization |
| [Tools](docs/APPLICATION_ARCHITECTURE_MASTER.md) and [adapters](docs/APPLICATION_ARCHITECTURE_MASTER.md) | Tool integration and supported paths |
| [Findings](docs/EVIDENCE_AND_REPORTING_MASTER.md) and [reports](docs/EVIDENCE_AND_REPORTING_MASTER.md) | Interpretation, evidence and exports |
| [Interfaces](docs/APPLICATION_ARCHITECTURE_MASTER.md) and [API](docs/APPLICATION_ARCHITECTURE_MASTER.md) | CLI, browser and service surfaces |
| [Engine V2 architecture](docs/ENGINE_V2_MASTER.md) | Execution contracts and engineering work |
| [Product roadmap](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) | Priorities, milestones and release gates |

## Contributing, security and licensing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes and [SECURITY.md](SECURITY.md) to report a security issue. This project is for **systems you own or are explicitly authorized to assess**; neither a tool configuration nor an AI suggestion replaces permission and rules of engagement.

WHAXON is licensed under [AGPL-3.0-or-later](LICENSE). See [commercial licensing](docs/CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md), [third-party notices](THIRD_PARTY_NOTICES.md) and the [trademark policy](TRADEMARK.md).
