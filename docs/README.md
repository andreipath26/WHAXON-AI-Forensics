# WHAXON Documentation Index

This index separates **current operator guidance**, **current engineering/acceptance records**, **roadmap designs**, and **historical evidence**. It applies only to `andreipath26/WHAXON-AI-Forensics`. The current implementation baseline is `main`; source and tests establish behavior, while the master roadmap establishes scope and release gates.

Start with the [repository-wide documentation reconciliation](DOCUMENTATION_RECONCILIATION.md) before using older material. The repository contains imported snapshots, point-in-time designs, experiment records and generated reports; their presence does not make them current product specifications.

## Start here

- [README](../README.md) — public product overview, install entry point and capability boundaries.
- [Getting started](getting-started.md) — current checkout and first run.
- [Project state](STATE.md) — dated release/CI/acceptance snapshot.
- [Master roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) — authoritative scope, sequencing and release gates.
- [Changelog](CHANGELOG.md) — chronological engineering history; older entries are not current status.
- [Documentation reconciliation](DOCUMENTATION_RECONCILIATION.md) — file inventory, status classes and source-of-truth rules.

## Current operator and developer guides

- [Dependency readiness and guided installation](dependency-readiness.md)
- [Troubleshooting](troubleshooting.md)
- [Scope and authorization](scope.md)
- [Tool catalog and execution](tools.md)
- [Adapters](adapters.md)
- [Findings](findings.md)
- [Reports and evidence](reports-and-evidence.md)
- [Interfaces](interfaces.md)
- [HTTP API](api.md) — selected routes; server source is authoritative.
- [Deployment](deployment.md)
- [AI behavior and configuration](ai.md)
- [Data retention](DATA_RETENTION.md)
- [Architecture](architecture.md)
- [Plugin development](plugins.md)
- [Contributing](../CONTRIBUTING.md)
- [Security policy](../SECURITY.md)

## Current implementation and acceptance records

These are dated engineering records. They describe the implementation or acceptance state at the stated revision; re-check the current source, tests and CI before relying on them for a financing or release claim.

- [Project state](STATE.md)
- [New UI interaction and acceptance audit](NEW_UI_INTERACTION_AUDIT.md)
- [Dependency readiness implementation and acceptance record](first-run-installation-redesign.md) — implementation detail; operator instructions are in `dependency-readiness.md`.
- [Engine v2 architecture and roadmap crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md) — target architecture plus dated implementation updates; not proof of v2 production acceptance.
- [Tool intelligence and controlled onboarding](TOOL_INTELLIGENCE_AND_ONBOARDING.md) — proposed subsystem/acceptance design, not a shipped capability.
- [Engineering execution model](ENGINEERING_EXECUTION_MODEL.md) — project engineering process, not product functionality.
- [WHAXON experiment audit](WHAXON_EXPERIMENT_AUDIT_2026-10-25.md) — dated research evidence and limitations, not current CI or release evidence.

## Roadmap and proposed designs — not shipped merely because documented

- [Master roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md)
- [Competitor capability and remediation addendum](../WHAXON%20Competitor%20Capability%20and%20Remediation%20Roadmap%20Addendum.md)
- [Bug-bounty add-on design](bounty-addon.md)
- [Metasploit / Armitage Engine integration design](METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md)
- [Engine v2 crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md)

A roadmap item, architecture proposal, acceptance criterion or UI route is not an implemented or verified capability unless current source and tests demonstrate it.

## Historical and superseded engineering records

Retained for provenance and to avoid losing design rationale. Do not use their old status tables, estimates, module inventories or present-tense statements as current facts:

- [Agent architecture](agent-architecture.md) — early agent design snapshot.
- [Autonomous loop](autonomous-loop.md) — early autonomy design snapshot.
- [Session execution](session-execution.md) — pre-implementation session transport design.
- [Report redesign](report-redesign.md) and [report visual design](report-visual-design.md) — historical design/PR plans; current behavior is in [Reports and evidence](reports-and-evidence.md) and source/tests.
- [Business impact](business-impact.md) — historical implementation/design notes; current behavior is in source/tests.
- [Engine v2 baseline inventory](ENGINE_V2_BASELINE_INVENTORY.md) — point-in-time E0 baseline, superseded by later crosswalk updates and current source.
- [Legacy web UI interaction audit](WEB_UI_INTERACTION_AUDIT.md) — superseded by the new UI audit.
- [Screenshots and demo capture guide](screenshots.md) — capture instructions, not evidence that listed screenshots exist.
- [Demo script](demo.md) — a proposed walkthrough, not a recorded product demonstration.

## Research, experiment and generated evidence

- `whaxon-experiment-2026-10-25/` — preserved experiment notebook, raw evidence, logs and dated results. Its target observations and CI claims are historical; do not generalize them to current product behavior.
- [Experiment audit](WHAXON_EXPERIMENT_AUDIT_2026-10-25.md) — current-main follow-up to that historical experiment; limitations remain explicit.
- `data/proof-dvwa/` — generated sample job and engagement reports from a dated DVWA run. These are sample artifacts, not a current benchmark, supported-tool guarantee or release test.
- `src/whaxon/data/payloads/` — vendored payload/reference material. Payload presence does not imply that a validator supports or safely executes every technique. See [payload attribution](../src/whaxon/data/payloads/ATTRIBUTION.md).

## UI source and imported web captures

- `web ui files and rendering/obsidian_kinetic/DESIGN.md` — supplied Obsidian Kinetic design reference.
- `web ui files and rendering/extracted_text_*.md` and related GitHub page captures — raw imported snapshots, including material from the original `WHAXON` repository. They are archival research artifacts, **not** current source, documentation or authority for this repository.
- `web ui files and rendering/whaxon_road_map_whats_next_full_scope.md` — older copied roadmap snapshot; superseded by the root master roadmap.
- `web ui files and rendering/whaxon_v1.0.0_deployment_release_notes.md` — unissued draft, not an actual v1.0.0 release note. See its replacement disclaimer.

## Licensing and notices

- [Editions](editions.md)
- [Licensing overview](licensing.md)
- [Commercial licensing](commercial-licensing.md)
- [Community license](../LICENSE)
- [Commercial license notice](../LICENSE-COMMERCIAL.md)
- [Enterprise licensing status](../LICENSE-ENTERPRISE.md)
- [Third-party notices](../THIRD_PARTY_NOTICES.md)
- [Trademark policy](../TRADEMARK.md)
- [Contributor License Agreement](../CLA.md)

## Related projects

KILN and Aletheia Framework are separate repositories and products, not WHAXON modules or dependencies:

- [KILN](https://github.com/andreipath26/KILN)
- [Aletheia Framework](https://github.com/andreipath26/aletheia-framework)
