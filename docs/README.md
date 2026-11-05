# WHAXON documentation

> **Documentation consolidation (2026-11-05):** [Engine V2 Master](ENGINE_V2_MASTER.md) is the canonical **technical** Engine V2 reference, incorporating the architecture, baseline, phase acceptance and evidence records. Older `ENGINE_V2_*.md` files are historical/source evidence, not parallel active masters. The [root roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) continues to govern product priorities and acceptance. Do not create additional competing Engine V2 planning or status files.

Source and tests on an exact commit establish implemented behavior. The [product trajectory](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) is the single active priority and release-gate file. A design, screenshot, old DONE label or passing historical CI run is not current product acceptance.

## Start here

- [Project README](../README.md): overview and installation entry point.
- [Product trajectory and release gates](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md): P0–P8, current work order, §38 acceptance and previous-scope reconciliation.
- [Engine V2 Master](ENGINE_V2_MASTER.md): consolidated architecture, implementation and phase acceptance; use this before the historical E-series source documents.
- [Project state](STATE.md): concise dated snapshot.
- [Baseline and acceptance register](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md): current source, test and CI evidence, critical workflow map and remaining acceptance.
- [Repository due diligence and dispositions](DOCUMENTATION_RECONCILIATION.md): exact removal candidates, dependency-bound cleanup, retirement gates and retained material. This is a disposition register, not another roadmap.
- [Changelog](CHANGELOG.md): engineering/release history, not the active task queue.

## Maintained operator and developer guides

| Topic | Guide |
|---|---|
| First run | [Getting started](getting-started.md), [dependency readiness](dependency-readiness.md), [troubleshooting](troubleshooting.md) |
| Execution | [Scope](scope.md), [tools](tools.md), [adapters](adapters.md), [plugins](plugins.md), [AI](ai.md) |
| Results | [Findings](findings.md), [reports and evidence](reports-and-evidence.md), [data retention](DATA_RETENTION.md) |
| Interfaces | [Interfaces](interfaces.md), [selected HTTP API](api.md), [deployment](deployment.md) |
| Development | [Architecture](architecture.md), [contributing](../CONTRIBUTING.md), [security policy](../SECURITY.md) |

Guides can describe supported subsets. Check current source and the capability register before assuming every tool, transport, platform or API workflow is implemented and accepted.

- [UI source-control inventory](UI_CONTROL_INVENTORY.md): all 22 templates, source binding evidence and unresolved runtime/visual/accessibility checks.

## Detailed architecture and acceptance records

These documents serve distinct purposes and remain subordinate to the trajectory's work order:

- [New UI interaction/acceptance audit](NEW_UI_INTERACTION_AUDIT.md): page-route/test mapping and remaining supplied-design acceptance.
- [Engine v2 architecture/crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md): detailed target contracts, migration and dated implementation records.
- [First-run implementation/acceptance record](first-run-installation-redesign.md): setup design and remaining deployment checks; current use belongs in the dependency-readiness guide.
- [Engineering execution model](ENGINEERING_EXECUTION_MODEL.md): dependency-driven work ownership, integration and verification.

## Approved deferred designs

Presence here is not a claim that a subsystem ships:

- [Tool intelligence and controlled onboarding](TOOL_INTELLIGENCE_AND_ONBOARDING.md).
- [Metasploit / Armitage integration](METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md).
- [Bug-bounty add-on](bounty-addon.md).
- [Competitor capability and remediation addendum](../WHAXON%20Competitor%20Capability%20and%20Remediation%20Roadmap%20Addendum.md).

The trajectory places these at their dependency gates. Inspect source before implementing; preserve reusable existing contracts and do not create parallel schedulers, registries or execution authorities.

## Historical records and references

These files retain rationale or earlier evidence. They are not current implementation instructions:

- [Agent architecture](agent-architecture.md), [autonomous loop](autonomous-loop.md), [session execution](session-execution.md).
- [Report redesign](report-redesign.md), [report visual design](report-visual-design.md), [business impact](business-impact.md).
- [Engine v2 E0 baseline](ENGINE_V2_BASELINE_INVENTORY.md), [legacy UI audit](WEB_UI_INTERACTION_AUDIT.md).
- [Screenshot capture guide](screenshots.md), [demo script](demo.md): instructions/proposals, not completed demonstrations.
- [Partnership/investor research](CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md): dated research, with external facts requiring revalidation before use.
- `data/proof-dvwa/`: dated generated sample reports; not current regression or release evidence.

The previously referenced `whaxon-experiment-2026-10-25/` folder and `docs/WHAXON_EXPERIMENT_AUDIT_2026-10-25.md` are absent from the inspected `6fa1fa5` working tree. Do not follow their former local links or describe them as currently checked-in artifacts. Their historical branch/reference disposition is recorded in the due-diligence register.

The complete previous roadmap remains available through the trajectory's pinned Git-history link. There is no second active roadmap or copied archive added to this tree.

## Supplied UI assets and imported captures

[Supplied UI source](../web%20ui%20files%20and%20rendering/README.md) and its [design reference](../web%20ui%20files%20and%20rendering/obsidian_kinetic/DESIGN.md) govern visual fidelity. Production templates live in `src/whaxon/interfaces/web/templates/ui_v2_*.html`. Named source variants are not interchangeable until mapped.

Verified loose duplicates, imported page captures, the copied roadmap, unissued release-note disclaimer and static source/history exports have been removed. Named design originals remain unchanged. See the [disposition register](DOCUMENTATION_RECONCILIATION.md) for executed cleanup and remaining migration gates.

Vendored [payload attribution](../src/whaxon/data/payloads/ATTRIBUTION.md) is a runtime/provenance resource. Payload presence does not establish validator support for every listed technique.

## Licensing and notices

- [Editions](editions.md), [licensing overview](licensing.md), [commercial licensing](commercial-licensing.md).
- [Community license](../LICENSE), [commercial notice](../LICENSE-COMMERCIAL.md), [enterprise status](../LICENSE-ENTERPRISE.md).
- [Third-party notices](../THIRD_PARTY_NOTICES.md), [third-party license inventory](../THIRD_PARTY_LICENSES/README.md).
- [Trademark policy](../TRADEMARK.md), [contributor agreement](../CLA.md).

KILN, Aletheia Framework, SYBIL and other portfolio projects are separate repositories/products, not WHAXON runtime dependencies or release workstreams.
