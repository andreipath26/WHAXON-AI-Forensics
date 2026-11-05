# WHAXON — documentation ownership and consolidation register

**Inventory baseline:** `main`, 2026-11-05, immediately after Engine V2 consolidation. This is a navigational inventory of root and `docs/` Markdown files (not payload examples, captured evidence, or design asset subfolders). The categories are an organizational classification, not a statement that every file's factual assertions have been revalidated.

## One authoritative master per subject

| Subject | Current authoritative document | What remains subordinate |
|---|---|---|
| Product scope, priorities, roadmap and release gates | [WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) | Competitor roadmap addenda, dated state and changelog |
| Engine V2 architecture, implementation, operational acceptance | [ENGINE_V2_MASTER.md](ENGINE_V2_MASTER.md) | 16 historical Engine V2 input documents integrated into master; dated CSV evidence, tests and code remain independent proof |
| V1 baseline and acceptance | [V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md) | Dated reconciliation checkpoints, requirement ledgers |
| UI V2 page contract and design acceptance | [V2_UI_MANDATORY_CROSSWALK.md](V2_UI_MANDATORY_CROSSWALK.md) | Page-specific interaction audits, visual evidence and control inventory |
| Commercial partnership and investor playbook | [CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md](CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md) | Supporting commercial and competitor research, which must not override the playbook |
| Repository cleanup and document dispositions | [DOCUMENTATION_RECONCILIATION.md](DOCUMENTATION_RECONCILIATION.md) | Candidate deletion evidence and historical retirement notes |
| User/operator documentation | [README.md](README.md) | Task-specific guides such as deployment, scope and troubleshooting |

**Documentation rule:** Before adding a new roadmap, architecture, acceptance or status Markdown file, update the existing subject master or append dated evidence in its existing section. Only create a separate file for a truly independent contract, operator guide or immutable evidence record. Link such files from the master and mark the source/commit/date. Do not delete historical acceptance, security, legal or provenance records merely to reduce document counts. Treat old branch documents as review candidates, never automatically as newer truth.

## Inventory of root and docs Markdown documents

### Product roadmap and status (4)

- [WHAXON Competitor Capability and Remediation Roadmap Addendum.md](../WHAXON%20Competitor%20Capability%20and%20Remediation%20Roadmap%20Addendum.md)
- [WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md)
- [CHANGELOG.md](CHANGELOG.md)
- [STATE.md](STATE.md)

### Engine V2 (17)

- [ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md)
- [ENGINE_V2_BASELINE_INVENTORY.md](ENGINE_V2_BASELINE_INVENTORY.md)
- [ENGINE_V2_CODE_VS_ROADMAP_AUDIT_2026-11-03.md](ENGINE_V2_CODE_VS_ROADMAP_AUDIT_2026-11-03.md)
- [ENGINE_V2_E1_ACCEPTANCE.md](ENGINE_V2_E1_ACCEPTANCE.md)
- [ENGINE_V2_E1_QUEUE_LEASE_PRIVACY.md](ENGINE_V2_E1_QUEUE_LEASE_PRIVACY.md)
- [ENGINE_V2_E3_PHASE_ACCEPTANCE.md](ENGINE_V2_E3_PHASE_ACCEPTANCE.md)
- [ENGINE_V2_E3_RECOVERY_BOUNDARIES.md](ENGINE_V2_E3_RECOVERY_BOUNDARIES.md)
- [ENGINE_V2_E3_RUN_REQUEST_AUDIT_EVENTS.md](ENGINE_V2_E3_RUN_REQUEST_AUDIT_EVENTS.md)
- [ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md](ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md)
- [ENGINE_V2_E5_PHASE_ACCEPTANCE.md](ENGINE_V2_E5_PHASE_ACCEPTANCE.md)
- [ENGINE_V2_E5_SERVICE_READINESS.md](ENGINE_V2_E5_SERVICE_READINESS.md)
- [ENGINE_V2_E6_CONTRACT_FIRST_ACCEPTANCE.md](ENGINE_V2_E6_CONTRACT_FIRST_ACCEPTANCE.md)
- [ENGINE_V2_E6_DEPLOYMENT_GATE_LEDGER.md](ENGINE_V2_E6_DEPLOYMENT_GATE_LEDGER.md)
- [ENGINE_V2_E6_SERVICE_UI_HANDOFF_MATRIX.md](ENGINE_V2_E6_SERVICE_UI_HANDOFF_MATRIX.md)
- [ENGINE_V2_EVIDENCE_MATRIX.md](ENGINE_V2_EVIDENCE_MATRIX.md)
- [ENGINE_V2_MASTER.md](ENGINE_V2_MASTER.md)
- [ENGINE_V2_PROVIDER_CAPABILITY_IMPLEMENTATION.md](ENGINE_V2_PROVIDER_CAPABILITY_IMPLEMENTATION.md)

### V1 release and acceptance (2)

- [V1_0_ACCEPTANCE_RECONCILIATION_2026-11-03.md](V1_0_ACCEPTANCE_RECONCILIATION_2026-11-03.md)
- [V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md](V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md)

### Web UI and design (7)

- [NEW_UI_INTERACTION_AUDIT.md](NEW_UI_INTERACTION_AUDIT.md)
- [UI_CONTROL_INVENTORY.md](UI_CONTROL_INVENTORY.md)
- [V2_UI_MANDATORY_CROSSWALK.md](V2_UI_MANDATORY_CROSSWALK.md)
- [WEB_UI_INTERACTION_AUDIT.md](WEB_UI_INTERACTION_AUDIT.md)
- [first-run-installation-redesign.md](first-run-installation-redesign.md)
- [report-redesign.md](report-redesign.md)
- [report-visual-design.md](report-visual-design.md)

### Funding, partnership, business (6)

- [CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md](CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md)
- [bounty-addon.md](bounty-addon.md)
- [business-impact.md](business-impact.md)
- [commercial-licensing.md](commercial-licensing.md)
- [editions.md](editions.md)
- [licensing.md](licensing.md)

### Architecture, execution and tools (11)

- [ENGINEERING_EXECUTION_MODEL.md](ENGINEERING_EXECUTION_MODEL.md)
- [METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md](METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md)
- [TOOL_INTELLIGENCE_AND_ONBOARDING.md](TOOL_INTELLIGENCE_AND_ONBOARDING.md)
- [adapters.md](adapters.md)
- [agent-architecture.md](agent-architecture.md)
- [architecture.md](architecture.md)
- [autonomous-loop.md](autonomous-loop.md)
- [plugins.md](plugins.md)
- [scope.md](scope.md)
- [session-execution.md](session-execution.md)
- [tools.md](tools.md)

### Operations and governance (15)

- [AGENTS.md](../AGENTS.md)
- [AI_USAGE_AUDIT.md](../AI_USAGE_AUDIT.md)
- [CLA.md](../CLA.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [LICENSE-COMMERCIAL.md](../LICENSE-COMMERCIAL.md)
- [LICENSE-ENTERPRISE.md](../LICENSE-ENTERPRISE.md)
- [SECURITY.md](../SECURITY.md)
- [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)
- [TRADEMARK.md](../TRADEMARK.md)
- [DATA_RETENTION.md](DATA_RETENTION.md)
- [DOCUMENTATION_RECONCILIATION.md](DOCUMENTATION_RECONCILIATION.md)
- [dependency-readiness.md](dependency-readiness.md)
- [deployment.md](deployment.md)
- [getting-started.md](getting-started.md)
- [troubleshooting.md](troubleshooting.md)

### Other developer / user guides (10)

- [README.md](../README.md)
- [README.md](README.md)
- [ai.md](ai.md)
- [api.md](api.md)
- [assets/README.md](assets/README.md)
- [demo.md](demo.md)
- [findings.md](findings.md)
- [interfaces.md](interfaces.md)
- [reports-and-evidence.md](reports-and-evidence.md)
- [screenshots.md](screenshots.md)

## Follow-up reconciliation policy

1. Compare current main, not a stale branch, before carrying any old-source assertions forward.
2. Preserve exact-head CI, manual production deployment gates, and unresolved acceptance independently.
3. Whenever a master subsumes a historical source, keep Git history and old links functional. Retire an old path only after checking cross-references and verifying its full useful content was incorporated.
4. No open pull request is merge-approved solely because GitHub reports it mergeable; require non-draft state, applicable checks and explicit project gates.
