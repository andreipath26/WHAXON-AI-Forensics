Warning: truncated output (original token count: 30271)
Total output lines: 1574

# WHAXON — UI V2 DESIGN, INTERACTION AND ACCEPTANCE MASTER

> **Current UI / delivery reconciliation — 2026-11-14, main code head `272245e700dfa89835f44886f370b011c1786cf1`.** UI safety and reliability PRs #203 (Adapters), #204 (Run), #206 (AI), #213 (disconnected Adapter configuration controls), #214 (deterministic Findings browser data), and #215 (truthful Reports unavailable state) are merged. The exact source candidate tree `75880425cdaf4857989f229638e59c5b65de099f` passed all 20 CI jobs in run #43624338670, including the isolated G01 chain. The regenerated inventory contains 808 controls across 22 templates. All 22 route rows remain open for full behavior/control wiring and D1–D6 acceptance. Complete implementation and internal tests before final external/manual/deployment qualification. Supported UI scope remains desktop.

> **Current-main reconciliation — 2026-11-21:** main is now `f32ce0913d460f046f6d984ec54a1f7f5d775409`; PR #226's exact head passed CI [44833852913](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833852913), README freeze [44833852900](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833852900), and dashboard acceptance [44833853031](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/44833853031) before merge. The source-control inventory at `272245e700dfa89835f44886f370b011c1786cf1` remains the latest static count: 808 controls across 22 templates. PR #226 did not add fresh per-control runtime acceptance. All 22 route rows and per-control wiring remain open; D1–D6 qualification stays deferred until implementation and internal checks are complete.

**Canonical UI implementation and post-completion qualification reference.** Use this crosswalk to complete the 22-page agreed UI scope. Source, tests, screenshots, and exact-head CI establish implementation behavior. Run internal browser/API checks throughout implementation. D1–D6 are final external/manual/deployment qualification criteria and are not prerequisites for implementing the UI. Start that qualification only after the agreed V2 engine and UI scope is complete and internal checks pass. Do not infer that one page's results establish another page's behavior.

**Supported scope:** This product targets desktop. Continue UI implementation within the supplied design and service contracts. Historical mobile/responsive references below are not current scope. Manual visual and accessibility reviews remain deferred until post-implementation qualification.

## Part I — Canonical UI V2 contract and page crosswalk

# Mandatory WHAXON V2 UI crosswalk — all 22 pages

**Scope:** All V2 UI designs, production pages, shared navigation, client APIs, desktop entry points, tests and reviews. This is the **single canonical UI-wide crosswalk**, not a Dashboard-only plan.
**Authority:** root roadmap P4/P5 and §38 G01–G10, the [project governance master](PROJECT_GOVERNANCE_MASTER.md), [Engine V2 master](ENGINE_V2_MASTER.md), and the UI audit, inventory, and supplied-design text consolidated later in this master.
**Implementation rule:** E6 UI integration is active work. Finish the agreed controls, workflows, and shared-service integration before external qualification. Do not redesign canonical supplied page variants. Internal tests and fixes proceed during implementation.

## REQUIRED BEFORE EACH UI TASK (human or agent)

1. **Locate page in matrix below**; inspect its supplied named source/PNG, variant, production template, tests, static control inventory, server route and exact source HEAD. Resolve ambiguous variants with the design owner; never silently replace a supplied design.
2. **Propose a bounded change:** user-visible outcome; affected UI IDs/controls; ownership and dependencies; exact backend endpoints, authorization/scope/approval policy; loading, empty, unavailable, error, cancellation, reconnect and offline behavior.
3. **Verify honest state:** API 200 is not proof of success; queued is not completed; completed is not verified; do not synthesize findings, active sessions, PTES coverage, audit cryptography, live workers or UI permissions. Unsupported actions must be labelled and disabled/hidden safely.
4. **Keep one owner for a shared file.** Batch independent work using explicit interfaces and no conflicting concurrent writes, per the engineering execution model. No uncontrolled UI parallel rewrite.
5. **Write internal regression tests with the change:** source/binding checks, Playwright interactions (including negative/malformed responses), client authorization and shared Core contracts where relevant; test supported desktop behavior, focus/keyboard, dark appearance and no overflow. Schedule manual assistive-technology review after the agreed UI and engine scope is complete.
6. **Record implementation evidence as work proceeds:** code SHA, internal test command, CI outcomes/skips, control-to-service mapping, and known limits. After implementation is complete, record the deferred external visual, manual accessibility/security, and deployment outcomes against the exact release candidate.
7. **Implementation review:** check all relevant control rows, service contracts, and internal browser/API tests; leave unimplemented or unsupported behavior explicitly identified. Do not block further implementation because D1–D6 post-completion qualification is pending.

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

### Approvals migration checkpoint — 2026-11-11

The Approvals page now loads persisted moderate/high/critical V2 tasks from
`GET /api/v2/approval-queue` and records exact task approvals through the V2
workflow approval endpoint. It does not submit work. Pending legacy AI runs
remain visible read-only; this page no longer posts answers or resumes their
executor. Blocked V2 tasks are displayed without a grant action because an
approval cannot unblock or retry them. UI-22 remains open for the D1–D6 review
gates below, broader queue-state coverage, and exact-head CI evidence.

The V2 Findings, BAS and Retest pages also no longer issue legacy validation
or retest mutations. Candidate findings link to V2 verification planning and
verified findings to V2 retest planning; both require sealed Engine V2 evidence
and current scope before the server saves a plan. Review, approval and durable
submission remain separate. Legacy routes remain available to older clients.
UI-11 and UI-17 remain open for the D1–D6 gates below.

All templates live under `src/whaxon/interfaces/web/templates/`; browser tests live under `tests/`. The dashboard alias `/ui-v2/dashboard` and root entry route `/` additionally require parity checks. Common tests: `test_web_ui_v2_route_matrix.py`, `test_web_ui_v2_navigation.py`, `test_web_ui_v2_control_inventory.py`; auxiliary pages share the listed suites. The regenerated inventory records **808 static controls across 22 templates** at code head `272245e700dfa89835f44886f370b011c1786cf1`; script references do not establish live bindings.

## Acceptance criteria for EVERY row

| Gate | Required proof | Default |
|---|---|---|
| D1 Design | Exact approved supplied screen and variant; desktop screenshot comparisons and no accidental visual changes | OPEN |
| D2 Controls | Every visible enabled control reachable, named, authorized and mapped to a real action; disabled/hidden ones documented with rationale | OPEN |
| D3 Runtime truth | Live API data, empty/unavailable/error/unauthorized/blocked/race states and rollback truthful, no invented records | OPEN |
| D4 Security | Scope/approval/consent on server; CSRF/Origin, XSS and secret redaction; no UI-only policy | OPEN |
| D5 Accessibility | Keyboard-only navigation, focus return, semantic labels, contrast/non-color cues and assistive-tech manual review | OPEN |
| D6 Deployment | Supported browser/desktop and platform checks, external asset/offline policy, versioned exact-SHA CI and release reviewer | OPEN |

A page becomes `DEPLOYMENT_READY` **only when D1–D6 each have exact-source evidence and explicit approver sign-off**. No aggregate percentage or page route smoke closes any gate. UI readiness does **not** automatically approve E6 or full product deployment.

### Emergency Halt Scan: legacy and Engine V2 cancellation boundary

Every enabled V2 Emergency Halt Scan control discovers legacy active jobs from `GET /api/jobs/active` and durable V2 requests from `GET /api/v2/workflow-runs/summary`. Both responses must be successful and have the expected list shape before the UI offers cancellation; an unavailable or malformed source fails the operation closed. Only rows explicitly marked `engine_v2_owned: false` are treated as legacy jobs. V2-owned rows and rows without a boolean ownership marker are not sent to the legacy job cancellation route.

After operator confirmation, the UI sends legacy job IDs only to `POST /api/jobs/<job_id>/cancel`, and durable request IDs from `active_requests[].id` only to `POST /api/v2/workflow-runs/<request_id>/cancel`. V2 active requests include `queued`, `running` and `uncertain` states. A successful response means cancellation was requested. It does **not** prove that an in-flight or uncertain provider/external effect stopped; the UI says so in its result. Partial failures report requested counts rather than claiming a complete stop.

This shared contract is implemented for the 14 previously legacy-only handlers in Adapters, AI Gate, Approvals, Audit, BAS, Bug Bounty, Chains, Compliance, Diagnostics, Evidence, Monitoring, PTaaS, Retest and Threat Intelligence. Dashboard and Settings already queried both services; they also now omit V2-owned job rows from legacy cancellation. Run's plan-specific durable cancellation remains unchanged.

## Work queue and Dashboard-first checkpoint

**Priority UI-01 Dashboard:** current template `ui_v2_dashboard.html`, route `/ui-v2`, browser suite `test_web_ui_v2_dashboard.py`, and supplied `web ui files and rendering/dashboard_engagement_hub_zero_state/`. Existing live functionality includes history/filters/JSON export, scope routing, job halt, Burp XML import, health/readiness labels. Known blocker: full approved screenshot and accessibility verification, complete per-control permission/malformed-response mapping, packaging/network asset policy.

Dashboard batch 1 hardens malformed-history export: a successful HTTP response with non-array payload must **fail visibly** rather than export a misleading empty archive; added browser regression. It does not alter visual design. **Dashboard remains NOT deployment-ready** until all D1–D6 complete.

**Next after Dashboard and Scope & Targets:** UI-03 Run & Orchestration, then UI-04 Findings, then evidence/report workflows and the remaining pages; order follows critical dependencies and is adjustable without skipping gates. Scope PR #127 is merged, but UI-02 deployment acceptance remains OPEN.

### Run & Orchestration (UI-03) — candidate hardening, 2026-11-05

**Reference and scope:** `web ui files and rendering/run_tool_orchestration/screen.png`, route `/ui-v2/run`, template `src/whaxon/interfaces/web/templates/ui_v2_run.html`, and browser module `tests/test_web_ui_v2_run.py`. The supplied design source remains unchanged. The guarded Run action performs an asynchronous scope check before posting to `/api/run`; two rapid clicks could previously pass the active-job check before either response set the current job, causing duplicate dispatches. The candidate adds a single-flight guard, disables the action while the authorization and dispatch request is pending, and adds a regression that asserts one scope check and one run request for two immediate clicks.

**Evidence and limits:** Local `ruff check tests/test_web_ui_v2_run.py` and `tests/test_v2_ui_mandatory_crosswalk.py` passed. The browser regression could not run locally because the Playwright Chromium download was truncated in this environment. Exact-head CI is required. This is one safety improvement; it does not establish complete control mapping, backend V2 parity or any D1–D6 acceptance. UI-03 remains **OPEN** pending the complete per-page evidence and approver sign-offs.

**Engine V2 durable run handoff — 2026-11-09:** The Run page now has a separate control for reviewing an already-persisted V2 plan, displaying its task capability/target/impact bindings, checking listed approvals for each moderate-or-higher task, submitting through `POST /api/v2/workflows/<plan_id>/run`, reconnecting through durable snapshots, and requesting cancellation through the durable run-request endpoint. It does not grant approval, claim that a queued request completed, or claim that cancellation stopped an external effect. The active V2 request ID is retained in session storage for same-tab reconnect. The server's legacy `/api/run` endpoint remained available to other clients while parity was unfinished.

**Saved plan discovery — 2026-11-09:** The V2 handoff now lists persisted missions and their plans through the bounded mission/plan read APIs. Operators can select a plan and review its immutable tasks before submitting. A plan ID can still be entered directly when working from a CLI/API-created plan. No mission or plan is created by this selector, and all authorization remains in the V2 execution path. Full UI-03 acceptance remains **OPEN**.

**Constrained plan authoring and consent — 2026-11-09:** The Run page can create a mission and one-task immutable plan only from an installed, selected, moderate-impact V2 capability whose declared inputs require no caller-supplied fields. The plan records the provider ID and inventory manifest fingerprint for execution-time pinning. Creation performs a scope preview and creates no execution request. A separate explicit confirmation records one-hour exact-task approval through the V2 approval endpoint. The actor is server-derived (`local` for loopback, verified username for remote Basic-auth requests); the endpoint does not provide role separation or an independent-approver guarantee. The scheduler still rechecks scope, provider binding, plan integrity and approval binding. Multi-step plans and capabilities requiring inputs remain CLI/API authored. UI-03 and D1–D6 remain **OPEN**.

**Engine V2 finding ownership and retest proposal — 2026-11-11:** Legacy CLI and web `validate`/`retest` routes reject V2-owned evidence before network replay or mutation, returning a workflow-required result. V2 Findings, BAS and Retest pages avoid legacy validation/retest posts. Candidate findings link to V2 verification-plan authoring, while verified findings link to V2 retest-plan authoring through `POST /api/v2/workflow-proposals`. The provider checks source-job ownership, evidence seal, exact finding sequence, supported kind, and current scope. A saved plan links to Run & Orchestration for task review, explicit approval, and separate durable run submission; proposal creation itself neither approves nor executes. Legacy validation/retest remains available to older clients and for legacy-owned findings. Browser acceptance cases were updated; execution still requires the existing V2 consent and lifecycle path. No supplied design source was changed. UI-11, UI-17 and D1–D6 remain **OPEN**.

**Run page primary dispatch migration — 2026-11-11:** The primary Run page action now creates an immutable Engine V2 mission and single-task plan from the selected installed V2 capability, after a scope preview. It does not call `/api/run`, open the legacy job event stream, or execute the new plan. The operator reviews the exact task, separately grants approval, and submits through the durable V2 run control. The catalog selector is marked as inventory-only; the unconstrained direct-run cancel control is hidden. Browser regressions cover saved-plan-only behavior, out-of-scope refusal, and single-flight plan creation with no legacy dispatch. The server's `/api/run` endpoint remains for legacy clients, and broader capability/transport parity and UI-03 acceptance remain **OPEN**.

**AI Gate plan-only migration — 2026-11-12:** The AI Gate form now creates a V2 mission and requests a saved plan through `POST /api/v2/ai/proposals`. The proposal is scope-checked again by the server and uses the bound provider contract. A saved plan links to Run & Orchestration for separate task review, exact approval and durable submission. The page does not call `/api/ai/run`; its legacy AI run history is read-only, and pending legacy runs cannot be authorized or resumed from this page. Both legacy execution endpoints, `/api/ai/run` and `/api/ai/runs/<run_id>/answer`, are default-denied and require explicit `WHAXON_LEGACY_AI_EXECUTION_ENABLED=true` opt-in. Browser regressions cover blocked server scope despite a spoofed client preview, plan-only save, no legacy resume, and the Run handoff. UI-10 and D1–D6 remain **OPEN**.

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
| D1 Design | OPEN | Approver-approved comparison to `web ui files and rendering/dashboard_engagement_hub_zero_state/screen.png` at representative supported desktop viewports |
| D2 Controls | PARTIAL | Runtime inventory of every visible control with final expected action, loading/empty/error and authorization behavior, including generated elements |
| D3 Runtime truth | CANDIDATE | New negative-case Playwright assertions, exact-head CI success, cross-client integration and monitored supported staging |
| D4 Security | PARTIAL | Independent server-side authorization/CSRF review, malicious content escaping, permission-denied/timeout/cancel proofs |
| D5 Accessibility | PARTIAL | Keyboard/focus, high zoom, non-color cues, contrast and assistive-technology manual sign-off |
| D6 Deployment | OPEN | Exact candidate browser/desktop tests, packaged fonts/icons/CSS or explicitly approved connected-only asset policy and failover, target-environment rollout/rollback evidence |

**Historical decision:** At the time, the Dashboard was recorded as not deployment-ready pending D1–D6 evidence. This dated checkpoint is not an active implementation freeze and does not establish that the operator approved each sign-off criterion. Current sequence: finish implementation and internal tests first; defer external qualification.

### Dashboard action safety update — 2026-11-05

- Emergency halt requests are single-flight within the dashboard session, to prevent duplicate submissions from repeated clicks. A malformed job identity is not sent to the cancellation endpoint; a partial cancel result remains an incomplete cancellation request, not proof of stopped effects.
- Error outcomes use an assertive accessibility alert role. Non-error informational updates use a status region. Added browser negative tests for invalid job IDs and alert signaling.
- Source changes are bounded to the production Dashboard template and browser tests; no design source was modified. **D1–D6 remain OPEN until evidence and sign-off are recorded**. Prior green CI is not exact-head acceptance.

### Dashboard crosswalk evidence — untrusted content and access denial

The Dashboard browser suite includes adversarial browser checks that scope and job-history text are not converted to executable markup, that all visible navigational links resolve to canonical UI routes, and that a 403 cancellation response never becomes a false stop-success claim. These are candidate proofs for D2–D4, not an independent security sign-off. Browser tests must pass for the exact candidate SHA, and deployment D1/D5/D6 remain unaccepted.

### Dashboard bundled styling milestone

The Dashboard now serves a build-time compiled, pinned Tailwind stylesheet from `/static/dashboard-v2.css`, with the build recipe `scripts/build_dashboard_css.cjs` and isolated branch-only vendor workflow. The runtime Tailwind CDN script is removed; its checked-in theme configuration remains non-executable for reproducible asset builds. Browser regression coverage blocks remote Tailwind and Google Fonts and verifies canonical background styling and live page operation using the bundled CSS. D6 **remains OPEN** because font/icon/image availability, final source-distribution install checks, approved network/offline support policy, target rollout and rollback, and operator acceptance require independent proof.

### Dashboard WCAG audit remediation
**Historical candidate result (mobile viewport scope superseded):** **Historical candidate result (mobile viewport scope superseded):** Automated axe-core WCAG 2 A/AA and 2.1 A/AA review on the integrated browser candidate found exactly one rule family failing at desktop and mobile: `document-title`. The production Dashboard now provides a descriptive HTML `<title>`, with a browser regression. The automated audit must be rerun on the exact post-fix SHA before its result is accepted. Automated success does not replace manual assistive-technology, contrast, zoom and keyboard review.

### Dashboard independently hosted static assets

The Dashboard production template no longer requests fonts, Material Symbols icons, logo, or avatar from Google hosts and no longer uses the runtime Tailwind CDN. The packaged local static assets include `dashboard-v2.css`, `dashboard-fonts.css`, 18 hashed font binaries, two supplied design images and license/source SHA-256 records. A browser regression blocks **all external HTTPS requests** and requires the Dashboard to function, render its canonical dark styling, and load both images using loopback-only static URLs. This addresses third-party page-view leakage and advances D6. Other supported environments, wheel/sdist inclusion, rollback, visual/manual accessibility and release approval remain independent requirements.

### Distribution packaging acceptance automation
The focused Dashboard workflow now builds both the `whaxon` wheel and source distribution, and invokes `scripts/check_dashboard_distribution.py`. The check requires the deployed template's CSS/fonts/images, fonts' license notices and manifest in **both** archives, and verifies SHA-256 for every bundled binary against the generated manifest. D6 packaging is accepted only once this exact-head step passes; supported-host deployment/rollback and explicit reviewer signoff remain separate.

### Parallel wheel-install and HTTP asset deployment lane
A second, independent GitHub Actions job builds the wheel+sdist, checks all packaged Dashboard resources/licenses against SHA-256 records, installs the built wheel into an isolated fresh virtual environment, starts `whaxon serve` on loopback and verifies live `/ui-v2` plus each local CSS/font/image URL via HTTP. It runs **in parallel** with visual, functional and automated WCAG browser checks. Full operator deployment authorization, actual host upgrade/rollback, manual screen-reader review and design signoff remain open.

### Exact-head CI reconciliation — 2026-11-05

At candidate `106c64f18e9762f4635043accee1338f513dd2f3`, [full CI run 42010899550](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42010899550) has now **completed SUCCESS**, including Python 3.11/3.12/3.13 test lanes and platform setup smoke. Python 3.11 and 3.13 source-distribution and clean-wheel smoke steps were **skipped**, while the Python 3.12 equivalents passed; do not count skips as passes. [Focused Dashboard run 42010899499](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42010899499) completed SUCCESS in both `dashboard` (browser, screenshot capture, automated axe) and `dashboard-install` (wheel/sdist manifest SHA and isolated loopback HTTP) jobs. These outcomes were verified against the exact PR head before this documentation update; **this documentation commit creates a new head requiring fresh exact-head CI**.

**Post-implementation qualification checklist:** The repository's current D1–D6 checklist describes desktop visual comparison, per-control mapping, staging/client parity, security, manual accessibility, and deployment/rollback evidence. Perform any applicable external/manual checks only after the agreed V2 engine and UI scope is implemented and internal checks pass. This checklist is repository documentation; it does not claim an unverified personal approval from the operator.

## Historical Dashboard UI-01 checkpoint — 2026-11-05

PR [#126](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/126) merged at `c9dea5b40e5150a0fa02dbd313365af9edaaca7d`. The repository added a Dashboard change guard and described the page as frozen at that time. This is retained as historical repository state; it is not an active instruction to stop UI implementation. Current delivery order is to complete the agreed UI and engine implementation, continue internal testing, and defer D1–D6 qualification until implementation is complete. Any remaining source-control guard must be reconciled with that active sequence before it can block authorized implementation work.

**Enforcement limitation:** the guard fails violating PR checks, but only repository branch protection or rulesets requiring that check (plus restricting direct pushes/admin bypass) can prevent an authorized maintainer from merging or pushing anyway. The active GitHub integration cannot administer those settings. Until repository administrators enable such controls, this is a documented contributor prohibition plus an automated PR check, not an absolute technical lock.


---

## Part 2 — docs/NEW_UI_INTERACTION_AUDIT.md (source record)

# New Default Web UI — Interaction and Acceptance Audit

> **Integration update — 2026-11-02, supersedes affected baseline statements below:** Four one-shot CLI commands now use `initialize(drain=False)` with regression coverage. Desktop startup targets `/ui-v2`. Test catalog consumers use the packaged seed; the duplicate tracked root catalog and unused qasync requirement/manifest entry are removed, while operator catalogs and protected legacy designs remain preserved. See [UI control inventory](#part-4--docsui_control_inventorymd-source-record) for the regenerated 808 source controls across 22 templates at code head `272245e700dfa89835f44886f370b011c1786cf1`; static coverage does not establish complete runtime wiring, visual fidelity, accessibility or service parity. Local browser execution is blocked by unavailable Chromium downloads. The earlier CI/source records below describe their stated baseline, not acceptance of this integration.


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
| `/ui` | Previous web interface | Preserved compatibility/reference route; the shipped desktop launcher does not use it |
| Desktop launcher | `gui/app.py` → `embed.URL` | Opens `/ui-v2`; regression coverage verifies the launcher destination matches the root redirect and renders the supplied V2 UI |

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
6. **Desktop/default entry points:** the shipped `whaxon-gui` entry point opens `/ui-v2`; `tests/test_gui_entrypoint.py` checks that destination against the root redirect and verifies the page renders. The separate, unreferenced `interfaces/gui/main_window.py` still contains direct legacy runner calls and remains packaged pending downstream-import review and clean-wheel qualification. Web-route CI does not prove native desktop parity.
7. **Exact candidate:** the inspected baseline is CI-green. Repeat required browser/E2E and acceptance checks for the final release candidate rather than relying on earlier commits.

## 7. Branch and PR reconciliation

At the time of this audit there were no open pull requests; the repository was checked again on 2026-11-02 and still had none open. The canonical UI integration PRs #37, #41 and #42, and the subsequent UI wiring/truthfulness PRs #43–#73, were already merged into `main`. The old full-wiring PR #16 was closed unmerged as a draft; its own description explicitly said not to merge because wiring and browser acceptance were incomplete. PRs #33–#36 were superseded by the later integrated UI work. Their old branch tips must not be blindly merged over newer main code.

No alternate UI or runtime implementation is created by this documentation refresh. Current branch comparison and retirement conditions are in the [due-diligence register](PROJECT_GOVERNANCE_MASTER.md). Stale historical branches are not merge candidates merely because they still exist.

## 8. Release gate

Do not mark the new UI DONE or deployment-ready until the acceptance gaps above are closed, browser and visual regression checks pass on the candidate commit, security regressions pass, and the roadmap's §38 release checklist is updated with observed evidence.


---

## Part 3 — docs/WEB_UI_INTERACTION_AUDIT.md (source record)

> **Historical audit — superseded (2026-11-02).** This file records an earlier UI generation and must not be used to assess the current Obsidian Kinetic UI. Its page inventory, PASS/WIRED/MOCKUP labels, endpoint wiring and test counts are historical. Use [New UI interaction audit](#part-2--docsnew_ui_interaction_auditmd-source-record) for the current 22-route implementation/acceptance record and master roadmap §38 for release acceptance. This historical file is retained for traceability only.

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
| F.01 | Findings list | Load bounded persisted job/finding pages; disclose total and returned coverage; load older pages; show empty, unavailable, malformed-response, and retry states | Implemented | GET /api/ui-v2/findings?limit=&offset= | API TEST ADDED; BROWSER CI PENDING |
| F.02 | Finding card | Select a finding and inspect only recorded fields | Implemented | none | EXISTING BROWSER TEST |
| F.03 | Validate selected finding | Open V2 Verification & Retest Studio for a sealed-evidence verification proposal | V2 plan proposal only | `/api/v2/workflow-proposals`; legacy POST remains for older clients | Browser test guards against legacy mutation |
| F.04 | Retest selected / verified findings | Open V2 Verification & Retest Studio for a sealed-evidence retest proposal | V2 plan proposal only | `/api/v2/workflow-proposals`; legacy POST remains for older clients | Browser test guards against legacy mutation |
| F.05 | Severity, status, and adapter filters | Filter the live list; each filter can be cleared | Implemented | none | WIRED |
| F.06 | Finding search | Search finding and recorded evidence fields | Implemented | none | EXISTING BROWSER TEST |
| F.07 | Copy Evidence | Copy the selected finding's recorded evidence | Implemented | Clipboard API | WIRED |
| F.08 | Scope status | Display current scope summary and enforcement state | Implemented | GET /api/scope | EXISTING BROWSER TEST |
| F.09 | Mark Fixed / Issue Tracker export / approvals | Unsupported controls are hidden; no state is claimed | Hidden at runtime | none | HIDDEN |

The Findings page reads a snapshot-consistent page from `GET /api/ui-v2/findings`, which avoids full report enrichment. It shows total and loaded counts and offers bounded older-job pages; each page is limited to 100 jobs and reports when older jobs remain. The page metadata applies to completed and failed legacy/V2 jobs. This is still partial page wiring and browser acceptance remains required.

The former F.05 “Sort headers” and F.06 “Density toggle” rows described controls absent from this card-list design and are retired. Bulk verify/delete and the AI banner are not controls in the current source; they are not counted as hidden controls. Mark Fixed, Issue Tracker export, and approvals remain source-visible placeholder buttons with inert handlers; current page JavaScript hides them at runtime until real actions exist.

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
| T.01 | Queue table | Show candidate and verified findings with current recorded status | Live queue | GET /api/report | WIRED |
| T.02 | Verify/retest button (row) | Save a V2 plan proposal for a candidate/verified sealed finding | V2 plan proposal only | POST /api/v2/workflow-proposals | Existing browser acceptance case |
| T.03 | V2 retest proposal | Persist a sealed-evidence retest plan for a selected V2 mission; never approve or execute it | UI proposal | POST /api/v2/workflow-proposals | IMPLEMENTED; BROWSER TEST ADDED |
| T.04 | Review V2 plan | Open the saved plan in Run & Orchestration for exact binding review, approval and separate durable submission | Canonical V2 run workflow | `/ui-v2/run?plan_id=<id>` → GET `/api/v2/workflows/<plan_id>` | IMPLEMENTED; BROWSER TEST ADDED |

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

**Source baseline:** Current draft head `97d8b850f16ea8abb8411f77a0c929e8dee6b09`. Regenerated from all 22 production `ui_v2_*.html` templates using the stdlib HTML parser in `tests/test_web_ui_v2_control_inventory.py`. Regenerate after template changes. This records static source controls only; it does not imply runtime acceptance.

## Evidence boundary

This is a complete **static source-control registry**, not a declaration that every control is live or accepted. It covers anchors, buttons, inputs, selects, textareas, summaries explicit button/link roles, inline event handlers, focusable tabindex and editable elements, including initially hidden controls. IDs are template plus one-based line:column; minified shell markup can share a line. Controls dynamically created by JavaScript, computed CSS visibility, event delegation and backend permissions require runtime inspection.

`source-hidden` includes an explicit hidden ancestor/class/style and can be responsive; `disabled` is declared disabled; `declared-nav` has a canonical href; `inline-handler` declares JavaScript; `script-reference` only means an ID/data-path or explicit `data-filter-action`/`data-filter-value` is referenced in an inline script, **not** that an event handler or backend works; `unresolved-static` means no binding was established by this conservative inspection. Unresolved controls are review items, not automatically dead controls. Every source row retains its binding evidence for follow-up.

## Acceptance still open

- The cross-page browser contract checks all 22 rendered destinations and rejects visible placeholder/unknown sidebar links after page scripts run. Page-specific tests remain the behavioral evidence for other controls.
- Complete runtime action/service/authorization mapping for every visible control, including loading/error/cancellation/reconnect states and generated controls.
- Visual comparison against approved supplied reference choices; no screenshot baselines were fabricated or auto-approved.
- Keyboard/focus/screen-reader/non-color/manual accessibility acceptance. Static labels and ordinary Playwright clicks do not close it.
- Full CLI/API/UI operation parity and deliberate-difference register, plus deployment tests for external fonts/Tailwind/icons/images.

## Page summary

| Template | Controls | Source-hidden | Disabled | Declared nav | Inline handler | Script reference | Unresolved static |
|---|---:|---:|---:|---:|---:|---:|---:|
| ui_v2_adapters.html | 48 | 0 | 30 | 0 | 0 | 12 | 6 |
| ui_v2_ai.html | 21 | 0 | 2 | 0 | 0 | 14 | 5 |
| ui_v2_approvals.html | 37 | 9 | 0 | 0 | 10 | 4 | 14 |
| ui_v2_audit.html | 43 | 0 | 0 | 0 | 13 | 17 | 13 |
| ui_v2_bas.html | 32 | 0 | 0 | 0 | 0 | 20 | 12 |
| ui_v2_bug_bounty.html | 32 | 0 | 0 | 0 | 0 | 16 | 16 |
| ui_v2_chains.html | 25 | 0 | 0 | 0 | 0 | 15 | 10 |
| ui_v2_compliance.html | 40 | 0 | 0 | 0 | 0 | 20 | 20 |
| ui_v2_dashboard.html | 36 | 2 | 0 | 0 | 0 | 21 | 13 |
| ui_v2_diagnostics.html | 33 | 0 | 0 | 0 | 12 | 17 | 4 |
| ui_v2_evidence.html | 35 | 0 | 0 | 0 | 0 | 14 | 21 |
| ui_v2_findings.html | 27 | 2 | 0 | 1 | 4 | 20 | 0 |
| ui_v2_history.html | 31 | 0 | 3 | 0 | 0 | 16 | 12 |
| ui_v2_monitoring.html | 45 | 0 | 0 | 0 | 0 | 19 | 26 |
| ui_v2_ptaas.html | 42 | 5 | 0 | 0 | 11 | 17 | 9 |
| ui_v2_report.html | 22 | 1 | 0 | 1 | 0 | 5 | 15 |
| ui_v2_reports.html | 21 | 1 | 2 | 0 | 0 | 5 | 13 |
| ui_v2_retest.html | 36 | 0 | 0 | 0 | 0 | 14 | 22 |
| ui_v2_run.html | 50 | 0 | 34 | 1 | 1 | 12 | 2 |
| ui_v2_scope.html | 39 | 25 | 1 | 5 | 0 | 6 | 2 |
| ui_v2_settings.html | 61 | 15 | 0 | 0 | 12 | 15 | 19 |
| ui_v2_threat_intel.html | 53 | 0 | 0 | 0 | 13 | 20 | 20 |

**Total:** 808 source controls across 22 templates.

## Exact source registry

Labels and binding excerpts are generated from the complete tracked templates; line:column identifies the source control. This registry is a static snapshot, not runtime acceptance.

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
| 18:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | btn-sync |
| 22:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | btn-reload |
| 26:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | btn-register |
| 116:1 | input | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | adapter-search |
| 121:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 124:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 127:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 130:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 133:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 140:1 | select | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | status-select |
| 188:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 232:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 276:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 320:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 363:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 407:1 | button | Read-only reference: this adapter configuration action is not connected to a live WHAXON workflow. | disabled | — |
| 451:1 | button | Read-only reference: this adapter configuration action is not connected to a live WHAXON workflow. | disabled | — |
| 495:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 545:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | close-drawer |
| 583:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 587:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 591:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 595:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 597:1 | input | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | add-flag-input |
| 631:1 | input | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 638:1 | input | (unnamed) | disabled | — |
| 645:1 | input | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | — |
| 661:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | btn-mock-test |
| 666:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | btn-resign |
| 669:1 | button | Read-only reference: this control is not connected to a live WHAXON workflow. | disabled | btn-save-conf |

### ui_v2_ai.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4719 | a | Dashboard / Zero State | script-reference | # |
| 4:4976 | a | Scope & Targets | script-reference | # |
| 4:5227 | a | Run & Orchestration | script-reference | # |
| 4:5486 | a | Trust Layer & Findings | script-reference | # |
| 4:5751 | a | PTES Coverage & Reports | script-reference | # |
| 4:6226 | a | AI Strategy Gate | script-reference | # |
| 4:6472 | a | Remediation Retest Studio | script-reference | # |
| 4:6737 | a | Correlated Attack Chains | script-reference | # |
| 4:7200 | a | Job Execution History | script-reference | # |
| 4:7457 | a | Evidence File Inspector | script-reference | # |
| 4:7718 | a | Cryptographic Audit Log | script-reference | # |
| 4:8181 | a | System Diagnostics & Health | script-reference | # |
| 4:8456 | a | Adapter & Plugin Manager | script-reference | # |
| 4:8725 | a | Settings & API Explorer | script-reference | # |
| 4:11089 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:11446 | button | add New | unresolved-static | — |
| 4:13151 | button | terminal Terminal Log | unresolved-static | — |
| 4:13490 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 84:1 | button | close Legacy response disabled Use V2 plan controls | disabled | btn-reject |
| 91:1 | button | bolt V2 approval in Run Separate action | disabled | btn-authorize |
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
| 164:1 | div | CRITICAL SQLi: Time-based Blind VERIFIED /api/v1/catalog/items?id= CVSS 9.8 Nuclei / sqlmap timer Delta: 5021ms (Threshold: 5000ms) CONFIRM 100% | inline-handler | selectFinding(1) |
| 191:1 | div | HIGH Stored Cross-Site Scripting (XSS) VERIFIED /v1/reviews/post (comment payload parameter) CVSS 7.5 Nuclei HTTP fingerprint Proof Nonce: <whaxon_proof_nonce_492> CONFIRMED | inline-handler | selectFinding(2) |
| 218:1 | div | HIGH BOLA Authorization Bypass CANDIDATE /api/v2/tenant/billing (tenant_id switch) CVSS 8.2 WHAXON Adapter approval_delegation Requires Operator Replay Approval QUEUED | inline-handler | selectFinding(3) |
| 245:1 | div | MEDIUM Exposed .env Backup Secret File VERIFIED /backup/.env.production.bak CVSS 6.5 Nikto Web check_circle Matched Pattern: DB_PASSWORD=[a-zA-Z0-9_]{16} EXIT 0 | inline-handler | selectFinding(4) |
| 332:1 | button | content_copy Copy Command | inline-handler | copyProofCurl() |
| 407:1 | button | play_arrow Replay Test (Retest) | inline-handler | triggerReplayAction() |
| 411:1 | button | check Mark Fixed | inline-handler | markFixedAction() |
| 417:1 | button | file_export Export Proof to Issue Tracker | inline-handler | exportProofAction() |
| 421:1 | button | how_to_reg Send to Approvals | inline-handler | sendToApprovalsAction() |
| 521:1518 | button | close | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:600 | input | (unnamed) | source-hidden | — |
| 529:1089 | input | (unnamed) | source-hidden | — |
| 529:1561 | input | (unnamed) | source-hidden | — |
| 529:2020 | textarea | Cross-tenant billing data was exposed in JSON response payload despite token tenant mismatch. Verified manually via modified export parameter. | source-hidden | — |
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
| 162:1 | select | ALL SIGNALS (6) SCOPE MODIFICATION FINDING VERIFICATION PAYLOAD DETONATION EMERGENCY HALT | inline-handler | category-filter |
| 171:1 | button | shield SEALED ONLY | unresolved-static | — |
| 178:1 | button | chevron_left | unresolved-static | — |
| 181:1 | button | chevron_right | unresolved-static | — |
| 203:1 | tr | 2026-03-30T14:22:08.892401Z #EVT-9941 Finding Verified person OP//7749-ALPHA (HSM#01) Finding #F-2026-881 (BOLA in /v2/transfers) sha256: 7b91f03ce89a88... PASS: SEALED data_object | inline-handler | selectEvent('EVT-9941') |
| 235:1 | button | Inspect Hash Tree | unresolved-static | — |
| 241:1 | tr | 2026-03-30T14:18:41.119830Z #EVT-9940 Scope Change key OP//4108-BRAVO (Dual-Auth) WHITELIST: CIDR 192.168.10.0/24 sha256: 4e18ac49b9901d... PASS: SEALED data_object | inline-handler | selectEvent('EVT-9940') |
| 273:1 | button | Inspect Hash Tree | unresolved-static | — |
| 279:1 | tr | 2026-03-30T14:05:12.601944Z #EVT-9939 Payload Detonation memory AUTONOMOUS RUNNER #04 (PID 41902) sqlmap blind injection /items?id=1 sha256: c99201f8b1a3e6... PASS: SEALED data_object | inline-handler | selectEvent('EVT-9939') |
| 311:1 | button | Inspect Hash Tree | unresolved-static | — |
| 317:1 | tr | 2026-03-30T13:42:01.002195Z #EVT-9938 Emergency Halt gavel OP//7749-ALPHA (Manual Abort) ALL 4 RUNNER DAEMONS PURGED sha256: aa82f76c023d19... PASS: SEALED data_object | inline-handler | selectEvent('EVT-9938') |
| 349:1 | button | Inspect Hash Tree | unresolved-static | — |
| 355:1 | tr | 2026-03-30T13:15:55.441920Z #EVT-9937 Tool Invocation terminal DAEMON//NUCLEI-ORCH cve-2024-auth-bypass against /oauth sha256: 02bc79e8a01124... PASS: SEALED data_object | inline-handler | selectEvent('EVT-9937') |
| 386:1 | button | Inspect Hash Tree | unresolved-static | — |
| 392:1 | tr | 2026-03-30T12:59:10.104510Z #EVT-9936 Policy Override verified_user SEC-COMPLIANCE-ROBOT Engagement Window Extended +2h sha256: 9d8213aa7312ee... PASS: SEALED data_object | inline-handler | selectEvent('EVT-9936') |
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
| 320:1 | select | User_A (Attacker Context) User_B (Victim / Target #092) Unauthenticated Guest | unresolved-static | — |
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
| 35:1 | select | Severity: All Vectors Severity: Critical & Compound 10.0 Severity: High (CVSS > 8.0) | unresolved-static | — |
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
| 27:4365 | a | Dashboard / Zero State | script-reference | # |
| 27:4621 | a | Scope & Targets | script-reference | # |
| 27:4872 | a | Run & Orchestration | script-reference | # |
| 27:5131 | a | Trust Layer & Findings | script-reference | # |
| 27:5396 | a | PTES Coverage & Reports | script-reference | # |
| 27:5871 | a | AI Strategy Gate | script-reference | # |
| 27:6118 | a | Remediation Retest Studio | script-reference | # |
| 27:6383 | a | Correlated Attack Chains | script-reference | # |
| 27:6846 | a | Job Execution History | script-reference | # |
| 27:7103 | a | Evidence File Inspector | script-reference | # |
| 27:7364 | a | Cryptographic Audit Log | script-reference | # |
| 27:7827 | a | System Diagnostics & Health | script-reference | # |
| 27:8102 | a | Adapter & Plugin Manager | script-reference | # |
| 27:8371 | a | Settings & API Explorer | script-reference | # |
| 27:8836 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 27:9133 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 27:9418 | a | PTaaS Client Portal | script-reference | # |
| 27:9671 | a | Threat Intelligence | script-reference | # |
| 27:9937 | a | BAS & Detection Validation | script-reference | # |
| 27:10210 | a | Compliance & Framework Crosswalk | script-reference | # |
| 27:10495 | a | Trust Layer Approvals Queue | script-reference | # |
| 27:12616 | button | No active engagement (No target selected) arrow_drop_down | unresolved-static | — |
| 27:12981 | button | add New | unresolved-static | — |
| 27:14694 | button | terminal Terminal Log | unresolved-static | — |
| 27:15033 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 49:1 | button | terminal CLI Help | unresolved-static | — |
| 53:1 | button | vpn_key Update Credentials Now | unresolved-static | — |
| 94:1 | button | history Switch Target Session | unresolved-static | — |
| 98:1 | button | rocket_launch Start New Engagement | unresolved-static | — |
| 209:1 | button | Open Scope Setup arrow_forward | source-hidden | — |
| 248:1 | button | upload Upload Artifact | unresolved-static | — |
| 289:1 | button | play_arrow Deploy Mock | unresolved-static | — |
| 314:1 | button | tune Configure Filters | source-hidden | — |
| 407:1 | input | Filter recent job history by ID, target, or tool | unresolved-static | — |
| 409:1 | button | download Export Archive | unresolved-static | — |
| 417:1 | div | Job history table, scroll horizontally for all columns | unresolved-static | — |

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
| 4:4386 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4732 | a | target Scope & Targets | script-reference | # |
| 4:5064 | a | terminal Run & Orchestration | script-reference | # |
| 4:5406 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5759 | a | analytics PTES Coverage & Reports | script-reference | # |
| 30:1 | button | replay Open V2 Verification & Retest Studio | inline-handler | openV2RetestStudio() |
| 126:1 | button | ALL | script-reference | filter:severity:all |
| 127:1 | button | CRIT (1) | script-reference | filter:severity:critical |
| 128:1 | button | HIGH (2) | script-reference | filter:severity:high |
| 129:1 | button | MED (1) | script-reference | filter:severity:medium |
| 130:1 | button | LOW (0) | script-reference | filter:severity:low |
| 135:1 | button | ALL | script-reference | filter:status:all |
| 136:1 | button | VERIFIED (6) | script-reference | filter:status:verified |
| 137:1 | button | CANDIDATE (11) | script-reference | filter:status:candidate |
| 138:1 | button | REVIEW NEEDED | script-reference | filter:status:review_needed |
| 143:1 | button | ALL | script-reference | filter:adapter:all |
| 144:1 | button | Nuclei | script-reference | filter:adapter:nuclei |
| 145:1 | button | sqlmap | script-reference | filter:adapter:sqlmap |
| 146:1 | button | Nikto | script-reference | filter:adapter:nikto |
| 151:1 | input | Filter findings by proof pattern, URL, or CVE | script-reference | whaxon-finding-filter |
| 158:1 | button | Load older findings | source-hidden | whaxon-findings-more |
| 169:229 | button | Retry | source-hidden | whaxon-findings-retry |
| 252:1 | button | content_copy Copy Evidence | script-reference | copy-btn |
| 314:1 | button | play_arrow Open V2 Verification & Retest Studio | script-reference | replay-btn |
| 318:1 | button | check Mark Fixed | inline-handler | markFixedAction() |
| 324:1 | button | file_export Export Proof to Issue Tracker | inline-handler | exportProofAction() |
| 328:1 | button | how_to_reg Send to Approvals | inline-handler | sendToApprovalsAction() |

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
| 619:1 | div | picture_as_pdf Executive Brief (PDF) v2.1 • 14 Pages • Cryptographically Signed download | inline-handler | downloadArtifact('Executive_Brief_Q4.pdf') |
| 632:1 | div | slideshow Board-Ready Deck (Slides) Keynote & PPTX • High-level KPIs & Timeline download | inline-handler | downloadArtifact('Board_Risk_Deck_2026.key') |
| 645:1 | div | table_chart Remediation Matrix (Jira CSV) Atlassian Schema • CVSS v3.1 & Remediation Fixes download | inline-handler | downloadArtifact('Findings_Jira_Sync.csv') |
| 683:1 | button | PING SEC-OPS | unresolved-static | — |
| 698:1 | button | close | source-hidden | closeScopeModal() |
| 705:1 | textarea | e.g. api-v3-staging.internal.stripe.com 192.168.12.0/24 (VPC Peered) | source-hidden | — |
| 711:1 | select | Synchronized with Primary RoE (Now through Nov 02, 2026) Restricted 48-hour Weekend Window Only Off-peak Business Hours Only (00:00 - 06:00 UTC) | source-hidden | — |
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
| 432:1 | button | Live report data has not loaded. | disabled | — |
| 436:1 | button | Live report data has not loaded. | disabled | — |
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
| 21:3692 | input | e.g., timing delta >3.0s (median of 3), xss marker present, candidate: replay request inconclusive | unresolved-static | — |
| 21:4285 | textarea | Enter proof delta justification... | unresolved-static | — |
| 21:4959 | button | refresh RE-EXECUTE IMMEDIATE PROBE | unresolved-static | — |
| 21:5315 | button | data_object EXPORT PROOF AUDIT JSON | unresolved-static | — |
| 21:5679 | button | assignment_turned_in COMMIT 3-WAY VERDICT TO AUDIT LEDGER | unresolved-static | — |

### ui_v2_run.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4076 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 5:4422 | a | target Scope & Targets | script-reference | # |
| 5:4754 | a | terminal Run & Orchestration | script-reference | # |
| 5:5096 | a | verified_user Trust Layer & Findings | script-reference | # |
| 5:5449 | a | analytics PTES Coverage & Reports | script-reference | # |
| 5:8710 | button | terminal Terminal Log | unresolved-static | — |
| 5:9049 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 55:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | toggle-planner-gate |
| 106:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 110:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 114:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 118:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 122:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 126:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 130:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 134:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 138:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 142:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 157:5 | select | Engine V2 mission | script-reference | v2-mission-select |
| 159:5 | select | Engine V2 workflow plan | disabled | v2-plan-select |
| 160:5 | button | Refresh List | script-reference | v2-refresh-missions |
| 161:5 | button | Review Selected | disabled | v2-use-plan |
| 168:7 | input | Assessment objective | script-reference | v2-mission-objective |
| 170:7 | select | Installed Engine V2 capability | disabled | v2-capability-select |
| 171:7 | button | Create Mission & Plan | disabled | v2-create-plan |
| 177:5 | input | Existing workflow plan ID | script-reference | v2-plan-id |
| 178:5 | button | Review Plan | script-reference | v2-load-plan |
| 179:5 | button | Submit V2 Run | disabled | v2-submit-run |
| 180:5 | button | Request Cancel | disabled | v2-cancel-run |
| 181:5 | button | Inspect Evidence Report | disabled | v2-inspect-report |
| 182:5 | button | Preview Evidence Follow-ups | disabled | v2-propose-followups |
| 192:1 | select | Legacy tool catalog (inventory only) | script-reference | run-tool-select |
| 193:1 | input | Authorized target host or URL | script-reference | run-target-input |
| 194:1 | button | play_arrow Create V2 Plan | script-reference | run-active-btn |
| 230:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | ai-planner-toggle |
| 266:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 273:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 321:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 324:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 378:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 390:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 394:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 398:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 435:1 | button | Clear buffer | inline-handler | clearLog() |
| 528:1 | input | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | cli-input |
| 529:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 537:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | btn-pause |
| 542:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 547:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |
| 552:1 | button | Reference control: this action is not connected to a live Engine V2 workflow. | disabled | — |

### ui_v2_scope.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 26:4304 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 26:4650 | a | target Scope & Targets | declared-nav | /ui-v2/scope |
| 26:4993 | a | terminal Run & Orchestration | declared-nav | /ui-v2/run |
| 26:5344 | a | verified_user Trust Layer & Findings | declared-nav | /ui-v2/findings |
| 26:5711 | a | analytics PTES Coverage & Reports | declared-nav | /ui-v2/reports |
| 26:9283 | button | terminal Terminal Log | unresolved-static | — |
| 26:9622 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 50:1 | button | file_upload Quick Import | script-reference | openImportDrawerBtn |
| 54:1 | button | add_circle Add In-Scope Target | script-reference | openTargetModalBtn |
| 123:1 | button | Waiting for scope | disabled | toggleScopeEnforcementBtn |
| 141:1 | input | Filter configured scope rules | script-reference | targetFilterInput |
| 169:3069 | button | link View Certificate SAN Chain | source-hidden | — |
| 169:3404 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 169:3702 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 169:4827 | button | link View Certificate SAN Chain | source-hidden | — |
| 169:5162 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 169:5460 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 169:6577 | button | link View Certificate SAN Chain | source-hidden | — |
| 169:6912 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 169:7210 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 184:1 | input | hostname, IP, or URL | script-reference | scopeCheckTarget |
| 185:1 | button | Check | script-reference | runScopeCheckBtn |
| 186:1 | button | Copy CLI | script-reference | copyCliBtn |
| 245:1 | button | add_moderator Add Boundary Exclusion | source-hidden | addDenyRuleBtn |
| 288:1 | button | close | source-hidden | closeTargetModalBtn |
| 296:1 | input | Authorized target hostname, IP address, or CIDR | source-hidden | modalTargetInput |
| 301:1 | input | (unnamed) | source-hidden | — |
| 305:1 | input | (unnamed) | source-hidden | — |
| 310:1 | input | AUTHORIZATION-REFERENCE | source-hidden | — |
| 313:1 | input | authConfirmCheckbox | source-hidden | authConfirmCheckbox |
| 321:1 | button | Cancel | source-hidden | cancelTargetModalBtn |
| 322:1 | button | Commit to Scope | source-hidden | saveTargetBtn |
| 334:1 | button | close | source-hidden | closeImportDrawerBtn |
| 342:1 | button | Burp XML/JSON | source-hidden | — |
| 343:1 | button | scope.json | source-hidden | — |
| 344:1 | button | CIDR List | source-hidden | — |
| 349:1 | textarea | Paste scope JSON definition | source-hidden | — |
| 353:1 | button | Cancel | source-hidden | cancelImportDrawerBtn |
| 354:1 | button | Import & Parse Rules | source-hidden | executeImportBtn |

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
| 808:1 | select | Operator (Execute scans, trigger payloads, write findings) Reviewer (Read-only, verify evidence, sign reports) Client-Viewer (Zero target details, summary metrics only) | source-hidden | — |
| 817:1 | button | 30 Days | source-hidden | — |
| 818:1 | button | 90 Days | source-hidden | — |
| 819:1 | button | 365 Days | source-hidden | — |
| 824:1 | button | CANCEL | source-hidden | closeKeyGenModal() |
| 827:1 | button | GENERATE TOKEN | source-hidden | executeTokenGeneration() |
| 841:1 | button | close | source-hidden | closeCredentialModal() |
| 851:1 | input | 10.0.0.0/8 or admin.internal.corp | source-hidden | — |
| 856:1 | select | SSH Private Key (Ed25519) HTTP Bearer JWT Kerberos TGT Ticket AWS IAM STS Role NTLM Password Hash | source-hidden | — |
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
| 207:1 | select | Severity (CVSS DESC) EPSS Probability Weaponized First CISA KEV Listed | unresolved-static | — |
| 217:1 | button | All (14) | inline-handler | toggleFilter('all', this) |
| 220:1 | button | CISA KEV (5) | inline-handler | toggleFilter('cisa', this) |
| 223:1 | button | Weaponized PoC (8) | inline-handler | toggleFilter('weaponized', this) |
| 226:1 | button | Remote Code Execution (4) | inline-handler | toggleFilter('rce', this) |
| 229:1 | button | PrivEsc (3) | inline-handler | toggleFilter('privesc', this) |
| 236:1 | div | CVE-2024-6387 RegreSSHion (OpenSSH Race Condition) CVSS 9.8 EPSS 88.2% CISA KEV Signal handler race condition in OpenSSH's server (sshd) allows unauthenticated remote attackers to execute arbitrary code with root privileges on glibc-based Linux systems. In Scope: ssh://10.142.0.4:22 (Discovered Nmap #4192) Async Python PoC Ready code Inspect Exploit Code sensors Queue Safe Probe tune Simulate Dry-Run | inline-handler | selectCve('CVE-2024-6387', 'RegreSSHion — OpenSSH Signal Handler Race RCE', '9.8 CRITICAL', '88.2%', 'YES', 'ssh://10.142.0.4:22') |
| 263:1 | button | code Inspect Exploit Code | unresolved-static | — |
| 266:1 | button | sensors Queue Safe Probe | unresolved-static | — |
| 269:1 | button | tune Simulate Dry-Run | unresolved-static | — |
| 275:1 | div | CVE-2024-38077 MadLicense (Windows RDP Gateway) CVSS 9.8 EPSS 94.6% CISA KEV Heap-based buffer overflow in Windows Remote Desktop Licensing Service (RDLGS) allowing unauthenticated RCE via RPC interface binding. In Scope: rdp://10.142.1.15:3389 (NetExec Identified) MSF: exploit/windows/rdp/cve_2024_38077 terminal Metasploit Harness data_object Inspect MSF Options | inline-handler | selectCve('CVE-2024-38077', 'MadLicense — Windows Remote Desktop Licensing Service RCE', '9.8 CRITICAL', '94.6%', 'YES', 'rdp://10.142.1.15:3389') |
| 301:1 | button | terminal Metasploit Harness | unresolved-static | — |
| 304:1 | button | data_object Inspect MSF Options | unresolved-static | — |
| 310:1 | div | CVE-2023-38606 BOLA in Internal Merchant API Endpoint CVSS 8.4 EPSS 34.1% NON-KEV Missing access token boundary check in `/v1/merchants/{id}/payouts` allows authenticated lower-tier operators to exfiltrate full banking routing artifacts. In Scope: api.internal.corp/v1/merchants Deterministic Replay Payload play_arrow Execute Curl Replay Test | inline-handler | selectCve('CVE-2023-38606', 'Broken Object Level Authorization (BOLA) in Internal Merchant API', '8.4 HIGH', '34.1%', 'NO', 'https://api.internal.corp/v1/merchants/') |
| 335:1 | button | play_arrow Execute Curl Replay Test | unresolved-static | — |
| 341:1 | div | CVE-2024-21762 Fortinet FortiOS SSL-VPN OOB Write CVSS 9.6 EPSS 96.8% CISA KEV Out-of-bounds write vulnerability in FortiOS SSL-VPN enables remote unauthenticated threat actors to execute arbitrary code via specially crafted HTTP requests. In Scope: vpn.internal.corp:8443 Weaponized Nuclei Template assignment_turned_in View Nuclei Heuristics | inline-handler | selectCve('CVE-2024-21762', 'Fortinet FortiOS SSL-VPN Out-of-Bounds Write RCE', '9.6 CRITICAL', '96.8%', 'YES', 'https://vpn.internal.corp:8443') |
| 366:1 | button | assignment_turned_in View Nuclei Heuristics | unresolved-static | — |
| 397:1 | button | Source Code | inline-handler | switchExploitTab('tab-source') |
| 400:1 | button | Mechanics | inline-handler | switchExploitTab('tab-mechanics') |
| 403:1 | button | Guardrails | inline-handler | switchExploitTab('tab-guardrails') |
| 406:1 | button | Artifacts | inline-handler | switchExploitTab('tab-artifacts') |
| 419:1 | button | content_copy Copy | unresolved-static | — |
| 503:1 | input | (unnamed) | unresolved-static | — |
| 510:1 | input | (unnamed) | unresolved-static | — |
| 518:1 | button | gavel Arm & Queue for HITL Approval Gate | unresolved-static | — |


## Part 5 — web ui files and rendering/obsidian_kinetic/DESIGN.md (historical embedded copy; original restored at supplied path)

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

### Scope & Targets — responsive and installed-wheel candidate evidence (2026-11-05)

This historical Scope UI checkpoint records the 390px fix and automated candidate checks; its mobile details are outside current desktop scope, and the Dashboard-freeze reference is superseded. These automated checks remain implementation evidence. D1–D6 visual, manual accessibility/security, and rollout/rollback qualification is deferred until the full agreed V2 implementation and internal checks are complete.
