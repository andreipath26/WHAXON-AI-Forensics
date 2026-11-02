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

The master roadmap §47 records CI run [#41313223574](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41313223574) on 2026-11-01 as passing Ruff, mypy, 1,322 tests (14 skipped), and wheel/sdist metadata validation on Python 3.11, 3.12 and 3.13. It also records clean-wheel diagnostics and selected Ubuntu/macOS/Windows setup and scanner smoke checks.

This is a specific recorded CI result, **not a claim that every later commit or the current HEAD has passed CI**. Check Actions for the exact candidate commit before release.

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

## 5. Known operational limitations

- Scope checks are application-level preflight controls, not a network firewall or connection-time DNS pin. External tools may follow redirects or make secondary requests. Enforce egress restrictions independently for real engagements.
- Dependency installation is allowlisted and approval-gated, but completed package changes are not generally rolled back. Audit-chain limitations and the absence of an independently stored trust anchor are documented in the installation design.
- Registered catalog tools are not automatically installed, licensed, platform-compatible or fully tested. Check tool readiness and adapter support individually.
- AI output is a proposal, not authorization, execution evidence or a verification verdict.

## 6. How to resume work

1. Read the master roadmap from §0 and the OPEN release checklist in §38.
2. Check current `main`, exact CI status and the latest UI/Engine v2 acceptance records.
3. Work on the highest-priority unmet dependency; do not restart completed work from historical session notes.
4. Update this file only when new evidence exists, including commit/run references and explicit limitations.

Historical session logs and old estimates belong in the changelog and roadmap history; they are not current remaining-work estimates.
