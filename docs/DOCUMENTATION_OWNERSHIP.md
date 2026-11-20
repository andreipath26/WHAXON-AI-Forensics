# WHAXON — documentation ownership and retirement policy

The Engine V2 requirement and checkpoint ledgers are live CSV navigation indexes. Keep their `implementation_candidate`, `test_candidate`, `source_paths` and `related_test_definition` columns pointing to existing files after every consolidation. `tests/test_documentation_integrity.py` enforces this condition and the 75-entry cardinality in CI. Dated narrative history remains intact.

**Active inventory and status baseline: `main` `f32ce0913d460f046f6d984ec54a1f7f5d775409` (2026-11-21).** PR #226's exact head passed CI, README freeze, and dashboard acceptance before merge; see [the G10 decision](ENGINE_V2_G10_RELEASE_DECISION.md) for exact run links and remaining release gates. This document specifies canonical owners; [docs/README](README.md) is the reader-facing index.

## Authoritative subject ownership

| Subject | Owner file |
|---|---|
| Product roadmap, competitor priorities, status | [WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) |
| Engine V2 | [ENGINE_V2_MASTER.md](ENGINE_V2_MASTER.md) |
| V1 acceptance | [V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) |
| UI V2 | [V2_UI_MANDATORY_CROSSWALK.md](V2_UI_MANDATORY_CROSSWALK.md) |
| App architecture, AI and API | [APPLICATION_ARCHITECTURE_MASTER.md](APPLICATION_ARCHITECTURE_MASTER.md) |
| Installation, deployment, operator instructions | [OPERATIONS_MASTER.md](OPERATIONS_MASTER.md) |
| Findings, reporting, evidence, retention | [EVIDENCE_AND_REPORTING_MASTER.md](EVIDENCE_AND_REPORTING_MASTER.md) |
| Commercial planning, CBC, funding, editions | [CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md](CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md) |
| Bug bounty authorization, programmes and differential workflows | [bounty-addon.md](bounty-addon.md) |
| Business-impact severity methodology | [business-impact.md](business-impact.md) |
| Engineering governance, previous retirement records | [PROJECT_GOVERNANCE_MASTER.md](PROJECT_GOVERNANCE_MASTER.md) |
| Release history | [CHANGELOG.md](CHANGELOG.md) |

## Permanently distinct files

The bug bounty module and business-impact calculator are independent technical specifications, not chapters of the CBC commercial playbook. The original `web ui files and rendering/obsidian_kinetic/DESIGN.md` remains at its canonical design-source path and must not be deleted or silently replaced by a consolidated copy.


The root `README.md`, `AGENTS.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CLA.md`, `LICENSE*`, `TRADEMARK.md`, `THIRD_PARTY_NOTICES.md` and third-party license inventory have distinct operational or legal roles; do not absorb/delete these. Retain asset readmes and data-provenance files adjacent to assets, plus CSV evidence registers and historical Git commits.

## Rules for new and obsolete documents

1. Write current advice into the existing owner; do not create another `*_STATUS`, `*_AUDIT`, `*_ROADMAP`, `*_ACCEPTANCE`, or `*_PLAN` Markdown narrative for the same topic.
2. A dated technical record may be appended to the master under a clear evidence boundary. Keep machine-readable verification results in test artifacts or CSVs.
3. Before deleting a standalone narrative, incorporate all unique content into its subject master, replace internal references, and verify no source/test/license consumer requires the old path.
4. Do not delete binding policy or data files on the assumption they are obsolete; their ownership is distinct. Do not delete historical acceptance, security, legal, or provenance records merely to reduce document counts.
5. Treat source and CI on exact HEAD as behavioral truth; historical text embedded in masters is evidence, not an updated deployment verdict.

## Consolidation record

**2026-11-05 consolidation:** Commit `2a6290b23ea5e51b60f92292470b818efd42fd0b` removed 56 narrative Markdown paths under the stated consolidation plan. A later full-text audit found that some source records had not been fully retained and that several consolidated files contained literal `tokens truncated` strings. The document restoration on 2026-11-20 restores the missing historical sources at their original paths, repairs the affected UI and application documentation, and preserves the previous categorized inventory at [the archived 2026-11-05 register](archive/DOCUMENTATION_OWNERSHIP_2026-11-05.md). This archive is a historical inventory, not a current file list.

The standalone `WHAXON Competitor Capability and Remediation Roadmap Addendum.md` was removed in that consolidation (`2a6290b23ea5e51b60f92292470b818efd42fd0b`); its complete text is embedded in Part II of the root Product Roadmap. This addendum is not a competitor-by-competitor assessment: the sourced competitor capability matrix and seeded-lab comparison are separately deferred as P7-02, after the solo UI/release gate. Use the Product Roadmap Part II anchor instead of the retired filename.
