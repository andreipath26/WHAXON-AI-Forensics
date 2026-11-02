# New Default Web UI — Interaction and Acceptance Audit

> **Integration update — 2026-11-02, supersedes affected baseline statements below:** Four one-shot CLI commands now use `initialize(drain=False)` with regression coverage. Desktop startup targets `/ui-v2`. Test catalog consumers use the packaged seed; the duplicate tracked root catalog and unused qasync requirement/manifest entry are removed, while operator catalogs and protected legacy designs remain preserved. See [UI control inventory](UI_CONTROL_INVENTORY.md) for 793 source controls across 22 templates; static coverage does not establish complete runtime wiring, visual fidelity, accessibility or service parity. Local browser execution is blocked by unavailable Chromium downloads. The earlier CI/source records below describe their stated baseline, not acceptance of this integration.


**Authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, P4 and §38 G06; the previous section references are reconciled in its §50.

**Repository:** `andreipath26/WHAXON-AI-Forensics`
**Current source baseline:** `6fa1fa5f9bcff9b7afffb87ca908b0f78562fa3b`, reviewed 2026-11-02.
**Historical integration baseline:** `aea6a2ff859301192b3133330a94ecc0e6a21cbf`; default-route change `8313b8af885d4c4f5711c4df0998f0e8523f9b33`; test assertion change `aa8fcd2b633b267e577ee32034e330bfb7bc9c71`.
**Exact-baseline CI:** [#41488450899](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41488450899) passed all nine jobs. Python 3.11/3.12/3.13 each reported 1,408 passed, 14 skipped; browser tests are part of that matrix. The earlier approvals Refresh-queue failure on `e9b2f02` is historical, not the current red-CI state. This does not establish complete UI acceptance. No browser tests were rerun locally during this documentation review.

This is a dated implementation and acceptance audit, not a declaration that the UI is fully accepted or deployment-ready. The roadmap §38 remains the controlling release gate; visual regression, complete visible-control inventory, accessibility, CLI/web parity and external-asset deployment checks remain open until evidence is recorded.

## 1. Source-of-truth assets and preservation

The checked-in design package contained 32 HTML files and 32 PNG files at the inspected baseline, plus `obsidian_kinetic/DESIGN.md`. The HTML/PNG set includes distinct versioned alternatives and ten byte-identical loose copies. Counts therefore do not mean 32 accepted workflows. The [due-diligence register](DOCUMENTATION_RECONCILIATION.md) separates safe duplicate-removal candidates from distinct supplied designs requiring canonical mapping; the cleanup removes the ten exact loose copies while retaining named originals and distinct alternatives. The production implementation consists of 22 `ui_v2_*.html` templates and 22 corresponding web routes.

The new templates use the supplied Obsidian Kinetic visual system. The original `base.html`, `index.html`, `app.js`, `style.css`, and historical `docs/WEB_UI_INTERACTION_AUDIT.md` remain the deprecated interface/reference. They must not be redesigned, repurposed as the new UI, or overwritten as part of this work.

## 2. Entry points

| URL | Purpose | State |
|---|---|---|
| `/` | Default web entry point | Redirects to `/ui-v2`; exact-baseline CI above passed; future candidates need their own CI evidence |
| `/ui-v2` | Canonical Obsidian Kinetic dashboard | Implemented |
| `/ui-v2/dashboard` | Dashboard alias | Implemented |
| `/ui` | Previous web interface | Preserved compatibility/reference route; desktop `gui/embed.py` still points here |
| Desktop launcher | `gui/app.py` → `embed.URL` | Still opens `/ui`; migrate to accepted new default and test startup/navigation |

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

All 22 routes have a corresponding production template. The tracked baseline has 23 UI-v2 test modules; some related pages share the auxiliary-page module.

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
5. **Deployment dependencies:** the supplied pages load Tailwind, fonts/icons and images from external hosts. Decide and test whether the supported deployment requires network-independent bundled assets; do not silently claim air-gapped readiness while external runtime assets remain.
6. **Desktop/default entry points:** the web server redirects `/` to `/ui-v2`, but `src/whaxon/interfaces/gui/embed.py` still sets its URL to `/ui`. Correct the desktop entry point, test startup/navigation against the accepted supplied UI and preserve legacy design source unchanged. Web-route CI does not prove desktop parity.
7. **Exact candidate:** the inspected baseline is CI-green. Repeat required browser/E2E and acceptance checks for the final release candidate rather than relying on earlier commits.

## 7. Branch and PR reconciliation

At the time of this audit there were no open pull requests; the repository was checked again on 2026-11-02 and still had none open. The canonical UI integration PRs #37, #41 and #42, and the subsequent UI wiring/truthfulness PRs #43–#73, were already merged into `main`. The old full-wiring PR #16 was closed unmerged as a draft; its own description explicitly said not to merge because wiring and browser acceptance were incomplete. PRs #33–#36 were superseded by the later integrated UI work. Their old branch tips must not be blindly merged over newer main code.

No alternate UI or runtime implementation is created by this documentation refresh. Current branch comparison and retirement conditions are in the [due-diligence register](DOCUMENTATION_RECONCILIATION.md). Stale historical branches are not merge candidates merely because they still exist.

## 8. Release gate

Do not mark the new UI DONE or deployment-ready until the acceptance gaps above are closed, browser and visual regression checks pass on the candidate commit, security regressions pass, and the roadmap's §38 release checklist is updated with observed evidence.
