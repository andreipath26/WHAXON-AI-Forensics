# WHAXON

Scope-controlled security-tool orchestration, deterministic finding validation, retesting and evidence-backed reporting for authorized assessments.

[![CI](https://img.shields.io/github/actions/workflow/status/andreipath26/WHAXON-AI-Forensics/ci.yml?branch=main)](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue)](LICENSE)

**Current source package: 0.11.16 · Beta · Python 3.11+ · v1.0 acceptance remains open.** The repository can contain changes beyond a published package. Source and tests on an exact commit establish implementation; the [product trajectory](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) defines priorities and release gates.

## What works today

WHAXON brings a tool run, its output, normalized findings and subsequent checks into a shared Python/SQLite workflow. It has substantial implementation, with remaining integration and acceptance work.

| Area | Implemented capability | Boundary |
|---|---|---|
| Tool execution | Shared runner, catalog, adapter registry, output/job persistence and guarded session/pivot paths | External tools need separate installation; catalog presence is not verified support or authorization |
| Findings | Structured adapter output, correlation, severity and request-context storage | Parser and evidence coverage vary by tool |
| Validation | Deterministic checks for supported SQL/error-marker, reflected-XSS, observation and blind/timing cases | Unsupported or ambiguous checks remain unverified; POST/state-changing context replay is refused |
| Retest | Rechecks eligible previously verified findings; records `fixed`, `still_vulnerable` or `inconclusive` with reasons | Failure to reproduce alone is not proof of remediation |
| Evidence/reporting | Persisted findings, history, coverage records and HTML/PDF/Markdown/JSON report paths | Completeness and detailed appendix selection differ by format; reporting acceptance remains open |
| Readiness/setup | Read-only diagnostics and profiles, deterministic reviewed plans, approval-bound installation and verification | Curated OS installation is limited; native Windows external-tool installation remains manual |
| Engine v2 | Versioned immutable plans/manifests, persisted missions/tasks/attempts, scheduler leases/retries/deadlines and bounded concurrency | Initial catalog-provider bridge only; durable mission-wide budgets/cancellation/audit and shared lifecycle remain incomplete |

The packaged catalog has 24 entries, including scanner commands, session operations and a test utility. Import-only integrations, adapter registrations, executables, providers and validated capabilities are separate inventories. See [tools](docs/tools.md), [adapters](docs/adapters.md) and the [baseline register](docs/V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md).

AI providers are optional. AI can propose actions and summarize evidence; deterministic code enforces policy and assigns supported verification outcomes. An AI recommendation never grants authorization or establishes a verified finding.

## Install from this repository

Use a virtual environment. Installing WHAXON does not install every external security tool.

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

`setup --profile core` previews dependencies; it does not install them. Review any proposed plan and its exact approval requirements before installing. Use `whaxon setup --help` for supported profile and installation options. On PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`; see [getting started](docs/getting-started.md) for platform instructions.

Before an assessment, inspect configuration and configure only the assets you own or are explicitly authorized to assess:

```bash
whaxon init --help
whaxon scope --help
whaxon run --help
whaxon report --help
```

Scope configuration is not proof of authorization. Review generated configuration rather than assuming default private-network ranges belong to you. [Scope documentation](docs/scope.md) explains the boundary and checks.

## Interfaces and deployment

```bash
whaxon web
```

Open [http://127.0.0.1:5001/](http://127.0.0.1:5001/). The root redirects to the supplied Obsidian Kinetic UI at `/ui-v2`. Its 22 production templates have page-specific browser coverage, but complete control inventory, visual/accessibility checks, service parity and external-asset acceptance remain open. Unsupported features stay hidden or disabled; a page is not a promise that its entire proposed subsystem ships.

`whaxon serve` provides the Waitress service entry point. Headless Linux startup has CI smoke coverage. Remote access requires explicit authentication and suitable reverse-proxy/TLS configuration; follow [deployment](docs/deployment.md). Foreground, daemon, systemd and Docker modes still need acceptance for each advertised deployment combination.

Optional `tui` and `gui` extras provide terminal and desktop interfaces. **The desktop shell now opens `/ui-v2`; actual Qt-window acceptance remains open.** Legacy reference assets are preserved. The supplied browser UI still depends on external assets; full air-gapped browser operation is not established.

## Current limitations and next work

- **One-shot isolation:** `coverage`, `validate`, `retest` and `recon` initialize without draining unrelated queued jobs. Dedicated regression tests cover successful and refused command paths; explicit worker/follow-up behavior remains supported.
- Scope guards are application-level checks, not a firewall or connection-time DNS pin. External tools can make secondary requests; deployment egress controls remain necessary.
- Evidence-chain, crash/restart, cancellation, budget and audit guarantees need integrated acceptance. Hash chaining without an independent trust anchor is not immutability.
- Package installation can leave partial changes; completed installations are not generally rolled back. Setup smoke is not universal platform or full-tool acceptance.
- Full autonomous bounty campaigns, multi-target orchestration, broad Metasploit integration, vulnerability patch application and enterprise features remain gated future work. `core/remediation.py` currently plans dependency repairs, not vulnerability patches.

The active sequence is correctness and Trust Layer → shared durable services → install/headless and supplied-UI acceptance → controlled-lab end-to-end proof → release. The [trajectory](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) separates implemented work from unmet gates and deferred scope. No global completion percentage or universal zero-false-positive claim is justified.

## Verification evidence

For inspected baseline [`6fa1fa5`](https://github.com/andreipath26/WHAXON-AI-Forensics/commit/6fa1fa5f9bcff9b7afffb87ca908b0f78562fa3b), [CI #41488450899](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41488450899) passed all nine jobs. Python 3.11, 3.12 and 3.13 each reported **1,408 passed, 14 skipped**; static checks, distribution builds and selected packaging/platform/headless/scanner smoke checks passed.

Those results certify that baseline and those checks. They do not certify every later commit, external tool, transport or release gate. Skipped checks remain untested. Consult current CI and [project state](docs/STATE.md) before relying on a release claim.

## Documentation and contribution

- [Documentation index](docs/README.md), [getting started](docs/getting-started.md), [dependency readiness](docs/dependency-readiness.md).
- [Findings](docs/findings.md), [reports and evidence](docs/reports-and-evidence.md), [interfaces](docs/interfaces.md), [API](docs/api.md).
- [Trajectory and release gates](WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md), [baseline evidence](docs/V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md), [cleanup and retirement register](docs/DOCUMENTATION_RECONCILIATION.md).
- [Contributing](CONTRIBUTING.md), [security policy](SECURITY.md), [changelog](docs/CHANGELOG.md).

Use only on systems you own or have explicit authorization to assess. WHAXON does not replace written authorization, rules of engagement or analyst judgment.

Licensed under [AGPL-3.0-or-later](LICENSE). See [commercial licensing](docs/commercial-licensing.md), [third-party notices](THIRD_PARTY_NOTICES.md) and [trademark policy](TRADEMARK.md) for additional terms and attribution.
