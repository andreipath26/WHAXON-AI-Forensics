# WHAXON — Project State

**Last reviewed:** 2026-11-02  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Branch:** `main`  
**Source of truth:** current source, tests, CI results and the master roadmap. This file is a dated status snapshot, not a replacement for those records.

## 1. Release identity

- Runtime package version: **0.11.16** (`src/whaxon/__init__.py`).
- Latest published PyPI version verified for this snapshot: **0.11.16**, published 2026-10-23.
- Package metadata in `pyproject.toml` is synchronized to 0.11.16 and the Beta classifier. The repository's main branch may be ahead of the published wheel.
- **WHAXON v1.0.0 is not declared released here.** Master roadmap §38 remains OPEN until every required acceptance item has evidence and the tag, build and publication state are verified.

## 2. Recorded engineering verification

The master roadmap records earlier passing CI runs, including [#41307525558](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41307525558) and the scheduler-test harness correction [#41445780317](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41445780317) on commit `1cefb99276b8db0bae697b17ca8f781d0c754147`. Those runs are historical evidence for their respective commits only.

**Latest checked pre-audit documentation commit:** `e9b2f02` (2026-11-02). The repository-wide documentation reconciliation is committed as `f0773d5` (18 files changed); its exact-commit CI run [#41456487674](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41456487674) was queued at the time of this review and has no result recorded here. Its workflow run [#41452761676](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41452761676) completed with a Python 3.13 test failure: 1,369 passed, 14 skipped, 1 failed. The failing test is `tests/test_web_ui_v2_auxiliary_pages.py::test_approvals_refresh_queue_and_halt_use_live_apis[chromium]`; the Refresh queue action did not produce the additional `/api/ai/pending` request expected by the test. Other jobs in that run passed. This failure is not attributed to the documentation changes, but the current commit is **not green**. Check Actions for the exact candidate commit before release.

## 3. Current product surfaces

- CLI, TUI, desktop and Flask web service remain available through their documented entry points.
- The root web route redirects to `/ui-v2`. The supplied Obsidian Kinetic implementation contains 22 page routes/templates. The former `/ui` interface is retained as a legacy/reference surface.
- The new UI is implemented and has page-specific browser tests, but the acceptance audit and roadmap §38 still leave visual regression, complete control inventory, accessibility, service parity and deployment-asset checks open. Do not call the UI fully accepted or production-ready.
- Dependency diagnostics and allowlisted installation planning/approval workflows are implemented. Their broader deployment and recovery acceptance remains open; see [Dependency readiness](dependency-readiness.md) and [the implementation/acceptance record](first-run-installation-redesign.md).
- Engine v2 has versioned mission/task contracts, persistence, scheduler/recovery primitives and an initial read-only scanner-provider integration slice. E1 security acceptance, remaining E3 production guarantees, broader E4 reconciliation, E5 shared lifecycle/headless integration, E6 UI acceptance and full end-to-end deployment acceptance remain open. See [Engine v2 crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md).

## 4. Release blockers and open acceptance

The controlling checklist is master roadmap §38. It remains OPEN. The principal gates include:

1. Evidence-backed framework-to-roadmap crosswalk.
2. Independent validation and retest semantics, including inconclusive outcomes.
3. Honest persisted coverage and non-testing disclosure.
4. Complete supplied-UI interaction, visual, accessibility and parity acceptance.
5. Scope, authorization, DNS/pivot and cancellation security regressions.
6. Clean wheel/sdist installation, packaged resources and upgrade checks.
7. Green required CI on the exact release candidate.
8. Matching version, tag, release workflow and PyPI publication.
9. This state record and supporting audits refreshed with actual evidence.

The roadmap is authoritative for the full list and acceptance criteria. A past green CI run or a version string does not close these gates.

## 5. Documentation reconciliation status

A repository-wide inventory identified 102 Markdown files on `main`. They are not all active product documentation. The tree contains current operator guides, the authoritative roadmap, dated implementation/acceptance records, proposed architecture, superseded design notes, an immutable experiment archive, generated sample reports, vendored payload references, legal notices and raw imported GitHub-page captures.

The [documentation reconciliation register](DOCUMENTATION_RECONCILIATION.md) and [documentation index](README.md) classify these materials and define which sources establish current behavior. In particular:

- The root README and operator guides are aligned to the current package identity, CLI setup/doctor behavior, web entry points, interface routes, scope limitations and documented capability boundaries.
- Historical agent, autonomy, session, report and UI design records are not current implementation specifications.
- The old `WHAXON` repository captures and copied roadmap are archival inputs only; they do not define `WHAXON-AI-Forensics`.
- The file named `whaxon_v1.0.0_deployment_release_notes.md` is an unissued draft, not evidence of a v1.0.0 release.
- The experiment folder and generated DVWA reports remain dated evidence artifacts. They are not current product acceptance results.

This classification is a documentation correction, not a declaration that every v1.0 or Engine v2 acceptance gate is closed. The master roadmap §38 remains OPEN. Current source/tests and CI on the exact candidate commit remain mandatory for due diligence.

## 6. Known operational limitations

- Scope checks are application-level preflight controls, not a network firewall or connection-time DNS pin. External tools may follow redirects or make secondary requests. Enforce egress restrictions independently for real engagements.
- Dependency installation is allowlisted and approval-gated, but completed package changes are not generally rolled back. Audit-chain limitations and the absence of an independently stored trust anchor are documented in the installation design.
- Registered catalog tools are not automatically installed, licensed, platform-compatible or fully tested. Check tool readiness and adapter support individually.
- AI output is a proposal, not authorization, execution evidence or a verification verdict.

## 7. How to resume work

1. Read the master roadmap from §0 and the OPEN release checklist in §38.
2. Check current `main`, exact CI status and the latest UI/Engine v2 acceptance records.
3. Work on the highest-priority unmet dependency; do not restart completed work from historical session notes.
4. Update this file only when new evidence exists, including commit/run references and explicit limitations.

Historical session logs and old estimates belong in the changelog and roadmap history; they are not current remaining-work estimates.
