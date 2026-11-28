<div align="center">

# WHAXON

### Evidence-led security assessment and vulnerability management

**Discover responsibly. Validate independently. Keep the evidence. Verify remediation.**

[![CI](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml/badge.svg)](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml)
[![License: AGPL-3.0-or-later](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB)](pyproject.toml)
[![Project: Beta](https://img.shields.io/badge/status-active%20beta-orange)](#project-status)

[Get started](#quick-start) · [Features](#capabilities) · [Engine V2](#engine-v2) · [Documentation](#documentation) · [Contribute](#contributing-and-security)

</div>

---

## Security findings need more than a scanner alert

A scan can indicate a potential weakness. It does not necessarily prove that a vulnerability is exploitable, establish what was actually tested, or demonstrate that remediation worked.

**WHAXON** is an open-source, operator-led platform for **authorized security assessments**. It brings external tool execution, normalized findings, scope checks, supported validation, evidence, reporting, and retesting into a connected workflow.

WHAXON is designed for security practitioners, maintainers, and researchers who want to distinguish **observations**, **supported verification results**, and **unresolved uncertainty**—without treating AI output or a tool's exit code as proof.

> [!IMPORTANT]
> **Project status: active beta, version 0.11.16.** Engine V2 includes substantial implemented and tested components but is **not fully migrated or approved for production deployment**. Some browser UI features and security-tool integrations are still being completed. The published code is not a certified pentesting service or a turnkey autonomous agent. See [Project status](#project-status).

## At a glance

| Area | What WHAXON provides | Boundary to understand |
| --- | --- | --- |
| **Assessment tools** | Tool catalog, adapters, runner, persisted job records, and supported import paths | Tools generally require separate installation; catalog presence does not imply readiness |
| **Scope and authorization** | Target scope controls and approval-bound execution on supported paths | Application checks do not replace real engagement authorization or network isolation |
| **Findings** | Normalized observations, correlation, severity data, evidence references, and lifecycle tracking | A detected candidate is not automatically verified |
| **Validation and retesting** | Supported deterministic checks and remediation outcomes | Unsupported cases remain uncertain or inconclusive |
| **Reports** | Assessment outputs including Markdown, HTML, PDF, and JSON paths | Report completeness depends on captured evidence and actual assessment coverage |
| **Interfaces** | CLI, a developing browser workspace, optional TUI and desktop UI | Not every visible V2 browser control is fully wired |
| **Engine V2** | Durable missions, plans, worker queues, provider routing, budgets, approvals, audit, and recovery controls | Full client-path migration, provider recovery, UI parity, and release qualification remain open |
| **AI advisory** | Review-only plan suggestions and a durable mission-linked advisory ledger | An MCP relay is **not** model inference; no live keyless ChatGPT/DeepSeek inference is claimed |

## How WHAXON approaches an assessment

```text
     Define engagement and authorized target scope
                         │
                         ▼
             Select supported capabilities
                         │
                         ▼
         Execute approved assessment steps
                         │
                         ▼
            Capture findings and raw evidence
                         │
                         ▼
         Independently validate where supported
                         │
                         ▼
             Report results and coverage gaps
                         │
                         ▼
                Remediate and retest
```

The goal is **traceable security decisions**, not the largest possible number of alerts. WHAXON distinguishes what a tool observed from what a supported check confirmed, and keeps unsupported claims visible rather than silently upgrading them to facts.

## Quick start

### Requirements

- **Python 3.11 or newer**; Linux is the primary supported target. Other environments are covered by selected CI checks, but installation and tool availability vary.
- Git and a Python virtual environment.
- Any external security utilities you intend to use, installed and configured **separately**.
- Authorization to assess the target system or a controlled lab.

### Install for evaluation

```bash
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[web]"

whaxon --help
whaxon doctor --json
whaxon setup --profile core
```

The setup profile is a **reviewable dependency preview**, not permission to install or execute external security tools. Refer to the [operations guide](docs/OPERATIONS_MASTER.md) for supported platforms, installation plans, service deployment, and troubleshooting.

### Open the local workspace

```bash
whaxon web
```

Open **[http://127.0.0.1:5001/](http://127.0.0.1:5001/)** in your browser. The server redirects to the developing `/ui-v2` workspace. Do **not** expose a development instance on a public interface without reviewing authentication, TLS, configuration, and deployment guidance.

### Explore the Engine V2 workflow service

```bash
# Display available registered capabilities and provider readiness.
whaxon workflow capabilities
whaxon workflow providers

# Create a mission. This does not run a scanner.
whaxon workflow mission create \
  --id lab-assessment \
  --objective "Authorized assessment of a controlled lab"

# Inspect all workflow subcommands, including plan creation and review.
whaxon workflow --help
```

**Execution is deliberately separate from planning.** The V2 service requires persisted plans, appropriate approvals, and an eligible worker. Creating a mission, viewing a provider, or accepting an AI suggestion does not start an assessment.

For deployment and workflow details, see the [Engine V2 architecture](docs/ENGINE_V2_MASTER.md) and [operations guide](docs/OPERATIONS_MASTER.md).

## Capabilities

### Tool-assisted discovery and assessment

WHAXON combines a capability catalog, adapters, and a shared execution/evidence pipeline. Supported integrations can use external tools to collect observations; each adapter has its own prerequisites and support limitations. **WHAXON does not bundle or guarantee every tool listed in its catalog.**

### Findings, independent validation, and retesting

Stored findings can be correlated, examined with context, and carried through reporting and supported retest flows. A validator should be able to explain the evidence for a decision; a successful process exit, an alert label, or model confidence alone is insufficient.

### Reports and evidence

WHAXON provides multiple report formats and preserved workflow information to help reconstruct what was attempted, what completed, and where coverage is incomplete. Evidence integrity, independent custody verification, and production qualification remain separate acceptance work.

### Operator interfaces

The headless CLI and shared service make the underlying workflows inspectable without a browser. The developing **V2 web workspace** presents assessment, finding, workflow, and reporting experiences. TUI and desktop entry points also exist; they are **not** assurances of complete feature parity.

## Engine V2

Engine V2 is the ongoing transition from separate direct-execution paths to **one durable workflow authority** used across clients and workers.

**Implemented engineering foundations include:**

- **Mission and plan lifecycle:** versioned workflow plans, dependency graphs, task progress, and durable queued run requests.
- **Controlled execution:** capability/provider manifests, pinned execution context, authorization and scope checks, bounded concurrency, time/rate/attempt/cost controls, and cancellation behavior.
- **Recovery and accountability:** persistent attempts, worker leases, audit events, conservative reconciliation of uncertain provider effects, and safeguards against unverified success claims.
- **Reviewable AI boundary:** constrained proposals and mission-linked advisory messages that **cannot authorize or directly execute** a security operation.

**Not yet complete:** remaining legacy execution-path migration, cross-client parity, broader provider-specific recovery, full UI action wiring and accessibility acceptance, and end-to-end external deployment qualification. CI and laboratory smoke-test success are valuable engineering evidence, **not a production-release approval**.

See the [Engine V2 master reference](docs/ENGINE_V2_MASTER.md), [master product roadmap](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md), and [release decision register](docs/ENGINE_V2_G10_RELEASE_DECISION.md).

### AI and MCP: communication is not inference

WHAXON is exploring a **model-API-key-free communication path** inspired by the [Zalmoxis MCP bridge](https://github.com/andreipath26/zalmoxis/tree/main/bridge):

- **MCP + OAuth** can let a compatible, authenticated AI agent exchange scoped messages with a service without using a **model API key** for the transport.
- **Inference** still requires an actual model: a supported, signed-in provider application capable of receiving a request and returning a result, or a locally hosted runtime.
- A queued message does not automatically wake a consumer chatbot, grant paid model access, or prove that inference ran.
- External AI recommendations remain **untrusted advisory input**. They cannot grant scope, approve a workflow, verify a finding, or dispatch security tools.

The durable advisory ledger is implemented in Engine V2. **Hosted MCP connections, account-provider round trips, local-model routing, and privacy/security qualification remain integration work**, not shipped production services. See the [MCP integration workstream](docs/ENGINE_V2_MASTER.md#engine-v2--account-authenticated-mcp-advisory-bridge-and-local-inference-2026-11-23).

## Project status

| Milestone | Status |
| --- | --- |
| Core package, CLI and supported assessment primitives | **Available in beta** |
| Findings, reporting, and supported validation/retest paths | **Available with stated limits** |
| Shared Engine V2 workflow service | **Substantial implementation; bounded engineering tests** |
| Durable AI advisory message ledger | **Implemented; transport integration pending** |
| Complete V2 cross-interface functionality and UI | **In progress** |
| Live keyless MCP-to-model inference | **Not verified or deployed** |
| Production rollout / v1.0 sign-off | **HOLD — not ready to deploy** |

This table is a **capability-level summary**, not a certification or substitute for the detailed acceptance record. For the implementation and qualification criteria, consult the [release decision](docs/ENGINE_V2_G10_RELEASE_DECISION.md). Release claims must be backed by the exact candidate and its evidence.

## Documentation

| Resource | Purpose |
| --- | --- |
| [Operations guide](docs/OPERATIONS_MASTER.md) | Installation, dependencies, local services, hardening, and deployment |
| [Engine V2 master](docs/ENGINE_V2_MASTER.md) | Architecture, lifecycle, safeguards, integration and remaining gates |
| [Product roadmap](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) | Product direction and implementation priorities |
| [Release acceptance decision](docs/ENGINE_V2_G10_RELEASE_DECISION.md) | Explicit deployment HOLD and remaining qualification work |
| [Changelog](docs/CHANGELOG.md) | Development history |
| [Contributing](CONTRIBUTING.md) | How to propose and submit changes |
| [Security policy](SECURITY.md) | How to disclose a vulnerability privately |
| [Third-party notices](THIRD_PARTY_NOTICES.md) | External component licensing |

## Contributing and security

Contributions from security engineers, maintainers, researchers, technical writers, and testers are welcome, especially for **correctness, evidence integrity, responsible assessment workflows, integration reliability, accessibility, and reproducible tests**.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request; the repository uses a contributor license agreement (CLA). Use [GitHub Issues](https://github.com/andreipath26/WHAXON-AI-Forensics/issues) for bugs or proposals **that do not contain sensitive vulnerability details**.

**Security disclosures:** do not report an exploitable WHAXON vulnerability in a public issue. Follow [SECURITY.md](SECURITY.md) for the private reporting process.

## License and responsible use

WHAXON's source code is licensed under **[AGPL-3.0-or-later](LICENSE)**. Separate commercial licensing may be available; third-party components retain their own licenses and terms. See [third-party notices](THIRD_PARTY_NOTICES.md).

Use WHAXON only against systems you own or have **explicit authorization** to assess. Maintain appropriate network and organizational safeguards. Scope controls, AI-generated suggestions, and validation tools do not replace professional judgment or independently obtained authorization.

---

<div align="center">

**WHAXON — from security observations to defensible evidence.**

[Explore the roadmap](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) · [Report a bug](https://github.com/andreipath26/WHAXON-AI-Forensics/issues) · [Read the security policy](SECURITY.md)

</div>
