# WHAXON Web UI Interaction Audit

## Governing rule

The roadmap at `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md` is the source of truth for product scope. **The UI must never invent state or demonstrate an unimplemented feature with mock data.**

- Keep the canonical HTML files under `web ui files and rendering/` unchanged as the design source of truth.
- For a feature that is not implemented or not yet correctly bound to real data/actions, hide its existing content in the served page. Do not replace it with a newly invented panel, sample data, or a pretend implementation.
- Hidden markup is retained in the original design file so it can be revealed when its real backend/service implementation and native UI wiring are ready.
- Show only values returned by the real backend. If a required endpoint fails, hide the affected page content rather than rewriting the design with fabricated fallback values.
- Keep the legacy UI and its templates/assets unchanged.
- Do not run tests, builds, browser checks, or runtime validation until all UI pages have been wired; status below is not a test pass.

## Current implementation status

**No runtime testing has been performed.** These statuses describe code inspection only.

| Page / route | Real backend surface | Current UI state |
|---|---|---|
| Dashboard — `/ui` | `GET /api/status`, `GET /api/history`, `GET /api/report?format=json`, `GET /api/tools`, optional `GET /api/msf/sessions` | Partially wired to live summary/history data. Demo operator, engagement, and sample target labels are hidden. If the MSF session endpoint fails, the UI reports unavailable rather than zero. Further review of every static dashboard value is still required before testing. |
| Scope & Targets — `/ui/scope-and-targets` | `GET /api/scope` | Existing table shows only live in-scope/excluded targets and their real state; unsupported columns and mutation/import modals are hidden. The scope-check API exists but is not exposed through a native control in this design yet. |
| Run & Orchestration — `/ui/run-and-orchestration` | `GET /api/tools`, `POST /api/run`, job stream and cancellation routes | Existing design controls are wired to the registered-tool/run flow. Unsupported pipeline, planner, and prototype actions are hidden. Not runtime-verified. |
| Trust Layer & Findings — `/ui/trust-layer-and-findings` | `GET /api/report?format=json`, validation and retest routes | Existing finding-card design is populated from returned findings; search and severity/status filters use those rows. Prototype proof claims and unsupported mark-fixed/export/approval actions are hidden. Not runtime-verified. |
| AI Approvals — `/ui/trust-layer-approvals-queue-modal` | `GET /api/ai/pending`, `POST /api/ai/runs/<id>/answer` | Existing page content is hidden pending wiring of the original controls to the real AI-run approval API. No replacement approval panel is generated. |
| PTES Coverage & Reports — `/ui/ptes-coverage-and-reports` | `GET /api/report?format=json|md|html|pdf` | Existing page content is hidden until report controls are wired in place. The prior custom replacement panel was removed; no new report UI is generated. |
| Job Execution History — `/ui/job-execution-history` | `GET /api/history` | Existing table uses live job rows and filters. Hard-coded counts and cryptographic integrity claims are hidden. Unsupported export/verification controls are hidden. Not runtime-verified. |
| Adapter & Plugin Manager — `/ui/adapter-and-plugin-manager` | `GET /api/tools` | Existing catalog design is populated from the live tool catalog. Category/status filters use returned tool data. Registration, configuration, sync, and signing actions without matching backend routes are hidden. Not runtime-verified. |
| Remediation Retest Studio — `/ui/remediation-retest-studio` | Retest API exists, but the new design is not yet wired through its native controls | Existing page content is hidden until its original controls are correctly wired. No substitute panel is inserted. This is UI wiring still to do, not a claim that the backend retest capability is absent. |
| Attack Surface & Continuous Monitoring — `/ui/attack-surface-and-continuous-monitoring` | Pivot graph/candidate APIs exist; continuous-monitoring operations are roadmap scope | Existing page content is hidden pending native design wiring and implementation of the roadmap's continuous-monitoring feature. No replacement panel or simulated asset graph is inserted. |
| BAS & Detection Validation — `/ui/bas-and-detection-validation` | Coverage ledger APIs exist; blue-team telemetry/SIEM actions are not implemented | Existing page content is hidden until the original design is wired to real coverage data. Unsupported detection/telemetry content is not shown as live. |
| Evidence File Inspector — `/ui/evidence-file-inspector` | Evidence list/download APIs exist, but the design's native controls are not yet wired | Existing page content is hidden until native wiring is complete. Merkle sync, integrity verification, TAR export, reparsing, and issue-tracker actions are not represented as working. |
| Correlated Attack Chains — `/ui/correlated-attack-chains` | Report correlation data exists; native design wiring is incomplete | Existing page content is hidden until the original design is wired to recorded correlation data. Execution/replay claims are not shown. |
| System Diagnostics & Health — `/ui/system-diagnostics-and-health` | `GET /api/health` | Existing page content is hidden pending native design wiring. No replacement diagnostics panel is generated. |
| Settings / API Explorer / Secrets Vault — `/ui/settings-and-api-explorer`, `/ui/settings-and-secrets-vault` | `GET /api/settings` | Existing page content is hidden pending native design wiring. Secret/token management actions without real routes are not shown as working. |
| Threat Intel & Exploit Arsenal — `/ui/threat-intel-and-exploit-arsenal` | Some Metasploit and pivot APIs exist; the roadmap's threat-feed integration is queued | Existing page content is hidden. A newly generated Metasploit runner was removed because it did not preserve the canonical design and is not a substitute for planned CVE/ExploitDB/ATT&CK/threat-feed integration. |
| Compliance & Framework Crosswalk — `/ui/compliance-and-framework-crosswalk` | No completed framework-mapping service/API identified | Existing page content is hidden; the roadmap's compliance mapping is not mocked. |
| Bug Bounty & Live Browser Studio — `/ui/bug-bounty-and-live-browser-studio` | No completed browser/issue-tracker integration identified | Existing page content is hidden; no simulated browser or issue activity is shown. |
| PTaaS Client Portal — `/ui/ptaas-client-portal` | Client portal is queued in roadmap §20.1 | Existing page content is hidden; no simulated client/workspace data is shown. |
| Cryptographic Audit Log — `/ui/cryptographic-audit-log` | No corresponding cryptographic audit-log API identified | Existing page content is hidden; no fabricated integrity state is shown. |

## Design and legacy preservation

- The canonical source designs under `web ui files and rendering/` remain the source of truth.
- The current branch's packaging changes include the existing design folder for source and packaged installs; no replacement UI design is generated.
- The legacy UI remains at `/legacy-ui`; its templates and static assets are not replaced.
- Unsupported-page handling only hides children of the existing page's `main` element. It does not remove original design files or insert a replacement content panel.
- The scope and report handlers no longer inject replacement panels; the AI approvals handler also hides the existing design until its native controls are wired.
- The UI wiring pass is **incomplete and untested**. Do not treat any row as runtime-verified. Continue page-by-page against the roadmap, using the existing HTML and revealing only elements that are bound to real backend state/actions.
