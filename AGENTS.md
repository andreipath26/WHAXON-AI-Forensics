# Repository contributor instructions

Before any change to the V2 UI, its routes, templates, designs, browser tests or UI-facing API contracts, **read and apply `docs/V2_UI_MANDATORY_CROSSWALK.md`**. It is the single mandatory crosswalk for all 22 pages and shared UI work. Refer to its source-of-truth links, per-page D1–D6 acceptance gates and review record. Do not claim UI deployment readiness without proof. The E6 engine integration freeze stays in effect until explicitly lifted by the operator.

## Dashboard freeze — operator instruction (2026-11-05)

**The V2 Dashboard page is FROZEN following merge of PR #126.** Do not edit, replace, reformat, refactor, re-test by altering frozen test source, redesign, regenerate bundled assets, create new Dashboard PRs, or deploy further Dashboard code until the operator **explicitly authorizes an unfreeze**. This includes the Dashboard template, its static assets/fonts/licenses/manifests, its dedicated test files and related build/vendor/install scripts and dedicated GitHub workflows. The original supplied Dashboard design references remain immutable. The rest of V2 UI may continue under the mandatory 22-page crosswalk; the E6 integration freeze remains separate and active. `.github/workflows/dashboard-frozen.yml` checks proposed PR changes to these files. Do not remove or circumvent the guard.

## Desktop-only UI and current UI freeze — operator instruction (2026-11-05)

WHAXON is not intended to run on mobile devices. Do not implement, modify, test, or propose mobile support, responsive navigation, mobile-specific layouts, or mobile viewport acceptance. Do not spend engineering time or agent tokens on mobile support. Any historical mobile references in the UI crosswalk or old PRs are superseded by this instruction; UI acceptance is desktop-only.

All UI implementation work is currently FROZEN. Do not start or continue UI feature work unless the operator explicitly lifts this freeze. Engine V2 work may continue independently, subject to the existing E6 freeze and release gates.

## Engine V2 gate sequencing and closure freeze — operator instruction (2026-11-05)

Work solo-release gates in order, starting with G01. Do not begin a later gate until the current gate meets its full deployment acceptance and its closure record is complete. Source changes, a passing component test, inventory presence, or green CI alone do not close a gate.

For each completed gate, update the Engine V2 master ledger with the exact candidate SHA, requirement IDs, assertions, supported environment, CI/lab evidence, limitations, reviewer and operator decision. Then mark the gate **FROZEN** and add a change guard for its accepted implementation and evidence before proceeding. Do not edit a frozen gate or its accepted files/test evidence unless the operator explicitly reopens it or a verified safety/correctness defect requires a narrowly scoped repair. Respect the current UI freeze; UI-dependent acceptance remains blocked until explicitly lifted.

