# WHAXON documentation — canonical index

> **Current delivery status — 2026-11-21:** `main` is at `f32ce0913d460f046f6d984ec54a1f7f5d775409`. PR #226's tested head `65cae35059934a6032cb250bca3752152c88d918` passed exact-head CI [44833852913](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833852913) (20/20), README freeze [44833852900](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833852900), and dashboard acceptance [44833853031](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833853031) before merge; the squash merge has the same tree, with no separate main-commit check run recorded yet. V2 remains **HOLD — NOT READY TO DEPLOY**: implementation/integration is incomplete, including provider-specific effect recovery, remaining shared lifecycle parity, and UI workflows/controls.

| Area | Single authoritative document | Scope |
|---|---|---|
| Product work order and release gates | [Product roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) | P0–P8, product priorities, deferred P7-02 competitor benchmarking, embedded Part II remediation roadmap, dated product-state capture |
| Engine V2 | [Engine V2 master](ENGINE_V2_MASTER.md) | Current synthesis and links to dated architecture, baseline, E1/E3/E5/E6 acceptance, privacy, recovery, readiness and UI handoff records |
| V1 release | [V1 acceptance master](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) | Solo release criteria, bounded acceptance and reconciliations |
| UI V2 | [UI V2 master](V2_UI_MANDATORY_CROSSWALK.md) | 22-page crosswalk, interaction, accessibility/design inventories and audits |
| Bug bounty module | [Bounty technical design](bounty-addon.md) | Programme policy, scope enforcement, differential analysis and proposed bounty workflows |
| Business impact | [Impact technical design](business-impact.md) | Severity calculation, finding enrichment, cost-range methodology and report presentation |
| Application architecture | [Application architecture master](APPLICATION_ARCHITECTURE_MASTER.md) | AI, agents, scope, tools, providers, adapters, autonomous execution and API; links to full session, Metasploit/Armitage and tool-intelligence design records |
| Installation and operations | [Operations master](OPERATIONS_MASTER.md) | First-run, dependency setup, deployment, diagnostics, demo and screenshots |
| Findings, evidence and reports | [Evidence/reporting master](EVIDENCE_AND_REPORTING_MASTER.md) | Findings, evidence, reporting design, retention requirements |
| Business, partnerships and licensing guidance | [CBC playbook](CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md) | CBC, funding/investor strategy, commercial editions and licensing overview |
| Engineering process, retention and repository cleanup | [Project governance master](PROJECT_GOVERNANCE_MASTER.md) | Engineering rules, prior cleanup decisions and AI use audit |
| Document routing | [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) | Single-master policy and current inventory |
| Engineering history | [Changelog](CHANGELOG.md) | Chronological changes (historical, not a second roadmap) |

## Separate binding or functional files

- [Repository README](../README.md), [contributor guide](../CONTRIBUTING.md), [security policy](../SECURITY.md), [agent instructions](../AGENTS.md), and the dated [AI usage audit](../AI_USAGE_AUDIT.md).
- [AGPL community license](../LICENSE), [commercial](../LICENSE-COMMERCIAL.md) and [enterprise](../LICENSE-ENTERPRISE.md) instruments, [CLA](../CLA.md), [trademark](../TRADEMARK.md), [third-party notices](../THIRD_PARTY_NOTICES.md) and [license inventory](../THIRD_PARTY_LICENSES/README.md).
- [Documentation assets inventory](assets/README.md), [supplied UI design sources](../web%20ui%20files%20and%20rendering/README.md) and [payload attribution](../src/whaxon/data/payloads/ATTRIBUTION.md). Historical categorized file inventory: [2026-11-05 ownership register](archive/DOCUMENTATION_OWNERSHIP_2026-11-05.md).
- Structured acceptance CSVs, checked-in tests, actual deployment configurations, screenshots and generated evidence remain as data/evidence rather than new narrative masters.

## Integrity rules

1. The root product roadmap decides priorities and release gates. The subject masters provide detailed explanation but cannot overrule it.
2. Complete the agreed Engine V2, UI V2, and remaining solo-v1.0 implementation scope before final external qualification. Internal tests continue during development; do not confuse those checks with post-completion release qualification.
3. Update the subject master in place. Add standalone files only for legally independent documents, functional source assets, or reproducible machine-readable evidence.
4. Historical source documents that carry acceptance, security, legal, provenance, or detailed design evidence are retained at their documented paths. Their dated claims are not current status; do not remove them merely to reduce document count.
