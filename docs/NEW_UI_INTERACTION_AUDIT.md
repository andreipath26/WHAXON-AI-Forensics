# New Default Web UI — Interaction and Acceptance Audit

**Authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md` (especially the repository reality check, §19, §32.12, §34.2 step 5, and §38).

**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Audit baseline:** `main` before the default-route change at `aea6a2ff859301192b3133330a94ecc0e6a21cbf`.  
**Default-route change:** `8313b8af885d4c4f5711c4df0998f0e8523f9b33` (root redirects to `/ui-v2`).  
**Test assertion change:** `aa8fcd2b633b267e577ee32034e330bfb7bc9c71`.  
**CI:** the baseline main commit had a successful CI run; CI for the default-route/test commits was running when this audit was written. Do not treat the latter as passing until GitHub reports a successful conclusion.

This is a current-state audit, not a declaration that the UI is complete or deployment-ready.

## 1. Source-of-truth assets and preservation

The checked-in design package contains 32 HTML files and 32 PNG files, plus `obsidian_kinetic/DESIGN.md`. The HTML/PNG set includes versioned alternatives and duplicate top-level copies; these are retained as reference assets. The production implementation consists of 22 `ui_v2_*.html` templates and 22 corresponding web routes.

The new templates use the supplied Obsidian Kinetic visual system. The original `base.html`, `index.html`, `app.js`, `style.css`, and historical `docs/WEB_UI_INTERACTION_AUDIT.md` remain the deprecated interface/reference. They must not be redesigned, repurposed as the new UI, or overwritten as part of this work.

## 2. Entry points

| URL | Purpose | State |
|---|---|---|
| `/` | Default web entry point | Redirects to `/ui-v2` after commit `8313b8a`; CI pending at audit time |
| `/ui-v2` | Canonical Obsidian Kinetic dashboard | Implemented |
| `/ui-v2/dashboard` | Dashboard alias | Implemented |
| `/ui` | Previous web interface | Preserved as a compatibility/reference route |

## 3. Canonical screen-to-route map

| Design screen | Production route | Template | Browser test coverage |
|---|---|---|---|
| Dashboard / engagement hub | `/ui-v2` | `ui_v2_dashboard.html` | `test_web_ui_v2_dashboard.py`, `test_web_ui_v2_navigation.py` |
| Scope and targets | `/ui-v2/scope` | `ui_v2_scope.html` | `test_web_ui_v2_scope.py`, `test_web_ui_v2_scope_interactions.py` |
| Run and orchestration | `/ui-v2/run` | `ui_v2_run.html` | `test_web_ui_v2_run.py` |
| Verified findings / Trust Layer | `/ui-v2/findings` | `ui_v2_findings.html` | `test_web_ui_v2_findings.py` |
| Report / PTES coverage | `/ui-v2/report` | `ui_v2_report.html` | `test_web_ui_v2_report.py` |
| Reports and exports | `/ui-v2/reports` | `ui_v2_reports.html` | `test_web_ui_v2_reports.py` |
| Job execution history | `/ui-v2/history` | `ui_v2_history.html` | `test_web_ui_v2_history.py` |
| System diagnostics and health | `/ui-v2/diagnostics` | `ui_v2_diagnostics.html` | `test_web_ui_v2_diagnostics.py` |
| Evidence file inspector | `/ui-v2/evidence` | `ui_v2_evidence.html` | `test_web_ui_v2_evidence.py` |
| AI strategy / human gate | `/ui-v2/ai` | `ui_v2_ai.html` | `test_web_ui_v2_ai.py` |
| Remediation and retest studio | `/ui-v2/retest` | `ui_v2_retest.html` | `test_web_ui_v2_retest.py` |
| Correlated attack chains | `/ui-v2/chains` | `ui_v2_chains.html` | `test_web_ui_v2_chains.py` |
| Adapter and plugin manager | `/ui-v2/adapters` | `ui_v2_adapters.html` | `test_web_ui_v2_adapters.py` |
| Settings and secrets vault | `/ui-v2/settings` | `ui_v2_settings.html` | `test_web_ui_v2_settings.py` |
| Cryptographic audit log | `/ui-v2/audit` | `ui_v2_audit.html` | `test_web_ui_v2_audit.py` |
| Attack-surface monitoring | `/ui-v2/monitoring` | `ui_v2_monitoring.html` | `test_web_ui_v2_monitoring.py` |
| BAS / detection validation | `/ui-v2/bas` | `ui_v2_bas.html` | `test_web_ui_v2_auxiliary_pages.py` |
| Bug bounty / browser studio | `/ui-v2/bug-bounty` | `ui_v2_bug_bounty.html` | `test_web_ui_v2_bug_bounty.py`, auxiliary-page tests |
| Compliance crosswalk | `/ui-v2/compliance` | `ui_v2_compliance.html` | `test_web_ui_v2_auxiliary_pages.py` |
| PTaaS client portal | `/ui-v2/ptaas` | `ui_v2_ptaas.html` | `test_web_ui_v2_ptaas.py`, auxiliary-page tests |
| Threat intelligence / exploit arsenal | `/ui-v2/threat-intel` | `ui_v2_threat_intel.html` | `test_web_ui_v2_auxiliary_pages.py` |
| Trust Layer approvals queue | `/ui-v2/approvals` | `ui_v2_approvals.html` | `test_web_ui_v2_auxiliary_pages.py` |

All 22 routes have a corresponding production template. The browser suite currently has 21 UI-v2 test modules; some related pages share the auxiliary-page module.

## 4. Live workflows with browser coverage

The repository contains Playwright coverage for the following live behaviors:

- Dashboard: live job history, filtering, JSON history export, emergency halt reporting, CLI-help/credential guidance, and Burp XML import.
- Scope: loading and persisting scope, malformed-rule rejection, explicit confirmation before disabling enforcement, and target checks.
- Run: live tool catalog, guarded passive/active run paths, output/status handling, out-of-scope rejection, and cancellation/abort controls.
- Findings: live findings, finding inspection, validation/retest requests, filtering, and scope-aware state.
- Reports: live report API data, JSON/Markdown downloads, preview modal, and truthful unavailability of unsupported evidence/configuration.
- History: live records, filters, and JSON export.
- Diagnostics: live health/tool/dependency APIs, read-only diagnostics, remediation-plan review, and guarded installation workflows.
- Evidence, AI, retest, attack chains, adapters, settings, audit, monitoring, BAS, bug bounty, PTaaS, compliance, threat intelligence and approvals: page-specific live data and interaction tests exist in their named test modules.

Presence of a test module does not mean every control on that page has passed independent acceptance. The CI result for the candidate commit must be checked.

## 5. Reference-only controls and simulated content

The live UI intentionally disables or hides controls for which there is no safe implemented backend. Examples verified in the current tests/source include:

- Adapter mock execution and manifest re-signing; adapter configuration mutation is disabled.
- Diagnostics actions that would claim simulated subsystem restarts, probes or benchmarks.
- Report configuration selectors that do not affect the live report API, sample proof/evidence, and unsupported gap filters.
- Monitoring's simulated recon trigger and unimplemented asset mutations.
- BAS, bug-bounty, PTaaS, compliance and threat-intelligence actions that imply exploit execution, deployment, client delivery or other unsupported operations.
- Sample engagement, target, finding, telemetry and diagnostic data is removed or hidden in the live presentation.

These controls must remain disabled/hidden until a real backend implementation, authorization boundary and test exist. A disabled visual reference control is not a delivered feature.

## 6. Acceptance gaps — still open

1. **Visual regression:** the current UI-v2 browser tests exercise rendering and interactions, but the test modules do not contain screenshot-baseline comparisons (no `to_have_screenshot`/equivalent snapshot assertions were found). The supplied PNGs are present, but automated pixel/perceptual comparison against approved baselines is not yet evidenced.
2. **CLI/web service parity:** the roadmap requires CLI verbs to use shared service modules and a parity test for CLI/web surfaces (or documented deliberate differences). A dedicated parity test was not identified in the current test tree. Audit the actual CLI/web command surface before claiming this gate passed.
3. **Accessibility:** browser tests exist, but a full keyboard/focus-management/screen-reader/WCAG 1.4.1 acceptance pass is not evidenced by the current test names or contents reviewed. Add automated checks where practical and record manual checks separately.
4. **All-control inventory:** the 22 pages have dedicated or shared browser tests, but a complete per-control inventory proving every visible control is wired, disabled or hidden has not yet been recorded. Continue page-by-page and extend tests for any uncovered controls.
5. **Deployment dependencies:** the supplied pages load Tailwind and web fonts from external CDNs. Decide and test whether the supported deployment requires network-independent bundled assets; do not silently claim air-gapped readiness while external runtime assets remain.
6. **Default route:** root redirect and legacy-route regression assertions were committed after baseline CI. Await and inspect the CI result for `aa8fcd2`.

## 7. Branch and PR reconciliation

At audit time there were no open pull requests. The canonical UI integration PRs #37, #41 and #42, and the subsequent UI wiring/truthfulness PRs #43–#73, were already merged into `main`. The old full-wiring PR #16 was closed unmerged as a draft; its own description explicitly said not to merge because wiring and browser acceptance were incomplete. PRs #33–#36 were superseded by the later integrated UI work. Their old branch tips must not be blindly merged over newer main code.

No new branch or alternate UI was created for this audit. Stale historical branches are not merge candidates merely because they still exist.

## 8. Release gate

Do not mark the new UI DONE or deployment-ready until the acceptance gaps above are closed, browser and visual regression checks pass on the candidate commit, security regressions pass, and the roadmap's §38 release checklist is updated with observed evidence.