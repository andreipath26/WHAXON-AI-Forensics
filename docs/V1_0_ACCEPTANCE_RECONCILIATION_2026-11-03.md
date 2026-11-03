# WHAXON v1.0 — bounded requirement acceptance reconciliation (2026-11-03)

**Decision:** accept four *bounded* source-level requirements, not four entire phases or any release gate.
**Source baseline:** [main at `f0b25d3629d776b433f72c83db679bb41313c812`](https://github.com/andreipath26/WHAXON-AI-Forensics/commit/f0b25d3629d776b433f72c83db679bb41313c812).
**Exact-SHA CI:** [run #41642767222](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41642767222): all 10 checks successful (Python 3.11, 3.12, 3.13; E1 regression job; Linux headless; Windows/macOS/Ubuntu setup; curated apt and Homebrew smokes).
**Evidence provenance:** GitHub source review, named test assertions and exact-source CI. No independent local execution, real-host service recovery, live scanner, visual/accessibility or end-to-end lab acceptance was performed in this reconciliation.
**Decision authority:** user-requested acceptance of already-proven behavior, with conservative boundaries.
**Ledger:** `ENGINE_V2_ROADMAP_REQUIREMENTS.csv`.

## Accepted requirements

| ID | Exact demonstrated behavior | Assertion/evidence | Limit |
|---|---|---|---|
| P0-04 | Only packaged catalog seed remains tracked; fresh workspace seeds from package and existing operator catalogs are preserved | `src/whaxon/data/tools.json`; missing `data/tools.json`; `tests/test_catalog_bootstrap.py::test_new_workspace_bootstraps_packaged_catalog_outside_checkout`; `::test_existing_operator_catalog_survives_startup_unchanged` | Tool *catalog presence* is not tool authorization or compatibility |
| P1-01 | `coverage`, `validate`, `retest`, `recon` and `run` initialize with `drain=False`, while `run` retains its own follow-up drain | `src/whaxon/interfaces/cli/{coverage_cmd,validate_cmd,retest_cmd,recon_cmd,run_cmd}.py`; `tests/test_cli_initialization_isolation.py::test_one_shot_preserves_unrelated_pending_jobs` (11 parameterized outcomes); `tests/test_run_cmd.py::test_run_automatically_drains_jobs_queued_by_automator` | Does not close other authorization, DNS, pivot or audit requirements |
| P2-07 | V2 catalog adapter provider is deliberately restricted to catalog defaults and registered readiness; unsupported providers are reported without enabling them | `src/whaxon/core/providers.py`; `tests/test_providers.py::test_catalog_adapter_provider_rejects_dynamic_cli_arguments`; `::test_provider_does_not_register_exploit_or_credential_tools`; `::test_catalog_portfolio_reconciles_unsupported_tools_without_registering` | No claim that providers are lab-validated or all E4 migration complete |
| P4-01 | The 22 production template/routes and preserved supplied reference design inventory have corresponding code/tests | 22 `ui_v2_*.html`, 27 `code.html` plus 27 `screen.png`; `tests/test_web_ui_v2_route_matrix.py::test_every_canonical_ui_route_renders`; `tests/test_web_ui_v2_control_inventory.py` | Does not accept all UI controls, backend wiring, visual fidelity, accessibility or offline assets |

All assertions are anchored to the source baseline and its successful CI; relevant test bodies were reviewed. This is a **bounded acceptance** decision. Any material later changes must be revalidated on the release candidate.

## Count and scope

- **4/75 ACCEPTED** (5.33%) as narrowly defined above.
- **71/75 NOT_ACCEPTED** remain in the ledger.
- **54 solo-v1-applicable** entries (P0–P5, E0–E6, G01–G10): **4 accepted, 50 open**.
- **21 deferred** entries (P6–P8, E7–E9) remain NOT_ACCEPTED; they are outside the solo-v1 release gate, not failed release requirements.
- **G01–G10: 0/10 closed.** G08 has exact-main CI success but still requires full exact-candidate browser, supported-platform acceptance and documented skips; current `0.11.16` Beta is not the approved v1 candidate.
- **E0–E9: 0/10 whole-engine gates formally closed**; no whole phase is inferred from bounded acceptance.

## Stale statement correction

The old baseline narrative in `STATE.md` and `V1_0_BASELINE_AND_ACCEPTANCE_REGISTER.md` describing default `drain=True` for four one-shot commands is historical, overridden by checked source and tests. Old E1 branch-only acceptance notes and older check-run totals are not the current main status. The preexisting 25/40 sampled-source-checkpoint figure is a different metric; it is not the 75-row acceptance figure.

## Still open before G01–G10 closure

Exhaustive cross-surface capability mapping; adversarial scope/external egress and audit-failure checks; validation/evidence ground truth; real worker/service restart and full backup/restore; 793-control runtime/visual/accessibility check; controlled solo-lab chain; supported installation modes; candidate-only CI; version/tag/index publication and explicit release decision.

**No product source code, visual assets or legacy designs were changed in this reconciliation.**
