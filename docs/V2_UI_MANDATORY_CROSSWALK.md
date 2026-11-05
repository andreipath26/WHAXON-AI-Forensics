# WHAXON — UI V2 DESIGN, INTERACTION AND ACCEPTANCE MASTER

**Canonical UI design and acceptance reference, consolidated 2026-11-05.** Source, tests, screenshots and exact-head CI are required to establish implemented behavior. The design crosswalk determines planned UI scope; historical audits and templates are evidence, not production-ready declarations. Keep D1–D6 deployment gates open until demonstrated and approved. Do not infer that Dashboard approval implies Scope or Engine E6 approval.

## Part I — Canonical UI V2 contract and page crosswalk

# Mandatory WHAXON V2 UI crosswalk — all 22 pages

**Scope:** All V2 UI designs, production pages, shared navigation, client APIs, desktop entry points, tests and reviews. This is the **single canonical UI-wide crosswalk**, not a Dashboard-only plan.
**Authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md` P4/P5 and §38 G01–G10 (especially G06); `docs/ENGINEERING_EXECUTION_MODEL.md`; `docs/NEW_UI_INTERACTION_AUDIT.md`; `docs/UI_CONTROL_INVENTORY.md`; `docs/ENGINE_V2_E6_SERVICE_UI_HANDOFF_MATRIX.md`; `web ui files and rendering/obsidian_kinetic/DESIGN.md`.
**Freeze rule:** E6 engine integration remains frozen until the operator explicitly declares the new UI **deployment-ready**. Independent UI preparation/hardening does **not** authorize E6 restart or production deployment. Do not edit supplied design references or redesign canonical page variants.

## REQUIRED BEFORE EACH UI TASK (human or agent)

1. **Locate page in matrix below**; inspect its supplied named source/PNG, variant, production template, tests, static control inventory, server route and exact source HEAD. Resolve ambiguous variants with the design owner; never silently replace a supplied design.
2. **Propose a bounded change:** user-visible outcome; affected UI IDs/controls; ownership and dependencies; exact backend endpoints, authorization/scope/approval policy; loading, empty, unavailable, error, cancellation, reconnect and offline behavior.
3. **Verify honest state:** API 200 is not proof of success; queued is not completed; completed is not verified; do not synthesize findings, active sessions, PTES coverage, audit cryptography, live workers or UI permissions. Unsupported actions must be labelled and disabled/hidden safely.
4. **Keep one owner for a shared file.** Batch independent work using explicit interfaces and no conflicting concurrent writes, per the engineering execution model. No uncontrolled UI parallel rewrite.
5. **Write regression tests with the change:** source/binding checks, Playwright interactions (including negative/malformed responses), client authorization and same Core contracts where relevant; test desktop and mobile, focus/keyboard, assistive technology, dark appearance and no overflow.
6. **Record exact candidate evidence:** code SHA, test command, CI URL/outcomes/skips, approved visual PNG baseline comparison, accessibility/manual outcomes, network/font/icon policy and actual supported deployment environment. A test file or static inventory entry alone is not proof.
7. **Review/merge gate:** check all relevant rows of this crosswalk and roadmap G06/G07/G08; preserve incomplete states as OPEN and do not merge claimed ready status without evidence. The E6 freeze and G01–G10 remain independent.

## All 22 required page crosswalk rows

| ID | Page | Canonical route | Production template | Existing browser test coverage | Deployment acceptance |
|---|---|---|---|---|---|
| UI-01 | Dashboard | `/ui-v2` | `ui_v2_dashboard.html` | `test_web_ui_v2_dashboard.py` | OPEN |
| UI-02 | Scope & Targets | `/ui-v2/scope` | `ui_v2_scope.html` | `test_web_ui_v2_scope.py`, `test_web_ui_v2_scope_interactions.py` | OPEN |
| UI-03 | Run & Orchestration | `/ui-v2/run` | `ui_v2_run.html` | `test_web_ui_v2_run.py` | OPEN |
| UI-04 | Findings | `/ui-v2/findings` | `ui_v2_findings.html` | `test_web_ui_v2_findings.py` | OPEN |
| UI-05 | Report | `/ui-v2/report` | `ui_v2_report.html` | `test_web_ui_v2_report.py` | OPEN |
| UI-06 | Reports | `/ui-v2/reports` | `ui_v2_reports.html` | `test_web_ui_v2_reports.py` | OPEN |
| UI-07 | History | `/ui-v2/history` | `ui_v2_history.html` | `test_web_ui_v2_history.py` | OPEN |
| UI-08 | Diagnostics | `/ui-v2/diagnostics` | `ui_v2_diagnostics.html` | `test_web_ui_v2_diagnostics.py` | OPEN |
| UI-09 | Evidence | `/ui-v2/evidence` | `ui_v2_evidence.html` | `test_web_ui_v2_evidence.py` | OPEN |
| UI-10 | AI Gate | `/ui-v2/ai` | `ui_v2_ai.html` | `test_web_ui_v2_ai.py` | OPEN |
| UI-11 | Retest | `/ui-v2/retest` | `ui_v2_retest.html` | `test_web_ui_v2_retest.py` | OPEN |
| UI-12 | Chains | `/ui-v2/chains` | `ui_v2_chains.html` | `test_web_ui_v2_chains.py` | OPEN |
| UI-13 | Adapters | `/ui-v2/adapters` | `ui_v2_adapters.html` | `test_web_ui_v2_adapters.py` | OPEN |
| UI-14 | Settings | `/ui-v2/settings` | `ui_v2_settings.html` | `test_web_ui_v2_settings.py` | OPEN |
| UI-15 | Audit | `/ui-v2/audit` | `ui_v2_audit.html` | `test_web_ui_v2_audit.py` | OPEN |
| UI-16 | Monitoring | `/ui-v2/monitoring` | `ui_v2_monitoring.html` | `test_web_ui_v2_monitoring.py` | OPEN |
| UI-17 | BAS | `/ui-v2/bas` | `ui_v2_bas.html` | `test_web_ui_v2_auxiliary_pages.py`, `test_web_ui_v2_advanced_truthfulness.py` | OPEN |
| UI-18 | Bug Bounty | `/ui-v2/bug-bounty` | `ui_v2_bug_bounty.html` | `test_web_ui_v2_bug_bounty.py`, `test_web_ui_v2_auxiliary_pages.py` | OPEN |
| UI-19 | Compliance | `/ui-v2/compliance` | `ui_v2_compliance.html` | `test_web_ui_v2_auxiliary_pages.py`, `test_web_ui_v2_advanced_truthfulness.py` | OPEN |
| UI-20 | PTaaS | `/ui-v2/ptaas` | `ui_v2_ptaas.html` | `test_web_ui_v2_ptaas.py`, `test_web_ui_v2_auxiliary_pages.py` | OPEN |
| UI-21 | Threat Intel | `/ui-v2/threat-intel` | `ui_v2_threat_intel.html` | `test_web_ui_v2_auxiliary_pages.py`, `test_web_ui_v2_advanced_truthfulness.py` | OPEN |
| UI-22 | Approvals | `/ui-v2/approvals` | `ui_v2_approvals.html` | `test_web_ui_v2_auxiliary_pages.py`, `test_web_ui_v2_advanced_truthfulness.py` | OPEN |

All templates live under `src/whaxon/interfaces/web/templates/`; browser tests live under `tests/`. The dashboard alias `/ui-v2/dashboard` and root entry route `/` additionally require parity checks. Common tests: `test_web_ui_v2_route_matrix.py`, `test_web_ui_v2_navigation.py`, `test_web_ui_v2_control_inventory.py`; auxiliary pages share the listed suites. The inventory records **793 static controls**; script references do not establish live bindings.

## Acceptance criteria for EVERY row

| Gate | Required proof | Default |
|---|---|---|
| D1 Design | Exact approved supplied screen and variant; desktop/mobile screenshot comparisons and no accidental visual changes | OPEN |
| D2 Controls | Every visible enabled control reachable, named, authorized and mapped to a real action; disabled/hidden ones documented with rationale | OPEN |
| D3 Runtime truth | Live API data, empty/unavailable/error/unauthorized/blocked/race states and rollback truthful, no invented records | OPEN |
| D4 Security | Scope/approval/consent on server; CSRF/Origin, XSS and secret redaction; no UI-only policy | OPEN |
| D5 Accessibility | Keyboard-only navigation, focus return, semantic labels, contrast/non-color cues and assistive-tech manual review | OPEN |
| D6 Deployment | Supported browser/desktop and platform checks, external asset/offline policy, versioned exact-SHA CI and release reviewer | OPEN |

A page becomes `DEPLOYMENT_READY` **only when D1–D6 each have exact-source evidence and explicit approver sign-off**. No aggregate percentage or page route smoke closes any gate. UI readiness does **not** automatically approve E6 or full product deployment.

## Work queue and Dashboard-first checkpoint

**Priority UI-01 Dashboard:** current template `ui_v2_dashboard.html`, route `/ui-v2`, browser suite `test_web_ui_v2_dashboard.py`, and supplied `web ui files and rendering/dashboard_engagement_hub_zero_state/`. Existing live functionality includes history/filters/JSON export, scope routing, job halt, Burp XML import, health/readiness labels, mobile navigation. Known blocker: full approved screenshot and accessibility verification, complete per-control permission/malformed-response mapping, packaging/network asset policy.

Dashboard batch 1 hardens malformed-history export: a successful HTTP response with non-array payload must **fail visibly** rather than export a misleading empty archive; added browser regression. It does not alter visual design. **Dashboard remains NOT deployment-ready** until all D1–D6 complete.

**Next after Dashboard:** UI-02 Scope, UI-03 Run, UI-04 Findings, then evidence/report workflows and the remaining pages; order follows critical dependencies and is adjustable without skipping gates.

**Reviewer record template:** UI-ID, base/head SHA, approved PNG/design variant, affected control IDs, backend routes and policy, D1–D6 evidence links, expected/observed states, limitations, independent reviewer, explicit decision.

## Dashboard implementation checkpoint — 2026-11-05 (D1–D6)

The Dashboard is the **first** page in this UI-wide crosswalk, not a separate crosswalk. Work is in [UI PR #126](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/126). Implemented safety hardening now includes:

- Fail-closed malformed HTTP-success payloads for history export and import; null/invalid JSON shapes for history/jobs/report/tools/scope/status; boolean-only health, adapter and scope enforcement assertions.
- No candidate-to-verified promotion from a generic finding `status`; use only explicit `verification_status`.
- Invalid historical timestamps and negative findings counts remain unrecorded rather than being presented as real data.
- Partial cancel failures report requested counts conservatively; history filtering has a visible no-match state and retains backend-unavailable messages.
- No supplied design files modified; all changes in the production Dashboard template and existing browser test module.

| Gate | Latest assessment | Evidence still required to close |
|---|---|---|
| D1 Design | OPEN | Approver-approved comparison to `web ui files and rendering/dashboard_engagement_hub_zero_state/screen.png` at representative desktop/mobile viewports |
| D2 Controls | PARTIAL | Runtime inventory of every visible control with final expected action, loading/empty/error and authorization behavior, including generated elements |
| D3 Runtime truth | CANDIDATE | New negative-case Playwright assertions, exact-head CI success, cross-client integration and monitored supported staging |
| D4 Security | PARTIAL | Independent server-side authorization/CSRF review, malicious content escaping, permission-denied/timeout/cancel proofs |
| D5 Accessibility | PARTIAL | Keyboard/focus, high zoom, non-color cues, contrast and assistive-technology manual sign-off |
| D6 Deployment | OPEN | Exact candidate browser/desktop tests, packaged fonts/icons/CSS or explicitly approved connected-only asset policy and failover, target-environment rollout/rollback evidence |

**Decision:** Dashboard **NOT DEPLOYMENT-READY** until D1–D6 evidence and operator sign-off exist; E6 remains FROZEN. Do not equate a green CI run, static 35-control inventory, or this checkpoint with approval.

### Dashboard action safety update — 2026-11-05

- Emergency halt requests are single-flight within the dashboard session, to prevent duplicate submissions from repeated clicks. A malformed job identity is not sent to the cancellation endpoint; a partial cancel result remains an incomplete cancellation request, not proof of stopped effects.
- Error outcomes use an assertive accessibility alert role. Non-error informational updates use a status region. Added browser negative tests for invalid job IDs and alert signaling.
- Source changes are bounded to the production Dashboard template and browser tests; no design source was modified. **D1–D6 remain OPEN until evidence and sign-off are recorded**. Prior green CI is not exact-head acceptance.

### Dashboard crosswalk evidence — untrusted content and access denial

The Dashboard browser suite includes adversarial browser checks that scope and job-history text are not converted to executable markup, that all visible navigational links resolve to canonical UI routes, and that a 403 cancellation response never becomes a false stop-success claim. These are candidate proofs for D2–D4, not an independent security sign-off. Browser tests must pass for the exact candidate SHA, and deployment D1/D5/D6 remain unaccepted.

### Dashboard bundled styling milestone

The Dashboard now serves a build-time compiled, pinned Tailwind stylesheet from `/static/dashboard-v2.css`, with the build recipe `scripts/build_dashboard_css.cjs` and isolated branch-only vendor workflow. The runtime Tailwind CDN script is removed; its checked-in theme configuration remains non-executable for reproducible asset builds. Browser regression coverage blocks remote Tailwind and Google Fonts and verifies canonical background styling and live page operation using the bundled CSS. D6 **remains OPEN** because font/icon/image availability, final source-distribution install checks, approved network/offline support policy, target rollout and rollback, and operator acceptance require independent proof.

### Dashboard WCAG audit remediation
Automated axe-core WCAG 2 A/AA and 2.1 A/AA review on the integrated browser candidate found exactly one rule family failing at desktop and mobile: `document-title`. The production Dashboard now provides a descriptive HTML `<title>`, with a browser regression. The automated audit must be rerun on the exact post-fix SHA before its result is accepted. Automated success does not replace manual assistive-technology, contrast, zoom and keyboard review.

### Dashboard independently hosted static assets

The Dashboard production template no longer requests fonts, Material Symbols icons, logo, or avatar from Google hosts and no longer uses the runtime Tailwind CDN. The packaged local static assets include `dashboard-v2.css`, `dashboard-fonts.css`, 18 hashed font binaries, two supplied design images and license/source SHA-256 records. A browser regression blocks **all external HTTPS requests** and requires the Dashboard to function, render its canonical dark styling, and load both images using loopback-only static URLs. This addresses third-party page-view leakage and advances D6. Other supported environments, wheel/sdist inclusion, rollback, visual/manual accessibility and release approval remain independent requirements.

### Distribution packaging acceptance automation
The focused Dashboard workflow now builds both the `whaxon` wheel and source distribution, and invokes `scripts/check_dashboard_distribution.py`. The check requires the deployed template's CSS/fonts/images, fonts' license notices and manifest in **both** archives, and verifies SHA-256 for every bundled binary against the generated manifest. D6 packaging is accepted only once this exact-head step passes; supported-host deployment/rollback and explicit reviewer signoff remain separate.

### Parallel wheel-install and HTTP asset deployment lane
A second, independent GitHub Actions job builds the wheel+sdist, checks all packaged Dashboard resources/licenses against SHA-256 records, installs the built wheel into an isolated fresh virtual environment, starts `whaxon serve` on loopback and verifies live `/ui-v2` plus each local CSS/font/image URL via HTTP. It runs **in parallel** with visual, functional and automated WCAG browser checks. Full operator deployment authorization, actual host upgrade/rollback, manual screen-reader review and design signoff remain open.

### Exact-head CI reconciliation — 2026-11-05

At candidate `106c64f18e9762f4635043accee1338f513dd2f3`, [full CI run 42010899550](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42010899550) has now **completed SUCCESS**, including Python 3.11/3.12/3.13 test lanes and platform setup smoke. Python 3.11 and 3.13 source-distribution and clean-wheel smoke steps were **skipped**, while the Python 3.12 equivalents passed; do not count skips as passes. [Focused Dashboard run 42010899499](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42010899499) completed SUCCESS in both `dashboard` (browser, screenshot capture, automated axe) and `dashboard-install` (wheel/sdist manifest SHA and isolated loopback HTTP) jobs. These outcomes were verified against the exact PR head before this documentation update; **this documentation commit creates a new head requiring fresh exact-head CI**.

**Outstanding acceptance blockers (do not close D1–D6):** D1 requires owner-selected/approved supplied baseline and signed desktop/mobile visual comparisons; D2 requires a complete per-visible/generated-control, permission, state and service mapping with reviewer sign-off; D3 needs supported staging/cross-client operational acceptance; D4 requires independent server-side scope/consent/CSRF/XSS/secret review; D5 requires manual screen-reader, high-zoom, keyboard and contrast review; D6 requires actual target deployment, desktop and upgrade/rollback evidence plus explicit release approval. Automated axe success is not manual accessibility approval. No reviewer approvals are recorded on PR #126. E6 remains frozen, PR remains draft and unmerged.

## Operator freeze — Dashboard UI-01, 2026-11-05

**Status: MERGED AND FROZEN.** UI PR [#126](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/126) was squash-merged at main commit `c9dea5b40e5150a0fa02dbd313365af9edaaca7d`. The 22-page crosswalk remains the common authority and must continue to govern all other V2 pages. Dashboard-specific edits, asset rebuilds, test modifications, additional PRs and deployments are **suspended indefinitely**; the sole unfreeze trigger is the operator's explicit later instruction. An automated pull-request guard at `.github/workflows/dashboard-frozen.yml` rejects changes to the frozen file family. The hourly Dashboard-development automation is disabled to avoid reintroducing changes.

**This freeze is a source-control change hold, not production release authorization.** The merged candidate had green CI and automated browser/accessibility/distribution checks, but D1 owner visual sign-off, D2 per-control approval, D4 independent security review, D5 manual assistive-technology/zoom review, and D6 actual production target upgrade/rollback/operator sign-off were not fully evidenced. Keep those deployment gates **OPEN**, and do not describe Dashboard as production-approved based on merge or freeze alone. E6 remains independently frozen until the user explicitly declares the new UI deployment-ready.

**Enforcement limitation:** the guard fails violating PR checks, but only repository branch protection or rulesets requiring that check (plus restricting direct pushes/admin bypass) can prevent an authorized maintainer from merging or pushing anyway. The active GitHub integration cannot administer those settings. Until repository administrators enable such controls, this is a documented contributor prohibition plus an automated PR check, not an absolute technical lock.


---

## Part 2 — docs/NEW_UI_INTERACTION_AUDIT.md (source record)

# New Default Web UI — Interaction and Acceptance Audit

> **Integration update — 2026-11-02, supersedes affected baseline statements below:** Four one-shot CLI commands now use `initialize(drain=False)` with regression coverage. Desktop startup targets `/ui-v2`. Test catalog consumers use the packaged seed; the duplicate tracked root catalog and unused qasync requirement/manifest entry are removed, while operator catalogs and protected legacy designs remain preserved. See [UI control inventory](./V2_UI_MANDATORY_CROSSWALK.md) for 793 source controls across 22 templates; static coverage does not establish complete runtime wiring, visual fidelity, accessibility or service parity. Local browser execution is blocked by unavailable Chromium downloads. The earlier CI/source records below describe their stated baseline, not acceptance of this integration.


**Authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, P4 and §38 G06; the previous section references are reconciled in its §50.

**Repository:** `andreipath26/WHAXON-AI-Forensics`
**Current source baseline:** `6fa1fa5f9bcff9b7afffb87ca908b0f78562fa3b`, reviewed 2026-11-02.
**Historical integration baseline:** `aea6a2ff859301192b3133330a94ecc0e6a21cbf`; default-route change `8313b8af885d4c4f5711c4df0998f0e8523f9b33`; test assertion change `aa8fcd2b633b267e577ee32034e330bfb7bc9c71`.
**Exact-baseline CI:** [#41488450899](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41488450899) passed all nine jobs. Python 3.11/3.12/3.13 each reported 1,408 passed, 14 skipped; browser tests are part of that matrix. The earlier approvals Refresh-queue failure on `e9b2f02` is historical, not the current red-CI state. This does not establish complete UI acceptance. No browser tests were rerun locally during this documentation review.

This is a dated implementation and acceptance audit, not a declaration that the UI is fully accepted or deployment-ready. The roadmap §38 remains the controlling release gate; visual regression, complete visible-control inventory, accessibility, CLI/web parity and external-asset deployment checks remain open until evidence is recorded.

## 1. Source-of-truth assets and preservation

The checked-in design package contained 32 HTML files and 32 PNG files at the inspected baseline, plus `obsidian_kinetic/DESIGN.md`. The HTML/PNG set includes distinct versioned alternatives and ten byte-identical loose copies. Counts therefore do not mean 32 accepted workflows. The [due-diligence register](PROJECT_GOVERNANCE_MASTER.md) separates safe duplicate-removal candidates from distinct supplied designs requiring canonical mapping; the cleanup removes the ten exact loose copies while retaining named originals and distinct alternatives. The production implementation consists of 22 `ui_v2_*.html` templates and 22 corresponding web routes.

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

No alternate UI or runtime implementation is created by this documentation refresh. Current branch comparison and retirement conditions are in the [due-diligence register](PROJECT_GOVERNANCE_MASTER.md). Stale historical branches are not merge candidates merely because they still exist.

## 8. Release gate

Do not mark the new UI DONE or deployment-ready until the acceptance gaps above are closed, browser and visual regression checks pass on the candidate commit, security regressions pass, and the roadmap's §38 release checklist is updated with observed evidence.


---

## Part 3 — docs/WEB_UI_INTERACTION_AUDIT.md (source record)

> **Historical audit — superseded (2026-11-02).** This file records an earlier UI generation and must not be used to assess the current Obsidian Kinetic UI. Its page inventory, PASS/WIRED/MOCKUP labels, endpoint wiring and test counts are historical. Use [NEW_UI_INTERACTION_AUDIT.md](./V2_UI_MANDATORY_CROSSWALK.md) for the current 22-route implementation/acceptance record and master roadmap §38 for release acceptance. This historical file is retained for traceability only.

# WHAXON Web UI Interaction Audit

## Status legend
- **PASS** — wired, verified in a browser, has a passing test
- **WIRED** — wired to a real backend, not yet verified in a browser
- **MOCKUP** — hardcoded data, no backend
- **HIDDEN** — mockup, sidebar item hidden until backend exists
- **BLOCKED** — no backend exists, cannot be wired in this session

## Findings page
| ID | Element | Expected | Actual | Backend | Status |
|---|---|---|---|---|---|
| F.01 | Findings table load | Fetch /api/report, render rows | Works | GET /api/report | PASS |
| F.02 | Row click | Open slide-over | Works | none | PASS |
| F.03 | Validate button | POST /api/validate | Wired | POST /api/validate/<job>/<seq> | WIRED |
| F.04 | Retest button | POST /api/retest | Wired | POST /api/retest/<job>/<seq> | WIRED |
| F.05 | Sort headers | Reorder table | Works | none | PASS |
| F.06 | Density toggle | Change row density | Works | none | PASS |
| F.07 | Bulk mark verified | Bulk verification | Hidden | none | HIDDEN |
| F.08 | Bulk delete | Bulk delete | Hidden | none | HIDDEN |
| F.09 | AI banner | Dismiss/approve proposal | Hidden | none | HIDDEN |

## Run page
| R.01 | Catalog load | Fetch /api/tools | Works | GET /api/tools | PASS |
| R.02 | Run button | POST /api/run | Works | POST /api/run | PASS |
| R.03 | Cancel button | POST cancel | Works | POST /api/jobs/<id>/cancel | PASS |
| R.04 | SSE stream | Live output | Works | GET /api/jobs/<id>/stream | PASS |

## Scope page
| S.01 | Scope list | Fetch /api/scope | Works | GET /api/scope | PASS |
| S.02 | Check scope | POST /api/scope/check | Works | POST /api/scope/check | PASS |
| S.03 | Import button | Import scope JSON | Hidden | none | HIDDEN |
| S.04 | + Add rule | Add scope rule | Hidden | none | HIDDEN |
| S.05 | Run anyway (modal) | POST /api/scope/override | Logs override | POST /api/scope/override | WIRED |

## Report page
| P.01 | Generate Markdown | Download md report | Downloads | GET /api/report?format=md | WIRED |
| P.02 | Generate HTML | Download html report | Downloads | GET /api/report?format=html | WIRED |
| P.03 | Generate PDF | Download pdf report | Downloads | GET /api/report?format=pdf | WIRED |
| P.04 | Recent reports table | List generated | Hardcoded | none | MOCKUP |
| P.05 | Known Vulns preview | Show CVE table | Hardcoded | none | MOCKUP |

## Retest page
| T.01 | Queue table | Show verified findings | Live queue | GET /api/report | WIRED |
| T.02 | Retest button (row) | POST /api/retest | Wired | POST /api/retest/<job>/<seq> | WIRED |

## Sessions page
| X.01 | Sessions list | Fetch /api/msf/sessions | Live list | GET /api/msf/sessions | WIRED |
| X.02 | Interact button | Open session | No handler | none | MOCKUP |

## Attack Surface page
| A.01 | Graph render | Fetch /api/pivot/graph | Hardcoded SVG | GET /api/pivot/graph | MOCKUP |

## Catalog page
| C.01 | Tool list | Fetch /api/tools | Live list | GET /api/tools | WIRED |
| C.02 | Adapter column | Derive from adapters | Hardcoded | none | MOCKUP |

## Threat Intel page
| I.01 | Search button | Run cve or lookup | No handler | none | MOCKUP |
| I.02 | CVE result card | Show CVE data | Hardcoded | none | MOCKUP |

## Compliance page
| M.01 | Framework progress | Real compliance mapping | Hardcoded | none | HIDDEN |

## Settings page
| G.01 | Theme selector | Persist theme | No handler | none | MOCKUP |
| G.02 | Members list | Show real users | Hardcoded | none | HIDDEN |

## Components page
| D.01 | Design system demo | Not user-facing | Static | none | HIDDEN |

## Cross-cutting
| B.01 | Notifications | Read notification list | No handler | none | MOCKUP |
| B.02 | Workspace switcher | Change workspace | No handler | none | MOCKUP |
| B.03 | Command palette | Search + actions | Mock actions stripped | none | HIDDEN |
| B.04 | Help / shortcuts | Show kbd legend | Works | none | PASS |
| B.05 | Sidebar collapse | Toggle | Works | none | PASS |

## Pass 1 targets (this session)
- P.01, P.02, P.03 → wire to /api/report downloads
- T.01, T.02 → replace with real retest queue
- X.01 → wire to /api/msf/sessions
- C.01 → wire to /api/tools
- S.05 → wire to /api/scope/override
- F.09 → hide AI banner (no backend)
- F.07, F.08 → hide bulk bar buttons (no backend)
- B.03 → strip palette mock actions, keep search

## Pass 2 targets (next session)
- A.01 → wire to /api/pivot/graph
- I.01, I.02 → add CVE/lookup web routes, wire search

## Pass 3 targets
- M.01, G.01, G.02, D.01, B.01, B.02, S.03, S.04, P.04, P.05 → hide or mark "coming soon"


---

## Part 4 — docs/UI_CONTROL_INVENTORY.md (source record)

# Supplied UI control inventory

**Source baseline:** `7ae5aa1` plus the current integration batch. Generated from all 22 production `ui_v2_*.html` templates using the stdlib HTML parser in `tests/test_web_ui_v2_control_inventory.py`. Regenerate after template changes. No supplied design was changed.

## Evidence boundary

This is a complete **static source-control registry**, not a declaration that every control is live or accepted. It covers anchors, buttons, inputs, selects, textareas, summaries explicit button/link roles, inline event handlers, focusable tabindex and editable elements, including initially hidden controls. IDs are template plus one-based line:column; minified shell markup can share a line. Controls dynamically created by JavaScript, computed CSS visibility, event delegation and backend permissions require runtime inspection.

`source-hidden` includes an explicit hidden ancestor/class/style and can be responsive; `disabled` is declared disabled; `declared-nav` has a canonical href; `inline-handler` declares JavaScript; `script-reference` only means an ID/data-path occurs in an inline script, **not** that an event handler or backend works; `unresolved-static` means no binding was established by this conservative inspection. Unresolved controls are review items, not automatically dead controls. Every source row retains its binding evidence for follow-up.

## Acceptance still open

- The cross-page browser contract checks all 22 rendered destinations and rejects visible placeholder/unknown sidebar links after page scripts run. Page-specific tests remain the behavioral evidence for other controls.
- Complete runtime action/service/authorization mapping for every visible control, including loading/error/cancellation/reconnect states and generated controls.
- Visual comparison against approved supplied reference choices; no screenshot baselines were fabricated or auto-approved.
- Keyboard/focus/screen-reader/non-color/manual accessibility acceptance. Static labels and ordinary Playwright clicks do not close it.
- Full CLI/API/UI operation parity and deliberate-difference register, plus deployment tests for external fonts/Tailwind/icons/images.

## Page summary

| Template | Controls | Source-hidden | Disabled | Declared nav | Inline handler | Script reference | Unresolved static |
|---|---:|---:|---:|---:|---:|---:|---:|
| ui_v2_adapters.html | 48 | 0 | 1 | 0 | 0 | 21 | 26 |
| ui_v2_ai.html | 21 | 0 | 0 | 0 | 0 | 16 | 5 |
| ui_v2_approvals.html | 37 | 9 | 0 | 0 | 10 | 4 | 14 |
| ui_v2_audit.html | 43 | 0 | 0 | 0 | 13 | 17 | 13 |
| ui_v2_bas.html | 32 | 0 | 0 | 0 | 0 | 20 | 12 |
| ui_v2_bug_bounty.html | 32 | 0 | 0 | 0 | 0 | 16 | 16 |
| ui_v2_chains.html | 25 | 0 | 0 | 0 | 0 | 15 | 10 |
| ui_v2_compliance.html | 40 | 0 | 0 | 0 | 0 | 20 | 20 |
| ui_v2_dashboard.html | 35 | 2 | 0 | 0 | 0 | 21 | 12 |
| ui_v2_diagnostics.html | 33 | 0 | 0 | 0 | 12 | 17 | 4 |
| ui_v2_evidence.html | 35 | 0 | 0 | 0 | 0 | 14 | 21 |
| ui_v2_findings.html | 25 | 0 | 0 | 1 | 4 | 7 | 13 |
| ui_v2_history.html | 31 | 0 | 3 | 0 | 0 | 16 | 12 |
| ui_v2_monitoring.html | 45 | 0 | 0 | 0 | 0 | 19 | 26 |
| ui_v2_ptaas.html | 42 | 5 | 0 | 0 | 11 | 17 | 9 |
| ui_v2_report.html | 22 | 1 | 0 | 1 | 0 | 5 | 15 |
| ui_v2_reports.html | 21 | 1 | 0 | 0 | 0 | 5 | 15 |
| ui_v2_retest.html | 36 | 0 | 0 | 0 | 0 | 14 | 22 |
| ui_v2_run.html | 37 | 0 | 0 | 1 | 7 | 9 | 20 |
| ui_v2_scope.html | 39 | 25 | 1 | 1 | 0 | 10 | 2 |
| ui_v2_settings.html | 61 | 15 | 0 | 0 | 12 | 15 | 19 |
| ui_v2_threat_intel.html | 53 | 0 | 0 | 0 | 13 | 20 | 20 |

**Total:** 793 source controls across 22 templates.

## Exact source registry

Labels and binding excerpts are shortened for readability; line:column identifies the complete source. No truncation changes the count or classification.

### ui_v2_adapters.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 7:4579 | a | Dashboard / Zero State | script-reference | # |
| 7:4836 | a | Scope & Targets | script-reference | # |
| 7:5087 | a | Run & Orchestration | script-reference | # |
| 7:5346 | a | Trust Layer & Findings | script-reference | # |
| 7:5611 | a | PTES Coverage & Reports | script-reference | # |
| 7:6086 | a | AI Strategy Gate | script-reference | # |
| 7:6333 | a | Remediation Retest Studio | script-reference | # |
| 7:6598 | a | Correlated Attack Chains | script-reference | # |
| 7:7061 | a | Job Execution History | script-reference | # |
| 7:7317 | a | Evidence File Inspector | script-reference | # |
| 7:7578 | a | Cryptographic Audit Log | unresolved-static | # |
| 7:8041 | a | System Diagnostics & Health | script-reference | # |
| 7:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 7:8585 | a | Settings & API Explorer | unresolved-static | # |
| 7:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 7:11306 | button | add New | unresolved-static | — |
| 7:13011 | button | terminal Terminal Log | unresolved-static | — |
| 7:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 18:1 | button | sync Sync whaxon.adapters | script-reference | btn-sync |
| 22:1 | button | restart_alt Reload Entry Points | script-reference | btn-reload |
| 26:1 | button | add_circle + Register New Adapter | script-reference | btn-register |
| 116:1 | input | Search adapters by tool name, entrypoint, author, tags... | script-reference | adapter-search |
| 121:1 | button | All (14) | unresolved-static | — |
| 124:1 | button | Recon (5) | unresolved-static | — |
| 127:1 | button | Vulnerability (4) | unresolved-static | — |
| 130:1 | button | Exploitation (3) | unresolved-static | — |
| 133:1 | button | Ingestion (2) | unresolved-static | — |
| 140:1 | select | All States Binary Found (12) Missing Binary (2) Untrusted (0) | script-reference | status-select |
| 188:1 | button | CONFIGURE tune | unresolved-static | — |
| 232:1 | button | CONFIGURE tune | unresolved-static | — |
| 276:1 | button | CONFIGURE tune | unresolved-static | — |
| 320:1 | button | CONFIGURE tune | unresolved-static | — |
| 363:1 | button | CONFIGURE tune | unresolved-static | — |
| 407:1 | button | CONFIGURE CONNECTION settings | unresolved-static | — |
| 451:1 | button | CONFIGURE tune | unresolved-static | — |
| 495:1 | button | CONFIGURE tune | unresolved-static | — |
| 545:1 | button | Close Panel | script-reference | close-drawer |
| 583:1 | button | Remove flag | unresolved-static | — |
| 587:1 | button | Remove flag | unresolved-static | — |
| 591:1 | button | Remove flag | unresolved-static | — |
| 595:1 | button | Remove flag | unresolved-static | — |
| 597:1 | input | + Add CLI parameter... | unresolved-static | add-flag-input |
| 631:1 | input | (unnamed) | unresolved-static | — |
| 638:1 | input | (unnamed) | disabled | — |
| 645:1 | input | (unnamed) | unresolved-static | — |
| 661:1 | button | play_arrow Test Adapter Execution with Mock Output | script-reference | btn-mock-test |
| 666:1 | button | Re-sign Manifest | script-reference | btn-resign |
| 669:1 | button | Save Configuration | script-reference | btn-save-conf |

### ui_v2_ai.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4579 | a | Dashboard / Zero State | script-reference | # |
| 4:4836 | a | Scope & Targets | script-reference | # |
| 4:5087 | a | Run & Orchestration | script-reference | # |
| 4:5346 | a | Trust Layer & Findings | script-reference | # |
| 4:5611 | a | PTES Coverage & Reports | script-reference | # |
| 4:6086 | a | AI Strategy Gate | script-reference | # |
| 4:6332 | a | Remediation Retest Studio | script-reference | # |
| 4:6597 | a | Correlated Attack Chains | script-reference | # |
| 4:7060 | a | Job Execution History | script-reference | # |
| 4:7317 | a | Evidence File Inspector | script-reference | # |
| 4:7578 | a | Cryptographic Audit Log | script-reference | # |
| 4:8041 | a | System Diagnostics & Health | script-reference | # |
| 4:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 4:8585 | a | Settings & API Explorer | script-reference | # |
| 4:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:11306 | button | add New | unresolved-static | — |
| 4:13011 | button | terminal Terminal Log | unresolved-static | — |
| 4:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 84:1 | button | close Reject & Re-plan [Esc] | script-reference | btn-reject |
| 91:1 | button | bolt Authorize & Execute [Enter] | script-reference | btn-authorize |
| 258:1 | button | content_copy Copy | unresolved-static | — |

### ui_v2_approvals.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | target Scope & Targets | script-reference | # |
| 4:4807 | a | terminal Run & Orchestration | script-reference | # |
| 4:5149 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5502 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9037 | button | terminal Terminal Log | unresolved-static | — |
| 4:9376 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 30:1 | button | replay Retest Verified Scope | inline-handler | runRetestAll() |
| 126:1 | button | ALL | unresolved-static | — |
| 127:1 | button | CRIT (1) | unresolved-static | — |
| 128:1 | button | HIGH (2) | unresolved-static | — |
| 129:1 | button | MED (1) | unresolved-static | — |
| 130:1 | button | LOW (0) | unresolved-static | — |
| 135:1 | button | VERIFIED (6) | unresolved-static | — |
| 136:1 | button | CANDIDATE (11) | unresolved-static | — |
| 137:1 | button | REVIEW NEEDED | unresolved-static | — |
| 142:1 | button | Nuclei | unresolved-static | — |
| 143:1 | button | sqlmap | unresolved-static | — |
| 144:1 | button | Nikto | unresolved-static | — |
| 149:1 | input | Filter proof pattern, URL, CVE... | unresolved-static | — |
| 164:1 | div | CRITICAL SQLi: Time-based Blind VERIFIED /api/v1/catalog/items?id= C | inline-handler | selectFinding(1) |
| 191:1 | div | HIGH Stored Cross-Site Scripting (XSS) VERIFIED /v1/reviews/post (co | inline-handler | selectFinding(2) |
| 218:1 | div | HIGH BOLA Authorization Bypass CANDIDATE /api/v2/tenant/billing (ten | inline-handler | selectFinding(3) |
| 245:1 | div | MEDIUM Exposed .env Backup Secret File VERIFIED /backup/.env.product | inline-handler | selectFinding(4) |
| 332:1 | button | content_copy Copy Command | inline-handler | copyProofCurl() |
| 407:1 | button | play_arrow Replay Test (Retest) | inline-handler | triggerReplayAction() |
| 411:1 | button | check Mark Fixed | inline-handler | markFixedAction() |
| 417:1 | button | file_export Export Proof to Issue Tracker | inline-handler | exportProofAction() |
| 421:1 | button | how_to_reg Send to Approvals | inline-handler | sendToApprovalsAction() |
| 521:1518 | button | close | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:600 | input | (unnamed) | source-hidden | — |
| 529:1089 | input | (unnamed) | source-hidden | — |
| 529:1561 | input | (unnamed) | source-hidden | — |
| 529:2020 | textarea | Cross-tenant billing data was exposed in JSON response payload despi | source-hidden | — |
| 529:2759 | button | redo Skip Item | source-hidden | — |
| 529:3032 | button | Refute / False Positive | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:3289 | button | Hold for Retest | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:3573 | button | how_to_reg Approve as Verified (Sign Proof) | source-hidden | document.getElementById('approvals-modal').remove() |

### ui_v2_audit.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4579 | a | Dashboard / Zero State | script-reference | # |
| 4:4836 | a | Scope & Targets | script-reference | # |
| 4:5087 | a | Run & Orchestration | script-reference | # |
| 4:5346 | a | Trust Layer & Findings | script-reference | # |
| 4:5611 | a | PTES Coverage & Reports | script-reference | # |
| 4:6086 | a | AI Strategy Gate | script-reference | # |
| 4:6333 | a | Remediation Retest Studio | script-reference | # |
| 4:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 4:6895 | a | Correlated Attack Chains | script-reference | # |
| 4:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 4:7443 | a | PTaaS Client Portal | script-reference | # |
| 4:7896 | a | Job Execution History | script-reference | # |
| 4:8153 | a | Evidence File Inspector | script-reference | # |
| 4:8414 | a | Cryptographic Audit Log | script-reference | # |
| 4:8876 | a | System Diagnostics & Health | script-reference | # |
| 4:9151 | a | Adapter & Plugin Manager | script-reference | # |
| 4:9420 | a | Settings & Secrets Vault | script-reference | # |
| 4:11786 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:12143 | button | add New | unresolved-static | — |
| 4:13848 | button | terminal Terminal Log | unresolved-static | — |
| 4:14187 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 38:1 | button | sync Verify Entire Merkle Root | inline-handler | triggerMerkleVerification() |
| 42:1 | button | enhanced_encryption Export Attestation (.sig) | inline-handler | downloadSigAttestation() |
| 157:1 | input | Search seq #, actor ID, SHA-256 digest, or payload target... | inline-handler | ledger-search |
| 162:1 | select | ALL SIGNALS (6) SCOPE MODIFICATION FINDING VERIFICATION PAYLOAD DETO | inline-handler | category-filter |
| 171:1 | button | shield SEALED ONLY | unresolved-static | — |
| 178:1 | button | chevron_left | unresolved-static | — |
| 181:1 | button | chevron_right | unresolved-static | — |
| 203:1 | tr | 2026-03-30T14:22:08.892401Z #EVT-9941 Finding Verified person OP//77 | inline-handler | selectEvent('EVT-9941') |
| 235:1 | button | Inspect Hash Tree | unresolved-static | — |
| 241:1 | tr | 2026-03-30T14:18:41.119830Z #EVT-9940 Scope Change key OP//4108-BRAV | inline-handler | selectEvent('EVT-9940') |
| 273:1 | button | Inspect Hash Tree | unresolved-static | — |
| 279:1 | tr | 2026-03-30T14:05:12.601944Z #EVT-9939 Payload Detonation memory AUTO | inline-handler | selectEvent('EVT-9939') |
| 311:1 | button | Inspect Hash Tree | unresolved-static | — |
| 317:1 | tr | 2026-03-30T13:42:01.002195Z #EVT-9938 Emergency Halt gavel OP//7749- | inline-handler | selectEvent('EVT-9938') |
| 349:1 | button | Inspect Hash Tree | unresolved-static | — |
| 355:1 | tr | 2026-03-30T13:15:55.441920Z #EVT-9937 Tool Invocation terminal DAEMO | inline-handler | selectEvent('EVT-9937') |
| 386:1 | button | Inspect Hash Tree | unresolved-static | — |
| 392:1 | tr | 2026-03-30T12:59:10.104510Z #EVT-9936 Policy Override verified_user  | inline-handler | selectEvent('EVT-9936') |
| 423:1 | button | Inspect Hash Tree | unresolved-static | — |
| 446:1 | button | content_copy Copy Raw Hex | inline-handler | copyRawProof() |
| 561:1 | button | gavel Court-Ready Forensic Bundle (.zip) | inline-handler | downloadCourtReadyPackage() |
| 565:1 | button | Cryptographic QR Verification Slip | inline-handler | generateQrCert() |

### ui_v2_bas.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 5:6895 | a | Correlated Attack Chains | script-reference | # |
| 5:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 5:7443 | a | Threat Intel & Exploit Arsenal | script-reference | # |
| 5:7724 | a | BAS & Detection Validation | script-reference | # |
| 5:8209 | a | Job Execution History | script-reference | # |
| 5:8466 | a | Evidence File Inspector | script-reference | # |
| 5:8727 | a | Cryptographic Audit Log | script-reference | # |
| 5:8988 | a | Compliance & Framework Crosswalk | script-reference | # |
| 5:9473 | a | System Diagnostics & Health | script-reference | # |
| 5:9748 | a | Adapter & Plugin Manager | script-reference | # |
| 5:10017 | a | PTaaS Client Portal | script-reference | # |
| 5:10270 | a | Settings & Secrets Vault | script-reference | # |
| 5:12636 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:12993 | button | add New | unresolved-static | — |
| 5:14698 | button | terminal Terminal Log | unresolved-static | — |
| 5:15037 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 40:1 | button | play_circle Detonate Sequence | unresolved-static | — |
| 44:1 | button | chevron_forward Query Blue Telemetry | unresolved-static | — |
| 48:1 | button | assessment Gap Report | unresolved-static | — |
| 443:1 | button | tune Configure Vector Filters | unresolved-static | — |
| 495:1 | button | Push Rule to SIEM | unresolved-static | — |
| 573:1 | button | download Export Validation Matrix (Navigator JSON + PDF) | unresolved-static | — |
| 601:1 | button | rocket_launch Deploy to Sentinel | unresolved-static | — |
| 628:1 | button | publish Deploy to Splunk | unresolved-static | — |

### ui_v2_bug_bounty.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 206:1124 | a | terminal Dashboard / Zero State | script-reference | # |
| 206:1479 | a | radar Scope & Targets | script-reference | # |
| 206:1821 | a | play_circle Run & Orchestration | script-reference | # |
| 206:2177 | a | verified_user Trust Layer & Findings | script-reference | # |
| 206:2541 | a | description PTES Coverage & Reports | script-reference | # |
| 206:3082 | a | psychology AI Strategy Gate | script-reference | # |
| 206:3429 | a | build_circle Remediation Retest Studio | script-reference | # |
| 206:3796 | a | account_tree Correlated Attack Chains | script-reference | # |
| 206:4161 | a | open_in_browser Bug Bounty & Live Browser | script-reference | # |
| 206:4702 | a | history_toggle_off Job Execution History | script-reference | # |
| 206:5067 | a | folder_zip Evidence File Inspector | script-reference | # |
| 206:5428 | a | encrypted Cryptographic Audit Log | script-reference | # |
| 206:5957 | a | monitor_heart System Diagnostics & Health | script-reference | # |
| 206:6331 | a | extension Adapter & Plugin Manager | script-reference | # |
| 206:6695 | a | shield_person PTaaS Client Portal | script-reference | # |
| 206:7051 | a | key Settings & Secrets Vault | script-reference | # |
| 206:8931 | button | terminal LOGS | unresolved-static | — |
| 206:9234 | button | dangerous HALT SCAN | unresolved-static | — |
| 305:1 | button | Go back | unresolved-static | — |
| 306:1 | button | Go forward | unresolved-static | — |
| 307:1 | button | Reload target view | unresolved-static | — |
| 313:1 | input | (unnamed) | unresolved-static | — |
| 320:1 | select | User_A (Attacker Context) User_B (Victim / Target #092) Unauthentica | unresolved-static | — |
| 384:1 | input | (unnamed) | unresolved-static | — |
| 389:1 | input | (unnamed) | unresolved-static | — |
| 414:1 | button | send EXECUTE COMMIT (TAMPERED) | unresolved-static | — |
| 439:1 | button | CLEAR CACHE | unresolved-static | — |
| 440:1 | button | DUMP DOM SNAPSHOT | unresolved-static | — |
| 555:1 | button | terminal INSPECTOR: POST /app/transfer/commit | unresolved-static | — |
| 595:1 | button | cached SEND TO VALIDATOR | unresolved-static | — |
| 599:1 | button | difference DIFF ANALYSIS | unresolved-static | — |
| 603:1 | button | verified_user PROMOTE TO FINDING | unresolved-static | — |

### ui_v2_chains.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Correlated Attack Chains | script-reference | # |
| 5:7061 | a | Job Execution History | script-reference | # |
| 5:7318 | a | Evidence File Inspector | script-reference | # |
| 5:7579 | a | Cryptographic Audit Log | script-reference | # |
| 5:8042 | a | System Diagnostics & Health | script-reference | # |
| 5:8317 | a | Adapter & Plugin Manager | script-reference | # |
| 5:8586 | a | Settings & API Explorer | script-reference | # |
| 5:10950 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:11307 | button | add New | unresolved-static | — |
| 5:13012 | button | terminal Terminal Log | unresolved-static | — |
| 5:13351 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 29:1 | button | sync_saved_locally Re-compute Graph | script-reference | btn-recompute |
| 35:1 | select | Severity: All Vectors Severity: Critical & Compound 10.0 Severity: H | unresolved-static | — |
| 41:1 | button | download Export Graph SVG/JSON | unresolved-static | — |
| 338:1 | button | play_arrow Simulate Controlled Replay | unresolved-static | — |
| 342:1 | button | menu_book Export PTES Chapter | unresolved-static | — |
| 429:1 | button | Add Custom Mitigation Rule (Envoy WAF) | unresolved-static | — |
| 432:1 | button | Generate Red Team Retest Script | unresolved-static | — |

### ui_v2_compliance.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 5:6895 | a | Correlated Attack Chains | script-reference | # |
| 5:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 5:7443 | a | Threat Intel & Exploit Arsenal | script-reference | # |
| 5:7724 | a | BAS & Detection Validation | script-reference | # |
| 5:8209 | a | Job Execution History | script-reference | # |
| 5:8466 | a | Evidence File Inspector | script-reference | # |
| 5:8727 | a | Cryptographic Audit Log | script-reference | # |
| 5:8988 | a | Compliance & Framework Crosswalk | script-reference | # |
| 5:9473 | a | System Diagnostics & Health | script-reference | # |
| 5:9748 | a | Adapter & Plugin Manager | script-reference | # |
| 5:10017 | a | PTaaS Client Portal | script-reference | # |
| 5:10270 | a | Settings & Secrets Vault | script-reference | # |
| 5:12636 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:12993 | button | add New | unresolved-static | — |
| 5:14698 | button | terminal Terminal Log | unresolved-static | — |
| 5:15037 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 22:1 | button | tune Configure Scope | unresolved-static | — |
| 26:1 | button | picture_as_pdf Auditor Crosswalk PDF | unresolved-static | — |
| 30:1 | button | archive Export Package (.ZIP) | unresolved-static | — |
| 201:1 | button | PCI-DSS v4.0 (5) | unresolved-static | — |
| 204:1 | button | OWASP Top 10 (4) | unresolved-static | — |
| 207:1 | button | SOC 2 Type II (8) | unresolved-static | — |
| 210:1 | button | ISO 27001 (6) | unresolved-static | — |
| 213:1 | button | NIST CSF (3) | unresolved-static | — |
| 216:1 | button | MITRE ATT&CK | unresolved-static | — |
| 423:1 | button | PREV | unresolved-static | — |
| 425:1 | button | NEXT | unresolved-static | — |
| 479:1 | input | (unnamed) | unresolved-static | — |
| 486:1 | input | (unnamed) | unresolved-static | — |
| 493:1 | input | (unnamed) | unresolved-static | — |
| 500:1 | input | (unnamed) | unresolved-static | — |
| 522:1 | button | lock_clock Compile Signed Matrix (.PDF / .JSON) | unresolved-static | — |

### ui_v2_dashboard.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 17:4342 | a | Dashboard / Zero State | script-reference | # |
| 17:4598 | a | Scope & Targets | script-reference | # |
| 17:4849 | a | Run & Orchestration | script-reference | # |
| 17:5108 | a | Trust Layer & Findings | script-reference | # |
| 17:5373 | a | PTES Coverage & Reports | script-reference | # |
| 17:5848 | a | AI Strategy Gate | script-reference | # |
| 17:6095 | a | Remediation Retest Studio | script-reference | # |
| 17:6360 | a | Correlated Attack Chains | script-reference | # |
| 17:6823 | a | Job Execution History | script-reference | # |
| 17:7080 | a | Evidence File Inspector | script-reference | # |
| 17:7341 | a | Cryptographic Audit Log | script-reference | # |
| 17:7804 | a | System Diagnostics & Health | script-reference | # |
| 17:8079 | a | Adapter & Plugin Manager | script-reference | # |
| 17:8348 | a | Settings & API Explorer | script-reference | # |
| 17:8813 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 17:9110 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 17:9395 | a | PTaaS Client Portal | script-reference | # |
| 17:9648 | a | Threat Intelligence | script-reference | # |
| 17:9914 | a | BAS & Detection Validation | script-reference | # |
| 17:10187 | a | Compliance & Framework Crosswalk | script-reference | # |
| 17:10472 | a | Trust Layer Approvals Queue | script-reference | # |
| 17:12865 | button | No active engagement (No target selected) arrow_drop_down | unresolved-static | — |
| 17:13230 | button | add New | unresolved-static | — |
| 17:14943 | button | terminal Terminal Log | unresolved-static | — |
| 17:15282 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 39:1 | button | terminal CLI Help | unresolved-static | — |
| 43:1 | button | vpn_key Update Credentials Now | unresolved-static | — |
| 84:1 | button | history Switch Target Session | unresolved-static | — |
| 88:1 | button | rocket_launch Start New Engagement | unresolved-static | — |
| 199:1 | button | Open Scope Setup arrow_forward | source-hidden | — |
| 238:1 | button | upload Upload Artifact | unresolved-static | — |
| 279:1 | button | play_arrow Deploy Mock | unresolved-static | — |
| 304:1 | button | tune Configure Filters | source-hidden | — |
| 397:1 | input | Filter recent job history by ID, target, or tool | unresolved-static | — |
| 399:1 | button | download Export Archive | unresolved-static | — |

### ui_v2_diagnostics.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 7:4579 | a | Dashboard / Zero State | script-reference | # |
| 7:4836 | a | Scope & Targets | script-reference | # |
| 7:5087 | a | Run & Orchestration | script-reference | # |
| 7:5346 | a | Trust Layer & Findings | script-reference | # |
| 7:5611 | a | PTES Coverage & Reports | script-reference | # |
| 7:6086 | a | AI Strategy Gate | script-reference | # |
| 7:6333 | a | Remediation Retest Studio | script-reference | # |
| 7:6598 | a | Correlated Attack Chains | script-reference | # |
| 7:7061 | a | Job Execution History | script-reference | # |
| 7:7317 | a | Evidence File Inspector | script-reference | # |
| 7:7578 | a | Cryptographic Audit Log | script-reference | # |
| 7:8041 | a | System Diagnostics & Health | script-reference | # |
| 7:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 7:8585 | a | Settings & API Explorer | script-reference | # |
| 7:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 7:11306 | button | add New | unresolved-static | — |
| 7:13011 | button | terminal Terminal Log | unresolved-static | — |
| 7:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 42:1 | button | restart_alt Restart Engine Daemons | script-reference | btn-restart-daemons |
| 46:1 | button | file_download Export Health Report (.json) | script-reference | btn-export-json |
| 50:1 | button | play_circle Run Full Diagnostic [F5] | script-reference | btn-run-diag |
| 263:1 | button | Probe Socket | inline-handler | pingService('PostgreSQL') |
| 290:1 | button | Benchmark Cache | inline-handler | pingService('SQLite Replay') |
| 317:1 | button | Ping Handshake | inline-handler | pingService('Metasploit RPC') |
| 344:1 | button | Probe RingBuffer | inline-handler | pingService('eBPF Kernel') |
| 371:1 | button | Warmup Inference | inline-handler | pingService('AI Planner') |
| 398:1 | button | Check Queue | inline-handler | pingService('Redis Broker') |
| 425:1 | button | Verify Cgroup | inline-handler | pingService('Docker Sandbox') |
| 682:1 | button | Test MSF RPC Handshake | inline-handler | triggerSelfCheck('msf') |
| 685:1 | button | Benchmark SQLite Write Speed | inline-handler | triggerSelfCheck('sqlite') |
| 688:1 | button | Probe Ollama LLM Socket | inline-handler | triggerSelfCheck('llm') |
| 691:1 | button | Check eBPF Filter Integrity | inline-handler | triggerSelfCheck('ebpf') |
| 694:1 | button | Clear Console | inline-handler | clearTerminalLogs() |

### ui_v2_evidence.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 6:4579 | a | Dashboard / Zero State | script-reference | # |
| 6:4836 | a | Scope & Targets | script-reference | # |
| 6:5087 | a | Run & Orchestration | script-reference | # |
| 6:5346 | a | Trust Layer & Findings | script-reference | # |
| 6:5611 | a | PTES Coverage & Reports | script-reference | # |
| 6:6086 | a | AI Strategy Gate | script-reference | # |
| 6:6333 | a | Remediation Retest Studio | script-reference | # |
| 6:6598 | a | Correlated Attack Chains | script-reference | # |
| 6:7060 | a | Job Execution History | script-reference | # |
| 6:7317 | a | Evidence File Inspector | script-reference | # |
| 6:7578 | a | Cryptographic Audit Log | script-reference | # |
| 6:8041 | a | System Diagnostics & Health | script-reference | # |
| 6:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 6:8585 | a | Settings & API Explorer | script-reference | # |
| 6:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 6:11306 | button | add New | unresolved-static | — |
| 6:13011 | button | terminal Terminal Log | unresolved-static | — |
| 6:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 46:1 | button | cloud_sync Sync Merkle Tree | unresolved-static | — |
| 50:1 | button | inventory_2 Export TAR.GZ | unresolved-static | — |
| 145:1 | button | Collapse all | unresolved-static | — |
| 148:1 | button | Refresh | unresolved-static | — |
| 157:1 | input | Search filename, sha256, tool... | unresolved-static | — |
| 319:1 | button | content_copy Copy | unresolved-static | — |
| 361:1 | button | Formatted Tree View | unresolved-static | — |
| 364:1 | button | Raw XML Source | unresolved-static | — |
| 367:1 | button | Parsed Tables | unresolved-static | — |
| 370:1 | button | Hex View | unresolved-static | — |
| 387:1 | button | download Download Raw | unresolved-static | — |
| 391:1 | button | fingerprint Verify SHA-256 Hash | unresolved-static | — |
| 395:1 | button | auto_fix_high Re-parse into Finding Model | unresolved-static | — |
| 399:1 | button | send_to_mobile Send to Issue Tracker | unresolved-static | — |
| 600:1 | a | Entry #4409 | unresolved-static | # |
| 642:1 | button | Trace Proof | unresolved-static | — |
| 658:1 | button | Trace Proof | unresolved-static | — |

### ui_v2_findings.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4470 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4816 | a | target Scope & Targets | script-reference | # |
| 4:5148 | a | terminal Run & Orchestration | script-reference | # |
| 4:5490 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5843 | a | analytics PTES Coverage & Reports | script-reference | # |
| 30:1 | button | replay Retest Verified Scope | inline-handler | runRetestAll() |
| 126:1 | button | ALL | unresolved-static | — |
| 127:1 | button | CRIT (1) | unresolved-static | — |
| 128:1 | button | HIGH (2) | unresolved-static | — |
| 129:1 | button | MED (1) | unresolved-static | — |
| 130:1 | button | LOW (0) | unresolved-static | — |
| 135:1 | button | ALL | unresolved-static | — |
| 136:1 | button | VERIFIED (6) | unresolved-static | — |
| 137:1 | button | CANDIDATE (11) | unresolved-static | — |
| 138:1 | button | REVIEW NEEDED | unresolved-static | — |
| 143:1 | button | ALL | unresolved-static | — |
| 144:1 | button | Nuclei | unresolved-static | — |
| 145:1 | button | sqlmap | unresolved-static | — |
| 146:1 | button | Nikto | unresolved-static | — |
| 151:1 | input | Filter findings by proof pattern, URL, or CVE | script-reference | whaxon-finding-filter |
| 247:1 | button | content_copy Copy Evidence | script-reference | copy-btn |
| 309:1 | button | play_arrow Replay Test (Retest) | script-reference | replay-btn |
| 313:1 | button | check Mark Fixed | inline-handler | markFixedAction() |
| 319:1 | button | file_export Export Proof to Issue Tracker | inline-handler | exportProofAction() |
| 323:1 | button | how_to_reg Send to Approvals | inline-handler | sendToApprovalsAction() |

### ui_v2_history.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 6:4579 | a | Dashboard / Zero State | script-reference | # |
| 6:4836 | a | Scope & Targets | script-reference | # |
| 6:5087 | a | Run & Orchestration | script-reference | # |
| 6:5346 | a | Trust Layer & Findings | script-reference | # |
| 6:5611 | a | PTES Coverage & Reports | script-reference | # |
| 6:6086 | a | AI Strategy Gate | script-reference | # |
| 6:6333 | a | Remediation Retest Studio | script-reference | # |
| 6:6598 | a | Correlated Attack Chains | script-reference | # |
| 6:7060 | a | Job Execution History | script-reference | # |
| 6:7317 | a | Evidence File Inspector | script-reference | # |
| 6:7578 | a | Cryptographic Audit Log | script-reference | # |
| 6:8041 | a | System Diagnostics & Health | script-reference | # |
| 6:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 6:8585 | a | Settings & API Explorer | script-reference | # |
| 6:10949 | button | No engagement selected (No target selected) arrow_drop_down | unresolved-static | — |
| 6:11316 | button | add New | unresolved-static | — |
| 6:13022 | button | terminal Terminal Log | unresolved-static | — |
| 6:13361 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 26:1 | button | file_download Export Ledger (.csv / .json) | unresolved-static | — |
| 31:1 | button | verified_user Verify Integrity | unresolved-static | — |
| 133:1 | input | Filter history by recorded job ID, tool, or target | script-reference | history-search |
| 140:1 | select | Filter history by tool | script-reference | history-tool-filter |
| 147:1 | select | Date filter unavailable because timestamps are not recorded | disabled | history-date-filter |
| 154:1 | select | Runner filter unavailable because runner mode is not recorded | disabled | history-runner-filter |
| 163:1 | button | All (42) | unresolved-static | — |
| 167:1 | button | Success (38) | unresolved-static | — |
| 172:1 | button | Failed (3) | unresolved-static | — |
| 177:1 | button | Scope-Blocked (1) | unresolved-static | — |
| 182:1 | button | Active / Queued (0) | unresolved-static | — |
| 226:1 | button | chevron_left | disabled | — |
| 229:1 | button | chevron_right | unresolved-static | — |

### ui_v2_monitoring.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4579 | a | Dashboard / Zero State | script-reference | # |
| 4:4836 | a | Scope & Targets | script-reference | # |
| 4:5087 | a | Run & Orchestration | script-reference | # |
| 4:5346 | a | Trust Layer & Findings | script-reference | # |
| 4:5611 | a | PTES Coverage & Reports | script-reference | # |
| 4:6086 | a | AI Strategy Gate | script-reference | # |
| 4:6333 | a | Remediation Retest Studio | script-reference | # |
| 4:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 4:6895 | a | Correlated Attack Chains | script-reference | # |
| 4:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 4:7443 | a | PTaaS Client Portal | script-reference | # |
| 4:7896 | a | Job Execution History | script-reference | # |
| 4:8153 | a | Evidence File Inspector | script-reference | # |
| 4:8414 | a | Cryptographic Audit Log | script-reference | # |
| 4:8877 | a | System Diagnostics & Health | script-reference | # |
| 4:9152 | a | Adapter & Plugin Manager | script-reference | # |
| 4:9421 | a | Settings & Secrets Vault | script-reference | # |
| 4:11787 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:12144 | button | add New | unresolved-static | — |
| 4:13849 | button | terminal Terminal Log | unresolved-static | — |
| 4:14188 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 28:1 | button | dns Configure Cloud & DNS Probes | unresolved-static | — |
| 32:1 | button | radar Trigger Delta Recon Now | script-reference | recon-trigger-btn |
| 133:1 | input | Filter FQDN, IP, ASN (e.g. AS13335, 10.0.0.0/8), Cloud Provider... | script-reference | asset-search-input |
| 138:1 | button | All Infra | unresolved-static | — |
| 141:1 | button | AWS (84) | unresolved-static | — |
| 145:1 | button | GCP (36) | unresolved-static | — |
| 149:1 | button | CF (22) | unresolved-static | — |
| 158:1 | button | ALL (142) | unresolved-static | — |
| 161:1 | button | DRIFT DETECTED 7 | unresolved-static | — |
| 165:1 | button | CLOUD EXPOSURES 4 | unresolved-static | — |
| 169:1 | button | EXPIRED/WEAK TLS 3 | unresolved-static | — |
| 176:1 | button | SEVERITY DESC arrow_downward | unresolved-static | — |
| 217:1 | button | Lock Boundary | unresolved-static | — |
| 221:1 | button | Direct Dynamic Inspection | unresolved-static | — |
| 273:1 | button | Remediate S3 Bucket ACL | unresolved-static | — |
| 277:1 | button | Inspect Bucket Contents | unresolved-static | — |
| 323:1 | button | Order ACME Renewal | unresolved-static | — |
| 327:1 | button | tune Harden Ciphers | unresolved-static | — |
| 364:1 | button | terminal Session Shell | unresolved-static | — |
| 368:1 | button | more_vert | unresolved-static | — |
| 385:1 | button | PREV | unresolved-static | — |
| 386:1 | button | NEXT | unresolved-static | — |
| 475:1 | button | Expand Canvas open_in_full | unresolved-static | — |
| 592:1 | button | Stream Full Cryptographic Audit Logs → | unresolved-static | — |

### ui_v2_ptaas.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 206:1124 | a | terminal Dashboard / Zero State | script-reference | # |
| 206:1479 | a | radar Scope & Targets | script-reference | # |
| 206:1821 | a | play_circle Run & Orchestration | script-reference | # |
| 206:2177 | a | verified_user Trust Layer & Findings | script-reference | # |
| 206:2541 | a | description PTES Coverage & Reports | script-reference | # |
| 206:3082 | a | psychology AI Strategy Gate | script-reference | # |
| 206:3429 | a | build_circle Remediation Retest Studio | script-reference | # |
| 206:3796 | a | account_tree Correlated Attack Chains | script-reference | # |
| 206:4161 | a | open_in_browser Bug Bounty & Live Browser | script-reference | # |
| 206:4702 | a | history_toggle_off Job Execution History | script-reference | # |
| 206:5067 | a | folder_zip Evidence File Inspector | script-reference | # |
| 206:5428 | a | encrypted Cryptographic Audit Log | script-reference | # |
| 206:5957 | a | monitor_heart System Diagnostics & Health | script-reference | # |
| 206:6331 | a | extension Adapter & Plugin Manager | script-reference | # |
| 206:6695 | a | shield_person PTaaS Client Portal | script-reference | # |
| 206:7052 | a | key Settings & Secrets Vault | script-reference | # |
| 206:8932 | button | terminal LOGS | unresolved-static | — |
| 206:9235 | button | dangerous HALT SCAN | unresolved-static | — |
| 254:1 | button | add_moderator EXPAND SCOPE | inline-handler | openScopeModal() |
| 258:1 | button | schedule SCHEDULE RETEST | inline-handler | scrollToRetestConsole() |
| 262:1 | button | workspace_premium EXECUTIVE CERTIFICATE | inline-handler | triggerCertDownload() |
| 377:1 | input | e.g. stage-auth.stripe-internal.dev | script-reference | targetInput |
| 378:1 | button | RUN PRE-FLIGHT | inline-handler | runPreflightValidation() |
| 397:1 | input | (unnamed) | unresolved-static | — |
| 404:1 | input | (unnamed) | unresolved-static | — |
| 411:1 | input | (unnamed) | unresolved-static | — |
| 417:1 | button | rocket_launch DISPATCH ACCREDITED JOB | inline-handler | launchAssessment() |
| 437:1 | button | ALL (18) | unresolved-static | — |
| 438:1 | button | ACTION NEEDED (4) | unresolved-static | — |
| 439:1 | button | RESOLVED (14) | unresolved-static | — |
| 467:1 | button | VIEW RAW PACKET open_in_new | inline-handler | toggleProof('proof-1') |
| 493:1 | button | refresh REQUEST VERIFICATION RETEST | inline-handler | requestRetest('BOLA / IDOR in Merchant Transfer Settlement Route') |
| 523:1 | button | VIEW SCRIPT open_in_new | inline-handler | toggleProof('proof-2') |
| 619:1 | div | picture_as_pdf Executive Brief (PDF) v2.1 • 14 Pages • Cryptographic | inline-handler | downloadArtifact('Executive_Brief_Q4.pdf') |
| 632:1 | div | slideshow Board-Ready Deck (Slides) Keynote & PPTX • High-level KPIs | inline-handler | downloadArtifact('Board_Risk_Deck_2026.key') |
| 645:1 | div | table_chart Remediation Matrix (Jira CSV) Atlassian Schema • CVSS v3 | inline-handler | downloadArtifact('Findings_Jira_Sync.csv') |
| 683:1 | button | PING SEC-OPS | unresolved-static | — |
| 698:1 | button | close | source-hidden | closeScopeModal() |
| 705:1 | textarea | e.g. api-v3-staging.internal.stripe.com 192.168.12.0/24 (VPC Peered) | source-hidden | — |
| 711:1 | select | Synchronized with Primary RoE (Now through Nov 02, 2026) Restricted  | source-hidden | — |
| 722:1 | button | CANCEL | source-hidden | closeScopeModal() |
| 725:1 | button | SIGN & SUBMIT ROE ADDENDUM | source-hidden | confirmScopeExpansion() |

### ui_v2_report.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4821 | a | target Scope & Targets | script-reference | # |
| 4:5153 | a | terminal Run & Orchestration | script-reference | # |
| 4:5495 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5848 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9396 | button | terminal Terminal Log | unresolved-static | — |
| 4:9735 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 279:1 | button | All Gaps (3) | unresolved-static | — |
| 280:1 | button | Policy (2) | unresolved-static | — |
| 281:1 | button | Safety (1) | unresolved-static | — |
| 363:1 | input | (unnamed) | unresolved-static | — |
| 371:1 | input | (unnamed) | unresolved-static | — |
| 379:1 | input | (unnamed) | unresolved-static | — |
| 387:1 | input | (unnamed) | unresolved-static | — |
| 428:1 | button | visibility Preview Markdown | script-reference | previewBtn |
| 432:1 | button | data_object Export Findings (.json) | unresolved-static | — |
| 436:1 | button | download Download Full Report (.pdf) | unresolved-static | — |
| 489:1 | a | download Raw | unresolved-static | # |
| 504:1 | a | download Raw | unresolved-static | # |
| 519:1 | a | download Raw | unresolved-static | # |
| 534:1 | a | download Raw | unresolved-static | # |
| 555:1 | button | close | source-hidden | closePreviewBtn |

### ui_v2_reports.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | target Scope & Targets | script-reference | # |
| 4:4807 | a | terminal Run & Orchestration | script-reference | # |
| 4:5149 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5502 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9037 | button | terminal Terminal Log | unresolved-static | — |
| 4:9376 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 279:1 | button | All Gaps (3) | unresolved-static | — |
| 280:1 | button | Policy (2) | unresolved-static | — |
| 281:1 | button | Safety (1) | unresolved-static | — |
| 363:1 | input | (unnamed) | unresolved-static | — |
| 371:1 | input | (unnamed) | unresolved-static | — |
| 379:1 | input | (unnamed) | unresolved-static | — |
| 387:1 | input | (unnamed) | unresolved-static | — |
| 428:1 | button | visibility Preview Markdown | script-reference | previewBtn |
| 432:1 | button | data_object Export Findings (.json) | unresolved-static | — |
| 436:1 | button | download Download Full Report (.pdf) | unresolved-static | — |
| 489:1 | a | download Raw | unresolved-static | # |
| 504:1 | a | download Raw | unresolved-static | # |
| 519:1 | a | download Raw | unresolved-static | # |
| 534:1 | a | download Raw | unresolved-static | # |
| 555:1 | button | close | source-hidden | closePreviewBtn |

### ui_v2_retest.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Correlated Attack Chains | script-reference | # |
| 5:7061 | a | Job Execution History | script-reference | # |
| 5:7318 | a | Evidence File Inspector | script-reference | # |
| 5:7579 | a | Cryptographic Audit Log | script-reference | # |
| 5:8042 | a | System Diagnostics & Health | script-reference | # |
| 5:8317 | a | Adapter & Plugin Manager | script-reference | # |
| 5:8586 | a | Settings & API Explorer | script-reference | # |
| 5:10950 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:11307 | button | add New | unresolved-static | — |
| 5:13012 | button | terminal Terminal Log | unresolved-static | — |
| 5:13351 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 13:1400 | button | tune FILTER BY 3-WAY VERDICT | unresolved-static | — |
| 13:1750 | button | play_arrow BATCH REPLAY (3x BASELINE + 3x INJECTED) | unresolved-static | — |
| 15:972 | input | Filter Finding, URL, Verification Reason... | unresolved-static | — |
| 15:1384 | button | ALL (5) | unresolved-static | — |
| 15:1571 | button | STILL_VULNERABLE (2) | unresolved-static | — |
| 15:1752 | button | FIXED (2) | unresolved-static | — |
| 15:1928 | button | INCONCLUSIVE (1) | unresolved-static | — |
| 15:12125 | button | Copy endpoint | unresolved-static | — |
| 15:18949 | button | content_copy copy curl | unresolved-static | — |
| 21:345 | button | refresh Re-Execute Replay (3x Baseline + 3x Injected) | unresolved-static | — |
| 21:1679 | input | (unnamed) | unresolved-static | — |
| 21:2308 | input | (unnamed) | unresolved-static | — |
| 21:2943 | input | (unnamed) | unresolved-static | — |
| 21:3692 | input | e.g., timing delta >3.0s (median of 3), xss marker present, candidat | unresolved-static | — |
| 21:4285 | textarea | Enter proof delta justification... | unresolved-static | — |
| 21:4959 | button | refresh RE-EXECUTE IMMEDIATE PROBE | unresolved-static | — |
| 21:5315 | button | data_object EXPORT PROOF AUDIT JSON | unresolved-static | — |
| 21:5679 | button | assignment_turned_in COMMIT 3-WAY VERDICT TO AUDIT LEDGER | unresolved-static | — |

### ui_v2_run.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4821 | a | target Scope & Targets | script-reference | # |
| 4:5153 | a | terminal Run & Orchestration | script-reference | # |
| 4:5495 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5848 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9381 | button | terminal Terminal Log | unresolved-static | — |
| 4:9720 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 54:1 | button | tune Approval Gate: Active | unresolved-static | toggle-planner-gate |
| 105:1 | input | (unnamed) | unresolved-static | — |
| 109:1 | input | (unnamed) | unresolved-static | — |
| 113:1 | input | (unnamed) | unresolved-static | — |
| 117:1 | input | (unnamed) | unresolved-static | — |
| 121:1 | input | (unnamed) | unresolved-static | — |
| 125:1 | input | (unnamed) | unresolved-static | — |
| 129:1 | input | (unnamed) | unresolved-static | — |
| 133:1 | input | (unnamed) | unresolved-static | — |
| 137:1 | input | (unnamed) | unresolved-static | — |
| 141:1 | input | (unnamed) | unresolved-static | — |
| 149:1 | select | WHAXON tool | script-reference | run-tool-select |
| 150:1 | input | Authorized target host or URL | script-reference | run-target-input |
| 151:1 | button | play_arrow Run Selected Tool | script-reference | run-active-btn |
| 187:1 | input | ai-planner-toggle | script-reference | ai-planner-toggle |
| 223:1 | button | View stdout open_in_new | inline-handler | showNmapStdout() |
| 230:1 | button | Re-run | unresolved-static | — |
| 278:1 | button | Pause | unresolved-static | — |
| 281:1 | button | Abort | unresolved-static | — |
| 335:1 | button | Engage Replay | unresolved-static | — |
| 347:1 | button | explore WhatWeb | unresolved-static | — |
| 351:1 | button | folder_zip Gobuster | unresolved-static | — |
| 355:1 | button | security WPScan | unresolved-static | — |
| 392:1 | button | Clear buffer | inline-handler | clearLog() |
| 485:1 | input | Type command (e.g. validate --id=F-104, pause, resume, replay)... | script-reference | cli-input |
| 486:1 | button | Execute | inline-handler | sendManualCommand() |
| 494:1 | button | pause_circle Pause Pipeline | inline-handler | togglePipelinePause() |
| 499:1 | button | input Inject Payload | inline-handler | injectPayloadPrompt() |
| 504:1 | button | add_circle Spawn Sub-tool | inline-handler | spawnSubtoolModal() |
| 509:1 | button | emergency_home Emergency Abort | inline-handler | emergencyAbort() |

### ui_v2_scope.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4821 | a | target Scope & Targets | script-reference | # |
| 4:5153 | a | terminal Run & Orchestration | script-reference | # |
| 4:5495 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5848 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9679 | button | terminal Terminal Log | unresolved-static | — |
| 4:10018 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 28:1 | button | file_upload Quick Import | script-reference | openImportDrawerBtn |
| 32:1 | button | add_circle Add In-Scope Target | script-reference | openTargetModalBtn |
| 101:1 | button | Waiting for scope | disabled | toggleScopeEnforcementBtn |
| 119:1 | input | Filter configured scope rules | script-reference | targetFilterInput |
| 147:3069 | button | link View Certificate SAN Chain | source-hidden | — |
| 147:3404 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 147:3702 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 147:4827 | button | link View Certificate SAN Chain | source-hidden | — |
| 147:5162 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 147:5460 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 147:6577 | button | link View Certificate SAN Chain | source-hidden | — |
| 147:6912 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 147:7210 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 162:1 | input | hostname, IP, or URL | script-reference | scopeCheckTarget |
| 163:1 | button | Check | script-reference | runScopeCheckBtn |
| 164:1 | button | Copy CLI | script-reference | copyCliBtn |
| 223:1 | button | add_moderator Add Boundary Exclusion | source-hidden | addDenyRuleBtn |
| 266:1 | button | close | source-hidden | closeTargetModalBtn |
| 274:1 | input | Authorized target hostname, IP address, or CIDR | source-hidden | modalTargetInput |
| 279:1 | input | (unnamed) | source-hidden | — |
| 283:1 | input | (unnamed) | source-hidden | — |
| 288:1 | input | AUTHORIZATION-REFERENCE | source-hidden | — |
| 291:1 | input | authConfirmCheckbox | source-hidden | authConfirmCheckbox |
| 299:1 | button | Cancel | source-hidden | cancelTargetModalBtn |
| 300:1 | button | Commit to Scope | source-hidden | saveTargetBtn |
| 312:1 | button | close | source-hidden | closeImportDrawerBtn |
| 320:1 | button | Burp XML/JSON | source-hidden | — |
| 321:1 | button | scope.json | source-hidden | — |
| 322:1 | button | CIDR List | source-hidden | — |
| 327:1 | textarea | Paste scope JSON definition | source-hidden | — |
| 331:1 | button | Cancel | source-hidden | cancelImportDrawerBtn |
| 332:1 | button | Import & Parse Rules | source-hidden | executeImportBtn |

### ui_v2_settings.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 206:1124 | a | terminal Dashboard / Zero State | script-reference | # |
| 206:1479 | a | radar Scope & Targets | script-reference | # |
| 206:1821 | a | play_circle Run & Orchestration | script-reference | # |
| 206:2177 | a | verified_user Trust Layer & Findings | script-reference | # |
| 206:2541 | a | description PTES Coverage & Reports | script-reference | # |
| 206:3082 | a | psychology AI Strategy Gate | script-reference | # |
| 206:3429 | a | build_circle Remediation Retest Studio | script-reference | # |
| 206:3796 | a | account_tree Correlated Attack Chains | script-reference | # |
| 206:4161 | a | open_in_browser Bug Bounty & Live Browser | script-reference | # |
| 206:4702 | a | history_toggle_off Job Execution History | script-reference | # |
| 206:5067 | a | folder_zip Evidence File Inspector | script-reference | # |
| 206:5428 | a | encrypted Cryptographic Audit Log | unresolved-static | # |
| 206:5957 | a | monitor_heart System Diagnostics & Health | script-reference | # |
| 206:6331 | a | extension Adapter & Plugin Manager | script-reference | # |
| 206:6695 | a | shield_person PTaaS Client Portal | script-reference | # |
| 206:7051 | a | key Settings & Secrets Vault | script-reference | # |
| 206:8931 | button | terminal LOGS | unresolved-static | — |
| 206:9234 | button | dangerous HALT SCAN | unresolved-static | — |
| 224:1 | button | lock_reset SEAL VAULT | inline-handler | lockVaultMaster() |
| 329:1 | input | (unnamed) | inline-handler | — |
| 347:1 | input | (unnamed) | inline-handler | — |
| 365:1 | input | (unnamed) | inline-handler | — |
| 395:1 | input | budgetSlider | inline-handler | budgetSlider |
| 413:1 | input | confSlider | inline-handler | confSlider |
| 436:1 | input | Filter scope or host... | unresolved-static | — |
| 439:1 | button | add ENCLAVE KEY | inline-handler | openCredentialModal() |
| 479:1 | button | Test / Replay | unresolved-static | — |
| 482:1 | button | Rotate Key | unresolved-static | — |
| 485:1 | button | Revoke & Expunge | unresolved-static | — |
| 511:1 | button | Test / Replay | unresolved-static | — |
| 514:1 | button | Rotate Key | unresolved-static | — |
| 517:1 | button | Revoke & Expunge | unresolved-static | — |
| 543:1 | button | Test / Replay | unresolved-static | — |
| 546:1 | button | Renew Ticket | unresolved-static | — |
| 549:1 | button | Purge | unresolved-static | — |
| 575:1 | button | Test / Replay | unresolved-static | — |
| 578:1 | button | Rotate Key | unresolved-static | — |
| 581:1 | button | Revoke & Expunge | unresolved-static | — |
| 592:1 | a | VIEW COMPLETE REPOSITORY arrow_forward | unresolved-static | # |
| 604:1 | button | download RESYNC CORPUS | unresolved-static | — |
| 642:1 | button | + NEW KEY | inline-handler | triggerKeyGenModal() |
| 717:1 | button | PING | inline-handler | sendTestPing('Slack SecOps') |
| 732:1 | button | PING | inline-handler | sendTestPing('DefectDojo') |
| 747:1 | button | PING | inline-handler | sendTestPing('Jira Engine') |
| 762:1 | button | PING | inline-handler | sendTestPing('Discord Hook') |
| 767:1 | button | add_link REGISTER ENDPOINT | unresolved-static | — |
| 794:1 | button | close | source-hidden | closeKeyGenModal() |
| 804:1 | input | e.g. CI_TEST_PIPELINE | source-hidden | newTokenName |
| 808:1 | select | Operator (Execute scans, trigger payloads, write findings) Reviewer  | source-hidden | — |
| 817:1 | button | 30 Days | source-hidden | — |
| 818:1 | button | 90 Days | source-hidden | — |
| 819:1 | button | 365 Days | source-hidden | — |
| 824:1 | button | CANCEL | source-hidden | closeKeyGenModal() |
| 827:1 | button | GENERATE TOKEN | source-hidden | executeTokenGeneration() |
| 841:1 | button | close | source-hidden | closeCredentialModal() |
| 851:1 | input | 10.0.0.0/8 or admin.internal.corp | source-hidden | — |
| 856:1 | select | SSH Private Key (Ed25519) HTTP Bearer JWT Kerberos TGT Ticket AWS IA | source-hidden | — |
| 866:1 | input | admin or svc_account | source-hidden | — |
| 871:1 | textarea | -----BEGIN OPENSSH PRIVATE KEY-----... | source-hidden | — |
| 875:1 | button | ABORT | source-hidden | closeCredentialModal() |
| 878:1 | button | SEAL TO ENCLAVE | source-hidden | closeCredentialModal() |

### ui_v2_threat_intel.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 5:6895 | a | Correlated Attack Chains | script-reference | # |
| 5:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 5:7443 | a | Threat Intel & Exploit Arsenal | script-reference | # |
| 5:7724 | a | BAS & Detection Validation | script-reference | # |
| 5:8209 | a | Job Execution History | script-reference | # |
| 5:8466 | a | Evidence File Inspector | script-reference | # |
| 5:8727 | a | Cryptographic Audit Log | script-reference | # |
| 5:8988 | a | Compliance & Framework Crosswalk | script-reference | # |
| 5:9473 | a | System Diagnostics & Health | script-reference | # |
| 5:9748 | a | Adapter & Plugin Manager | script-reference | # |
| 5:10017 | a | PTaaS Client Portal | script-reference | # |
| 5:10270 | a | Settings & Secrets Vault | script-reference | # |
| 5:12636 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:12993 | button | add New | unresolved-static | — |
| 5:14698 | button | terminal Terminal Log | unresolved-static | — |
| 5:15037 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 104:1 | button | sync Sync Upstream Feeds | unresolved-static | — |
| 108:1 | button | database Rebuild SQLite Vector DB | unresolved-static | — |
| 112:1 | button | terminal Searchsploit Terminal | unresolved-static | — |
| 203:1 | input | Filter by CVE-ID, service (OpenSSH, RDP, FortiOS), CVSS, EPSS... | unresolved-static | — |
| 207:1 | select | Severity (CVSS DESC) EPSS Probability Weaponized First CISA KEV List | unresolved-static | — |
| 217:1 | button | All (14) | inline-handler | toggleFilter('all', this) |
| 220:1 | button | CISA KEV (5) | inline-handler | toggleFilter('cisa', this) |
| 223:1 | button | Weaponized PoC (8) | inline-handler | toggleFilter('weaponized', this) |
| 226:1 | button | Remote Code Execution (4) | inline-handler | toggleFilter('rce', this) |
| 229:1 | button | PrivEsc (3) | inline-handler | toggleFilter('privesc', this) |
| 236:1 | div | CVE-2024-6387 RegreSSHion (OpenSSH Race Condition) CVSS 9.8 EPSS 88. | inline-handler | selectCve('CVE-2024-6387', 'RegreSSHion — OpenSSH Signal Handler Race  |
| 263:1 | button | code Inspect Exploit Code | unresolved-static | — |
| 266:1 | button | sensors Queue Safe Probe | unresolved-static | — |
| 269:1 | button | tune Simulate Dry-Run | unresolved-static | — |
| 275:1 | div | CVE-2024-38077 MadLicense (Windows RDP Gateway) CVSS 9.8 EPSS 94.6%  | inline-handler | selectCve('CVE-2024-38077', 'MadLicense — Windows Remote Desktop Licen |
| 301:1 | button | terminal Metasploit Harness | unresolved-static | — |
| 304:1 | button | data_object Inspect MSF Options | unresolved-static | — |
| 310:1 | div | CVE-2023-38606 BOLA in Internal Merchant API Endpoint CVSS 8.4 EPSS  | inline-handler | selectCve('CVE-2023-38606', 'Broken Object Level Authorization (BOLA)  |
| 335:1 | button | play_arrow Execute Curl Replay Test | unresolved-static | — |
| 341:1 | div | CVE-2024-21762 Fortinet FortiOS SSL-VPN OOB Write CVSS 9.6 EPSS 96.8 | inline-handler | selectCve('CVE-2024-21762', 'Fortinet FortiOS SSL-VPN Out-of-Bounds Wr |
| 366:1 | button | assignment_turned_in View Nuclei Heuristics | unresolved-static | — |
| 397:1 | button | Source Code | inline-handler | switchExploitTab('tab-source') |
| 400:1 | button | Mechanics | inline-handler | switchExploitTab('tab-mechanics') |
| 403:1 | button | Guardrails | inline-handler | switchExploitTab('tab-guardrails') |
| 406:1 | button | Artifacts | inline-handler | switchExploitTab('tab-artifacts') |
| 419:1 | button | content_copy Copy | unresolved-static | — |
| 503:1 | input | (unnamed) | unresolved-static | — |
| 510:1 | input | (unnamed) | unresolved-static | — |
| 518:1 | button | gavel Arm & Queue for HITL Approval Gate | unresolved-static | — |


---

## Part 5 — web ui files and rendering/obsidian_kinetic/DESIGN.md (source record)

---
name: Obsidian Kinetic
colors:
  surface: '#0f131c'
  surface-dim: '#0f131c'
  surface-bright: '#353942'
  surface-container-lowest: '#0a0e16'
  surface-container-low: '#181c24'
  surface-container: '#1c2028'
  surface-container-high: '#262a33'
  surface-container-highest: '#31353e'
  on-surface: '#dfe2ee'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dfe2ee'
  inverse-on-surface: '#2c3039'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#e29100'
  on-tertiary-container: '#523200'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131c'
  on-background: '#dfe2ee'
  surface-variant: '#31353e'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 20px
  body-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  code-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.06em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 12px
    letterSpacing: 0.08em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.75rem
  gutter-lg: 1rem
  margin: 1rem
  margin-mobile: 0.75rem
  space-xs: 0.25rem
  space-sm: 0.375rem
  space-md: 0.5rem
  space-lg: 0.75rem
  space-xl: 1rem
  space-2xl: 1.5rem
---

## Brand & Style

This design system embodies high-stakes operational defense, cryptographic rigor, and deterministic precision. Built for elite offensive security engineers, Red Teams, and SecOps commanders executing synchronized operations, it trades decorative ornamentation for absolute signal-to-noise clarity, rapid cognitive processing, and mission certainty.

The aesthetic fuses **Precision Engineering** with **Technical Minimalism**:
- **Tactical Utility:** Dense, compact arrangements that optimize screen real estate for complex multi-pane workspaces, target trees, and continuous event telemetry.
- **Controlled Luminescence:** A layered dark environment where color is strictly semantic—reserved for validation tiers, severity states, telemetry rates, and lethal execution signals.
- **Architectural Rigor:** Sharp delineation, structured 1px framing, low-contrast structural grids, and monospaced data anchors that invoke military-grade console hardware.
- **Uncompromising Determinism:** State changes, terminal buffers, and inspection surfaces behave predictably with instant transitions, zero layout shifts, and absolute type hierarchy.

## Colors

The palette leverages a deep obsidian hierarchy to simulate physical command hardware, establishing a high-density backdrop where operational telemetry stands out with zero optical fatigue.

### Color Hierarchy & Roles
- **Primary (`#10B981` — Cyber Emerald):** Operational safety, verified targets within legal scope, authenticated nodes, passed exploits, and confirmed operational boundaries.
- **Secondary (`#06B6D4` — Cyber Teal):** Active network scanners, data streams, dynamic telemetry, routing links, interactive utility triggers, and telemetry graphs.
- **Tertiary (`#F59E0B` — Tactical Amber):** Candidate findings, unvalidated scope deviations, warnings, human-in-the-loop review queues, and unstable payloads.
- **Critical Severity (`#EF4444` — Tactical Crimson):** Confirmed vulnerabilities (RCE, SQLi, SSRF), operational breaches, out-of-bounds alerts, and abort commands.
- **Neutral Core (`#0B0F17` — Deep Obsidian):** Root canvas ground.
  - Surface Tier 1 (`#111827` — Deep Charcoal): Structural sidebars, rail panels, and bottom dock drawers.
  - Surface Tier 2 (`#1E293B` — Slate Matrix): Cards, modal layers, terminal envelopes, and inspection cells.
  - Borders & Dividers (`#334155` / `rgba(255,255,255,0.08)`): Hairline structural separators.
  - Text Primary (`#F8FAFC`): Absolute legibility for code payloads and telemetry parameters.
  - Text Muted (`#94A3B8`): Contextual headers, metadata keys, and secondary descriptors.

## Typography

The typographic architecture balances technical authority, compact scanning, and zero character ambiguity:
- **Headlines (Space Grotesk):** Provides structured geometric confidence for module titles, CVE matrices, and panel headers.
- **Body & Controls (Inter):** High x-height and neutral geometry allow dense dashboard grids and nested tree nodes to remain readable under extreme density without distraction.
- **Code, Data & Labels (JetBrains Mono):** Dedicated to technical artifacts: raw payloads, regex targets, cURL strings, IP/CIDR notations, hash digests, and status badges. Features distinctive glyph shaping to avoid confusion between `0` / `O` and `1` / `l` / `I`.
- **All-Caps Metrics:** Small status tags and data labels (`label-md`, `label-sm`) default to uppercase with extended letter spacing (`0.06em` to `0.08em`) to establish visual contrast against prose.

## Layout & Spacing

The command center uses a strict, low-overhead fluid grid with fixed utility rails:
- **Spatial Logic:** A base 4px spatial rhythm tuned down for maximum information density. Standard margins are compact (`1rem` / 16px), and panel gutters maintain tight adjacency (`0.75rem` / 12px) to maximize horizontal data span.
- **Desktop Architecture (1440px+):** 
  - Primary persistent left rail: 56px (collapsed) to 220px (expanded) for operational phase switching.
  - Multi-pane workspace: 3-column split layout (Scope Tree: 280px fixed; Attack Surface / Finding Matrix: dynamic flex; Target Detail / Raw Inspector: 440px fixed or collapsible drawer).
- **Reflow Rules:**
  - **Tablet (768px - 1024px):** Target Detail moves to a floating bottom drawer; secondary panels stack into tabs.
  - **Mobile (< 768px):** Collapses to single-pane task focus with bottom-docked command navigation. Grid margins drop to `0.75rem`.

## Elevation & Depth

This system intentionally eliminates soft, diffuse consumer dropshadows. Depth is articulated purely through tonal luminance tiers and precise 1px perimeter framing.

- **Level 0 (Canvas Base — `#0B0F17`):** Non-interactive foundation and grid background.
- **Level 1 (Docked Surfaces — `#111827`):** Structural sidebars, top status HUD, and terminal split panes. Separated by `1px solid rgba(255, 255, 255, 0.07)`.
- **Level 2 (Containers & Cards — `#1E293B`):** Data tables, finding summaries, target nodes, and payload editors. Outlined with `1px solid rgba(255, 255, 255, 0.12)`.
- **Level 3 (Interactive Hover & Flyouts — `#27354A`):** Popover inspectors, command palettes, and context menus. Paired with a concentrated tactical shadow: `0 4px 12px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(6, 182, 212, 0.25)`.
- **Semantic Backglow:** High-threat cards and critical alert states utilize subtle localized glow accents (`box-shadow: 0 0 12px rgba(239, 68, 68, 0.15)`) to direct immediate visual triage without obstructing neighboring data.

## Shapes

The design system enforces a sharp, engineered geometry (`roundedness: 1`):
- **Base Elements (Buttons, Inputs, Badges, Tabs):** 4px (`0.25rem`) border radius, evoking precision-cut instrumentation panels.
- **Card Containers & Panels (`rounded-lg`):** 8px (`0.5rem`) border radius for modular workspace units.
- **Dialogs & Overlays (`rounded-xl`):** 12px (`0.75rem`) border radius maximum.
- **Zero Pill Shapes:** Circular pills are prohibited; all tags, status flags, and metric badges maintain crisp 4px corners to avoid consumer-app associations and preserve tabular horizontal rhythm.

## Components

### Buttons
- **Primary Tactical:** Solid Emerald background (`#10B981`), charcoal-black text (`#0B0F17`), weight 600, height 32px, padding 0 12px. Hover: `#059669`. Active: `#047857`. Focus: 2px offset ring in `#10B981`.
- **Secondary / Ghost Utility:** Transparent background, 1px border `#334155`, text `#F8FAFC`. Hover: `#1E293B` background, border `#06B6D4`.
- **Destructive / Abort Action:** High-saturation Crimson fill (`#EF4444`) or 1px Crimson border with semi-transparent tint (`rgba(239, 68, 68, 0.12)`). Used for attack cancel, payload detonate, or credential purge.

### Chips & Badges
- Strict monospaced typography (`label-sm`).
- **In-Scope / Verified:** Tinted background `rgba(16, 185, 129, 0.12)`, border `1px solid rgba(16, 185, 129, 0.3)`, text `#10B981`.
- **Review Needed / Ambiguous:** Background `rgba(245, 158, 11, 0.12)`, border `1px solid rgba(245, 158, 11, 0.3)`, text `#F59E0B`.
- **Critical / Exploit Available:** Background `rgba(239, 68, 68, 0.14)`, border `1px solid rgba(239, 68, 68, 0.4)`, text `#F87171`. Includes a pulsing 4px indicator pip.

### Inputs & Terminal Fields
- Background `#0B0F17`, border `1px solid #334155`, text `#F8FAFC`, placeholder `#64748B`. Height 32px.
- Focus: Border shifts instantly to Cyber Teal (`#06B6D4`) with zero transition lag; no blurry glow.
- Monospace variant for payload inputs, target regex, CIDR filters, and auth tokens.

### Data Tables & Tree Grids
- Ultra-dense row height: 32px default, 28px condensed.
- Row zebra striping omitted in favor of thin border separators (`1px solid rgba(255, 255, 255, 0.05)`). Hover state: row tint `#1E293B`.
- Headers: JetBrains Mono `label-sm`, all-caps, text `#94A3B8`, background `#111827`.

### Code Blocks & Raw Inspection Panes
- Background `#080C14` with a persistent top metadata banner (displaying syntax mode, byte size, and copy button).
- Monospace font (`code-sm` / 11px), 16px line height. Active execution lines highlighted with `rgba(6, 182, 212, 0.1)`.
- Distinct syntax tokens: Methods (GET/POST) color-coded, query params in `#06B6D4`, injection payloads in `#F59E0B` or `#EF4444`.

### Specialized Domain Components
- **Scope Verification Banner:** Dual-state header lock indicating operational mandate, legal authorization timeframe, and IP range constraints.
- **CVE / Finding Severity Pill:** Compact micro-indicator displaying CVSS base score alongside metric vectors (`AV:N/AC:L/PR:N`).
- **Telemetry Pulse Indicator:** Constant 6px radar dot in teal/emerald indicating active agent heartbeat and live proxy socket health.
