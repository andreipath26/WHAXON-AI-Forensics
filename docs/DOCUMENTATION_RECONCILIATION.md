# Repository-wide documentation reconciliation

**Review date:** 2026-11-02  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Branch reviewed:** `main`  
**Baseline before this reconciliation:** `e9b2f02`  
**Inventory:** 102 Markdown files in the recursive Git tree at that baseline.

## Executive result

This repository's Markdown inventory is not a single coherent set of current product documentation. It mixes current operator guides with roadmap proposals, historical implementation plans, research evidence, generated sample reports, vendored payload references, legal records and imported GitHub-page captures. A substantial portion was carried forward from earlier WHAXON development or collected as research artifacts. Their presence must not be mistaken for current implementation or release evidence.

The documentation index now classifies these sources. The unissued v1.0.0 release-note draft has been replaced with a clear disclaimer; older roadmap and web-page captures are explicitly archival. Current operator instructions are separated from implementation records and proposed designs.

This is a **documentation status and truthfulness reconciliation**, not a declaration that the product has passed v1.0 acceptance. The root roadmap §38 remains the controlling release gate and remains OPEN.

## Source-of-truth hierarchy

1. **Current behavior:** source code and tests on the exact `main` commit being reviewed.
2. **Release acceptance and work order:** root `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, especially §0 and §38. A DONE marker elsewhere does not close §38.
3. **Operator instructions:** root `README.md` and the current guides linked under [docs/README.md](README.md).
4. **Dated status:** [STATE.md](STATE.md), which must cite exact commits and CI runs.
5. **Historical evidence/design:** useful for provenance and rationale only; never use it as proof of current behavior.

No roadmap, design document, screenshot, sample report, payload file, old changelog entry or imported web capture independently proves a shipped capability.

## Source-checked product facts

| Area | Current repository evidence | Required claim boundary |
|---|---|---|
| Package/release identity | `pyproject.toml`: package `whaxon`, version `0.11.16`, Python `>=3.11`, Beta classifier. | Do not call v1.0.0 released. Roadmap §38 remains OPEN. |
| Interfaces | CLI dispatcher in `src/whaxon/cli.py`; optional TUI, GUI and web extras in `pyproject.toml`; Flask and Waitress entry points in `src/whaxon/interfaces/web/`. | Optional dependencies and host requirements apply. Interface presence does not mean every workflow is accepted. |
| Browser UI | Root route redirects to `/ui-v2`; 22 `ui_v2_*.html` templates exist. The former `/ui` is retained as legacy/reference. | UI implementation and browser tests do not equal visual, accessibility, parity or production acceptance. |
| Setup | `src/whaxon/interfaces/cli/setup_cmd.py` supports Core/Standard/Full/Custom preview, optional venv creation, exact-plan Python package approval, and a separate curated OS-tool installation flow. | Profile preview is read-only. Python and OS package installation are separate consent-bound operations; this is not a general-purpose package manager. |
| Web serving | `whaxon web` starts Flask in the foreground with debug and reloader disabled. `whaxon serve` uses Waitress in the foreground; POSIX daemon mode is also implemented. Root `whaxon.service` exists. | Do not describe `whaxon web` as the production WSGI server. Follow remote-authentication and reverse-proxy requirements. |
| Execution and orchestration | Shared catalog/runner, persistent job store, event-driven follow-up automation, worker/scheduler and Engine v2 mission/task primitives exist. | Do not imply exactly-once execution, complete Engine v2 migration, full durable recovery guarantees or broad provider coverage without separate evidence. |
| Scope | Scope manager and guarded runner paths perform application-level checks; tests cover fail-closed behavior. | Scope preflight is not a firewall, DNS pin or guarantee against redirects/secondary requests by external tools. |
| Findings and validation | Normalized adapter findings and deterministic validators exist for selected finding types/request shapes; retest distinguishes fixed/still-vulnerable/inconclusive. | A candidate is not verified; a verified result is limited to its specific check. Payload-library presence does not mean a validator supports every technique. |
| Reporting | Job and engagement report paths and Markdown/HTML/PDF/JSON outputs exist in report source and CLI/API. | Output completeness and appendix selection differ by format. Do not claim every format contains identical evidence or all finding severities in the detailed appendix. |
| Bug bounty | Review-oriented ingestion/parsing and policy-related primitives exist. | The broader differential-session, workflow-inference and autonomous programme subsystem in `docs/bounty-addon.md` is a design, not a shipped end-to-end capability. |
| Metasploit | RPC, module, session, adapter and pivot-related components exist. | The full integration matrix in `docs/METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md` is not wholly implemented or accepted. |
| Engine v2 | Versioned contracts, persistence, scheduler/recovery primitives and an initial provider slice are present. | Engine v2 remains partially implemented; use roadmap §§49–52 and the crosswalk for open gates. It is not a generally accepted production mission engine. |
| Licensing | Root `LICENSE` is AGPL-3.0-or-later; commercial licensing is separately discussed. | Do not imply an enterprise edition, support commitment or commercial agreement exists without a signed agreement. |

## Complete Markdown inventory classification

The 102 Markdown files at the baseline are classified below. These classifications describe the role of each file, not a guarantee that every sentence in a dated record has been independently revalidated.

### Current public/operator guidance and maintained references

- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`
- `docs/README.md`, `docs/STATE.md`, `docs/CHANGELOG.md`
- `docs/getting-started.md`, `docs/dependency-readiness.md`, `docs/troubleshooting.md`
- `docs/scope.md`, `docs/tools.md`, `docs/adapters.md`, `docs/findings.md`
- `docs/reports-and-evidence.md`, `docs/interfaces.md`, `docs/api.md`, `docs/deployment.md`
- `docs/ai.md`, `docs/architecture.md`, `docs/DATA_RETENTION.md`, `docs/plugins.md`
- `docs/editions.md`, `docs/licensing.md`, `docs/commercial-licensing.md`
- `docs/ENGINEERING_EXECUTION_MODEL.md` (engineering process, not a product feature description)

### Roadmap, proposed architecture or dated acceptance records

These files may define intended future behavior or track work, but must not be represented as implemented solely because they are present:

- Root `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md` (authoritative plan; not itself proof of implementation).
- Root `WHAXON Competitor Capability and Remediation Roadmap Addendum.md` (queued direction).
- `docs/NEW_UI_INTERACTION_AUDIT.md` (current dated UI implementation/acceptance audit; open gates remain).
- `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md` (target architecture plus dated implementation updates).
- `docs/TOOL_INTELLIGENCE_AND_ONBOARDING.md` (proposed subsystem design).
- `docs/METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md` (broader integration design; partial implementation only).
- `docs/bounty-addon.md` (draft add-on; not a shipped full bug-bounty subsystem).
- `docs/first-run-installation-redesign.md` (implementation/acceptance record; operator guide is `docs/dependency-readiness.md`).
- `docs/CBC_2026_WHAXON_PARTNERSHIP_AND_INVESTOR_PLAYBOOK.md` (date-sensitive commercial/funding research; reverify external facts before use).

### Historical or superseded engineering/design records

- `docs/agent-architecture.md`
- `docs/autonomous-loop.md`
- `docs/session-execution.md`
- `docs/business-impact.md`
- `docs/report-redesign.md`
- `docs/report-visual-design.md`
- `docs/ENGINE_V2_BASELINE_INVENTORY.md`
- `docs/WEB_UI_INTERACTION_AUDIT.md`
- `AI_USAGE_AUDIT.md` (author's dated disclosure, not a continuously updated provenance log)

### Dated research and experiment archive — preserve as evidence, not current product truth

- `docs/WHAXON_EXPERIMENT_AUDIT_2026-10-25.md`
- `whaxon-experiment-2026-10-25/docs/environment-report.md`
- `whaxon-experiment-2026-10-25/docs/findings.md`
- `whaxon-experiment-2026-10-25/docs/limitations.md`
- `whaxon-experiment-2026-10-25/docs/literature-review.md`
- `whaxon-experiment-2026-10-25/docs/privilege-boundary-assessment.md`
- `whaxon-experiment-2026-10-25/docs/research-contribution.md`
- `whaxon-experiment-2026-10-25/docs/research-gaps.md`
- `whaxon-experiment-2026-10-25/docs/research-hypotheses.md`
- `whaxon-experiment-2026-10-25/docs/research-map.md`
- `whaxon-experiment-2026-10-25/docs/scope-and-rules.md`
- `whaxon-experiment-2026-10-25/docs/test-plan.md`
- `whaxon-experiment-2026-10-25/docs/verification-results.md`
- `whaxon-experiment-2026-10-25/logs/decision-log.md`
- `whaxon-experiment-2026-10-25/logs/errors-and-blockers.md`
- `whaxon-experiment-2026-10-25/logs/experiment-index.md`
- `whaxon-experiment-2026-10-25/logs/hypothesis-ledger.md`
- `whaxon-experiment-2026-10-25/logs/publication-log.md`
- `whaxon-experiment-2026-10-25/logs/research-journal.md`
- `whaxon-experiment-2026-10-25/logs/tool-inventory.md`
- `whaxon-experiment-2026-10-25/logs/trace-availability.md`
- `whaxon-experiment-2026-10-25/logs/verification-log.md`
- `whaxon-experiment-2026-10-25/research/whaxon_execution_evidence.md`

The experiment records are intentionally dated and preserved. Their target-specific findings, environment observations and test totals do not automatically describe current WHAXON behavior. Git history may retain earlier sensitive blobs even when the current tree has been sanitized.

### Imported GitHub page captures and old copied documents

- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_1.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_2.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_ai_forensics.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_ai_forensics_commits.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_ai_forensics_tree_main.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_blob_main_docs.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_commit.md`
- `web ui files and rendering/extracted_text_from_https_github.com_andreipath26_whaxon_commits_main.md`
- `web ui files and rendering/whaxon_road_map_whats_next_full_scope.md` (old copied roadmap, superseded).
- `web ui files and rendering/whaxon_v1.0.0_deployment_release_notes.md` (unissued draft; replaced by a disclaimer, not a release record).
- `web ui files and rendering/obsidian_kinetic/DESIGN.md` (supplied visual design reference; not runtime acceptance evidence).

### Generated sample reports, payload references and legal/provenance records

- `data/proof-dvwa/README.md`, `data/proof-dvwa/engagement.md`, `data/proof-dvwa/job-137b9002ee9a.md`, `data/proof-dvwa/job-3fec9011c57f.md`, `data/proof-dvwa/job-d76244691d83.md`, `data/proof-dvwa/job-deaa28ed3bcf.md` — dated generated sample evidence, not a current benchmark.
- `src/whaxon/ai/prompts/planner_v1.md` — runtime prompt resource, not operator documentation.
- `src/whaxon/data/payloads/ATTRIBUTION.md`, `command_injection.md`, `crlf.md`, `lfi_rfi.md`, `sql_injection.md`, `ssrf.md`, `xss.md` — vendored reference/payload material; not a validator support matrix.
- `assets/README.md`, `docs/assets/README.md` — asset inventories and screenshot provenance.
- `CLA.md`, `LICENSE-COMMERCIAL.md`, `LICENSE-ENTERPRISE.md`, `THIRD_PARTY_NOTICES.md`, `THIRD_PARTY_LICENSES/README.md`, `TRADEMARK.md` — legal, licensing and third-party notices; not feature descriptions.

## CI and release evidence at review time

The pre-reconciliation documentation baseline `e9b2f02` had workflow run [#41452761676](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41452761676). Python 3.13 reported **1 failed, 1,369 passed, 14 skipped**. The failure was `tests/test_web_ui_v2_auxiliary_pages.py::test_approvals_refresh_queue_and_halt_use_live_apis[chromium]`: clicking Refresh queue did not cause the additional `/api/ai/pending` request expected by the test. Other jobs in that run passed. This failure remains an open verification item and is not attributed to documentation edits without further diagnosis.

The reconciliation itself is committed as `f0773d5` (18 files changed). Its exact-commit CI run [#41456487674](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41456487674) was queued when this register was written; do not describe that commit as CI-green until the run completes. A prior green run on a different commit is not a green result for the current HEAD. Before financing or release, record the exact candidate SHA, full CI result, unresolved failures and the evidence for each material product claim.

## Remaining reconciliation and due-diligence controls

- Keep operator instructions in the current guides; do not copy steps from old captures or design proposals.
- When a code change alters behavior, update the relevant current guide, tests and changelog in the same change.
- Mark new proposals as proposed/draft and identify the source/test evidence required to promote them to implemented.
- Keep experiment evidence immutable; correct interpretation in a separate current audit rather than rewriting the original record.
- Recheck date-sensitive funding, event, vendor, dependency and external-tool information before presenting it externally.
- Never describe a roadmap DONE marker, route/template, payload list, screenshot, sample report or historic CI run as proof of v1.0 release acceptance.
