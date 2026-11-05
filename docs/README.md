# WHAXON documentation — canonical index

> **Current verified evidence (2026-11-05):** [main CI at `fc056d0`](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42033360849) passed all 13 jobs, including Python 3.11–3.13, SearchSploit, systemd, Docker and platform setup. Subsequent commits must pass **their own** exact-head checks. E5 bounded engineering work is merged, while complete client migration, D1–D6, independent real-target/evidence acceptance and V1 G01–G10 release gates remain OPEN.

**Consolidated 2026-11-05.** One authoritative master per subject. Superseded documentation has been absorbed into the linked masters and removed from the live tree. Git history preserves its original revisions. Do not create competing architecture, roadmap, audit, acceptance, or status documents. For current feature claims, consult code and exact-HEAD CI rather than historical narratives embedded within masters.

| Area | Single authoritative document | Scope |
|---|---|---|
| Product work order and release gates | [Product roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) | P0–P8, product priorities, competitor gap analysis, dated product-state capture |
| Engine V2 | [Engine V2 master](ENGINE_V2_MASTER.md) | Architecture, migration, provider contracts, E0–E9, evidence and acceptance |
| V1 release | [V1 acceptance master](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) | Solo release criteria, bounded acceptance and reconciliations |
| UI V2 | [UI V2 master](V2_UI_MANDATORY_CROSSWALK.md) | 22-page crosswalk, interaction, accessibility/design inventories and audits |
| Bug bounty module | [Bounty technical design](bounty-addon.md) | Programme policy, scope enforcement, differential analysis and proposed bounty workflows |
| Business impact | [Impact technical design](business-impact.md) | Severity calculation, finding enrichment, cost-range methodology and report presentation |
| Application architecture | [Application architecture master](APPLICATION_ARCHITECTURE_MASTER.md) | AI, agents, scope, tools, providers, adapters, autonomous/session execution, API |
| Installation and operations | [Operations master](OPERATIONS_MASTER.md) | First-run, dependency setup, deployment, diagnostics, demo and screenshots |
| Findings, evidence and reports | [Evidence/reporting master](EVIDENCE_AND_REPORTING_MASTER.md) | Findings, evidence, reporting design, retention requirements |
| Business, partnerships and licensing guidance | [CBC playbook](CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md) | CBC, funding/investor strategy, commercial editions and licensing overview |
| Engineering process, retention and repository cleanup | [Project governance master](PROJECT_GOVERNANCE_MASTER.md) | Engineering rules, prior cleanup decisions and AI use audit |
| Document routing | [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) | Single-master policy and current inventory |
| Engineering history | [Changelog](CHANGELOG.md) | Chronological changes (historical, not a second roadmap) |

## Separate binding or functional files

- [Repository README](../README.md), [contributor guide](../CONTRIBUTING.md), [security policy](../SECURITY.md), [agent instructions](../AGENTS.md).
- [AGPL community license](../LICENSE), [commercial](../LICENSE-COMMERCIAL.md) and [enterprise](../LICENSE-ENTERPRISE.md) instruments, [CLA](../CLA.md), [trademark](../TRADEMARK.md), [third-party notices](../THIRD_PARTY_NOTICES.md) and [license inventory](../THIRD_PARTY_LICENSES/README.md).
- [Documentation assets inventory](assets/README.md), [supplied UI design sources](../web%20ui%20files%20and%20rendering/README.md) and [payload attribution](../src/whaxon/data/payloads/ATTRIBUTION.md).
- Structured acceptance CSVs, checked-in tests, actual deployment configurations, screenshots and generated evidence remain as data/evidence rather than new narrative masters.

## Integrity rules

1. The root product roadmap decides priorities and release gates. The subject masters provide detailed explanation but cannot overrule it.
2. Draft UI V2 and Engine V2 acceptance does not mean production-ready; do not relax deployment gates because documents were consolidated.
3. Update the subject master in place. Add standalone files only for legally independent documents, functional source assets, or reproducible machine-readable evidence.
4. The old standalone narrative documents have been removed. Locate past revisions in Git history when needed, not through dead links.
