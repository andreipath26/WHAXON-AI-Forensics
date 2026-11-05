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
