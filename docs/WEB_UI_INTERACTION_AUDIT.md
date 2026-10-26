# WHAXON Web UI Interaction Audit

## Scope and status

This audit covers the new designs in `web ui files and rendering/`, the existing Flask routes, and the existing legacy UI. The new UI serves the original design HTML directly; the source design files are not replaced with a newly invented UI. The legacy templates and static assets remain unchanged and are available at `/legacy-ui`.

- **WIRED** — connected to an existing backend route; not browser-tested.
- **HIDDEN** — prototype-only actions or data are hidden because there is no suitable backend operation.
- **NOT TESTED** — intentional: do not run tests or browser checks until all pages are wired.

## Page wiring

| Page / route | Existing backend used | Current state |
|---|---|---|
| Dashboard — `/ui` | `GET /api/status`, `GET /api/history`, `GET /api/report?format=json` | WIRED: live summary counts and history rows; prototype-only workspace, upload, mock deployment, and archive actions hidden |
| Scope & Targets — `/ui/scope-and-targets` | `GET /api/scope`, `POST /api/scope/check` | WIRED: live in-scope/excluded rules and scope-check action; add/import/commit controls hidden because no scope mutation/import endpoint exists |
| Run & Orchestration — `/ui/run-and-orchestration` | `GET /api/tools`, `POST /api/run`, `GET /api/jobs/<id>/stream`, `POST /api/jobs/<id>/cancel` | WIRED: tool selection, target input, scope-guarded run, SSE output and cancellation. Arbitrary arguments, sub-tool injection, and mock pipeline controls hidden |
| Trust Layer & Findings — `/ui/trust-layer-and-findings` | `GET /api/report?format=json`, `POST /api/validate/<job>/<seq>`, `POST /api/retest/<job>/<seq>` | WIRED: live findings, dynamic card list, live severity/state filters, detail metadata, validation for candidates and retest for verified findings. Mock proof claims, mark-fixed, issue-export, and finding-approval actions hidden |
| Approvals queue — `/ui/trust-layer-approvals-queue-modal` | `GET /api/ai/pending`, `POST /api/ai/runs/<id>/answer` | WIRED to the existing AI-run approval mechanism only; it does not invent a finding-approval API |
| PTES Coverage & Reports — `/ui/ptes-coverage-and-reports` | `GET /api/report?format=json|md|html|pdf` | WIRED: live report summary/findings, Markdown preview, Markdown/HTML/PDF/JSON downloads |
| BAS & Detection Validation — `/ui/bas-and-detection-validation` | `GET /api/history`, `GET /api/coverage/<job>`, report formats | PARTIALLY WIRED: real findings and recorded coverage gaps are shown; unsupported blue-telemetry and SIEM deployment actions hidden |
| Remediation Retest Studio — `/ui/remediation-retest-studio` | `GET /api/report?format=json`, `POST /api/retest/<job>/<seq>` | WIRED: live verified-finding retest queue |
| Attack Surface & Continuous Monitoring — `/ui/attack-surface-and-continuous-monitoring` | `GET /api/pivot/graph` | WIRED as a live relationship/edge view; continuous recon, cloud-probe, ACL-remediation and certificate-renewal actions hidden because no matching endpoints exist |
| Job Execution History — `/ui/job-execution-history` | `GET /api/history` | WIRED: live job rows and search; hard-coded counts, integrity claims, and unsupported export/verification controls hidden |
| Evidence File Inspector — `/ui/evidence-file-inspector` | `GET /api/history`, `GET /api/jobs/<id>/evidence`, `GET /api/jobs/<id>/evidence/<seq>/download` | WIRED: choose a job, list its evidence, download recorded evidence; mock Merkle sync, TAR export, reparsing and issue-tracker actions hidden |
| Correlated Attack Chains — `/ui/correlated-attack-chains` | `GET /api/report?format=json` (`chains`) | WIRED to recorded chain data; unsupported execution/replay actions hidden |
| System Diagnostics & Health — `/ui/system-diagnostics-and-health` | `GET /api/health` | WIRED read-only health display; restart/diagnostic actions hidden because no matching endpoints exist |
| Adapter & Plugin Manager — `/ui/adapter-and-plugin-manager` | `GET /api/tools` | WIRED to the live tool catalog and availability metadata; mock adapter registration, sync, resigning and configuration actions hidden |
| Settings & API Explorer / Secrets Vault — `/ui/settings-and-api-explorer`, `/ui/settings-and-secrets-vault` | `GET /api/settings` | WIRED read-only settings view with secret-like keys redacted; secret/token management and writes hidden |
| Threat Intel & Exploit Arsenal — `/ui/threat-intel-and-exploit-arsenal` | `GET /api/msf/modules/<type>`, `POST /api/msf/run`, `POST /api/scope/check`, `GET /api/pivot/candidates` | WIRED: live Metasploit module catalog, pivot candidates, and explicitly triggered module execution after a successful scope check; static CVE/EPSS claims hidden because no threat-feed endpoint exists |
| Compliance & Framework Crosswalk — `/ui/compliance-and-framework-crosswalk` | No compliance-mapping endpoint found | HIDDEN |
| Bug Bounty & Live Browser Studio — `/ui/bug-bounty-and-live-browser-studio` | No browser/issue-tracker integration endpoint found | HIDDEN |
| PTaaS Client Portal — `/ui/ptaas-client-portal` | No client-portal backend found | HIDDEN |
| Cryptographic Audit Log — `/ui/cryptographic-audit-log` | No corresponding cryptographic audit-log API found | HIDDEN |

## Cross-cutting implementation

- `/` redirects to the new design-based UI at `/ui`.
- The previous UI remains available at `/legacy-ui`; `templates/base.html`, `templates/index.html`, and the legacy static assets are not replaced.
- Page navigation uses the existing `data-path` values in the source HTML and allowlisted routes; unknown page links are hidden.
- The 21 canonical design HTML files are included in wheel/sdist packaging, and the existing design directory is copied into the Docker image. The server can resolve design files from a source checkout or the packaged `whaxon/ui_source` fallback.
- Mock global controls (workspace switcher, terminal-log shortcut, emergency-halt button, demo engagement/operator identifiers) are hidden or neutralized where no matching backend exists.
- API failures hide stale prototype data rather than silently presenting mock values as live results.
- No test, build, browser, or runtime validation has been run, per instruction. All states above are **WIRED, not PASS** until the complete wiring pass is finished and testing is authorized.
