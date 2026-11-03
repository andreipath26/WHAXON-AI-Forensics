# Engine V2 — source versus roadmap audit (2026-11-03)

**Audited main commit:** `781246b87575f6a7e5f7eea22e63aad789428894` (semantic provider migration, durable provenance and portfolio reconciliation).
**Authority:** master product roadmap §§0, 38, 49; `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md` §14; `docs/ENGINE_V2_ROADMAP_REQUIREMENTS.csv`.
**Method:** parallel read-only inspection of main Git tree, selected source, named test definitions, documentation and GitHub Actions check-runs. **No local tests, deployment, UI/browser acceptance or external-effect crash lab were executed for this audit.** GitHub check-runs for the exact inspected head were **9/9 successful**, including the three Python-version jobs and setup/headless jobs. A successful CI check is not universal acceptance.

## Three different metrics — never interchange them

- The pre-existing requirements index contains **75 source-level entries**, with **42/75 (56.0%)** linked to candidate implementation/document artifacts and **68/75 (90.7%)** linked to candidate tests, as recorded in `docs/ENGINE_V2_EVIDENCE_MATRIX.md`. Those are *mapping coverage*, not completed requirements; candidate tests may cover only a subset of a compound requirement.
- This report deliberately inspects **40 bounded and explicitly named implementation checkpoints** across E0–E6. **25/40 (62.5%) have a source-confirmed supporting implementation or documentation checkpoint**. This is an *observed-checkpoint coverage rate*, NOT percentage of an entire engine, weighted workload, remaining effort or production readiness. Selection is not exhaustive or equal-effort.
- **Formally accepted requirements: 0/75 recorded as accepted in the requirements CSV**. This measures *signed-off ledger entries*, not absence of implementation. Atomic, exact-SHA acceptance criteria have not been fully enumerated. The roadmap forbids portraying mapping or observed-checkpoint figures as Engine V2 completion percentages.

## Bounded checkpoint comparison

Symbols: **S** source/artifact and related test found; **G** gate incomplete or full requirement not demonstrated. Each row describes an independently scoped checkpoint, not necessarily the entire roadmap obligation.

| Phase | Observed checkpoints | Source-backed | Not demonstrated / remaining |
|---|---:|---:|---|
| E0 inventory | **2/5 (40.0%)** | S: dated architecture/baseline inventory exists; S: 75-entry requirement mapping/evidence index exists | G: fully current all-surface call graph; G: exhaustive tool/transport/UI control acceptance; G: reviewed migration/rollback/trust-anchor decision matrix |
| E1 security | **4/5 (80.0%)** | S: one-shot drain contract and regression; S: fail-closed IP/DNS scope tests; S: exact plan-bound approval tests; S: worker ownership/lease recovery tests | G: complete adversarial redirect/pivot/external DNS, audit-failure and exact candidate acceptance lab |
| E2 contracts | **4/5 (80.0%)** | S: versioned immutable DAG/task contracts; S: immutable manifest registry with deterministic resolution; S: durable scoped/revocable approval bindings; S: plan digest/integrity and compatibility tests | G: full canonical versioned domain contract set and backward-migration acceptance |
| E3 durability | **5/6 (83.3%)** | S: persisted mission/plan/task/attempt graph; S: atomic claims/leases/retries; S: mission budget/deadline/cost/rate limits; S: stop intent and uncertain outcome fencing; S: durable events and consumer cursors | G: real external-effect process-kill, multi-worker recovery, audit-store failure and outbox/independent integrity trust-anchor acceptance |
| E4 providers | **5/7 (71.4%)** | S: local catalog-adapter bridge; S: bound trusted provider router with provider selection; S: semantic operation aliases; S: read-only catalog/adapter portfolio audit; S: separately proposed evidence-driven follow-ups | G: exhaustive transport/catalog/CLI/UI parity and provider substitution acceptance; G: retirement of bypassable legacy autochains only after proven migration |
| E5 services | **3/6 (50.0%)** | S: durable acknowledged run-request queue; S: continuous headless request worker with stop controls; S: CLI/API/Core shared workflow surfaces | G: controlled real crash/restart with running external effect; G: daemon/systemd/container, backup/restore and supported platform acceptance; G: all service-client lifecycle and reconnect parity |
| E6 UI/release | **2/6 (33.3%)** | S: 22 UI-v2 routes/templates in the product; S: static source-control inventory with 793 controls | G: per-control real-service acceptance; G: visual/responsive/accessibility/offline parity; G: authorized seeded end-to-end solo lab; G: §38 G01–G10 release sign-off |
| **E0–E6 sampled total** | **25/40 (62.5%)** | Evidence of implementation, **not 62.5% completion** | No phase has full gate acceptance |
| E7–E9 | Excluded | Components or designs exist | Deferred P6–P8; do not penalize solo-v1.0 denominator |

### Concrete source and test references

- **E1** `tests/test_initialize_drain.py::test_initialize_drain_false_leaves_job_pending`; `tests/test_scope_failclosed.py::test_hostname_dns_failure_fails_closed`; `tests/test_providers.py::test_core_plan_bound_policy_requires_exact_unrevoked_approval`; `tests/test_worker.py::test_stale_reconciliation_fences_old_worker_token`.
- **E2** `src/whaxon/core/workflow.py`, `src/whaxon/core/capabilities.py`; `tests/test_workflow.py::test_plan_roundtrip_is_stable_and_digest_is_deterministic`, `test_workflow_approval_is_durable_exact_bound_and_revocable`; `tests/test_capabilities.py::test_capability_registry_persists_and_reloads_manifests`.
- **E3** `src/whaxon/core/scheduler.py`, `src/whaxon/core/store.py`, `src/whaxon/core/workflow_requests.py`; `tests/test_workflow.py::test_mission_wide_attempt_cap_applies_across_independent_plans`, `test_mission_rate_limit_serializes_claims_across_plans_and_restart`, `test_workflow_event_cursor_is_durable_monotone_and_plan_scoped`, `test_success_after_cancellation_is_recorded_uncertain_atomically`; `tests/test_workflow_run_requests.py::test_stale_run_is_uncertain_not_automatically_replayed`.
- **E4** `src/whaxon/core/providers.py`; `tests/test_providers.py::test_router_selects_explicit_provider_for_shared_semantic_capability`, `test_e4_portfolio_audit_reconciles_catalog_and_adapter_only`, `test_semantic_operation_and_legacy_alias_use_same_guarded_runner`; `tests/test_engine_v2_followups.py::test_e4_semantic_evidence_proposes_only_pinned_semantic_followup`.
- **E5** `src/whaxon/core/__init__.py`, `src/whaxon/core/workflow_requests.py`, `src/whaxon/interfaces/cli/workflow_cmd.py`, `src/whaxon/interfaces/web/server.py`; `tests/test_workflow_continuous_worker.py::test_headless_worker_polls_for_later_arrivals`; `tests/test_server_workflow_v2.py::test_api_202_is_persisted_before_worker_wakeup` is **not** defined there: the test actually lives in `tests/test_workflow_run_requests.py`. This cross-file distinction matters for exact traceability.
- **E6** `src/whaxon/interfaces/web/templates/ui_v2_*.html`, `docs/UI_CONTROL_INVENTORY.md`, `tests/test_web_ui_v2_*.py`. Static discovery does not establish every displayed control is wired.

## Documentation-versus-code discrepancies requiring reconciliation

1. **Stale evidence head:** `docs/ENGINE_V2_EVIDENCE_MATRIX.md` audits `c75c038...`, whereas inspected main is `781246b...`. Add verified source/test findings for subsequent commits without retroactively accepting previous requirements.
2. **E1 branch claim is historical:** `docs/ENGINE_V2_E1_ACCEPTANCE.md` says all E1 changes are on a working branch and instructs one future merge. Current main already contains many E1-related source changes and tests; acceptance remains OPEN, but the branch-only statement is not reliable current status.
3. **Old startup blocker retained in narrative:** `docs/STATE.md` lines describing `coverage/validate/retest/recon` as still draining unrelated jobs are superseded by its 2026-11-02 top note and the architecture continuation. Treat the fixed one-shot startup behavior as implemented, not an open code task; preserve wider E1 proof.
4. **E3/E5 under-described by dated snapshots:** actual main includes persisted run requests, continuous polling, mission-wide durable limits, cancellation fencing, event cursors, evidence cross-checks and local evidence seals. They close *implementation slices*, not process-kill and deployment acceptance.
5. **E4 snapshot lags main:** the existing dated E4 discussion still describes earlier unmerged/failed PRs; main now includes trusted alternative routing, bound provider identities, semantic operation aliases, a read-only portfolio audit and evidence-derived follow-up planning. Full transport parity is still not established.
6. **Audit integrity limitation:** `src/whaxon/core/store.py` explicitly describes its local SHA-256 evidence baseline as not a tamper-proof external audit signature. Do not label local digests an independent trust anchor.
7. **UI status must not be equated with working controls:** 793 statically inventoried controls across 22 templates, including unresolved/static examples, do not imply complete interaction, visual, accessibility or offline acceptance.

## Batches to turn observed-checkpoint coverage into genuine completion percentages

**Batch A (E0/E1, parallel):** Refresh all current callers/permission/transport inventory and acceptance traceability; adversarial startup/target/pivot/DNS/session/cancel/audit failure suites with exact negative assertions and network limitations.

**Batch B (E2/E3, parallel subject to stable interfaces):** Enumerate canonical schema/compatibility matrix; controlled subprocess hard-kill after external dispatch, two-worker contention, lost lease, injected audit/store failure, incomplete response and manual reconciliation; preserve uncertain effects without blind retries.

**Batch C (E4/E5, parallel):** Compare live catalog vs adapters vs normalized operations vs CLI/API/UI exposure and proofs; validate explicit provider substitution and migration parity; exercise headless service, foreground/daemon/container restart, backup/restore and clients reconnecting after restart.

**Batch D (E6, after service contracts):** Compare each visible supplied UI control against a real endpoint/permission/test; run browser visual/accessibility and controlled lab end-to-end/§38 release gates. Never redesign or invent functionality.

For **each atomic criterion**, store: requirement ID, scope/applicability, source path and symbol, test function plus exact assertion, observed command/environment/commit, result, limitation, reviewer and decision. Only then compute `accepted / applicable atomic criteria`. Review all new writes against current head to avoid overwriting concurrent work.

**Audit outcome:** code has advanced materially beyond several narrative status snapshots; 9/9 exact-head CI succeeded; **no credible full Engine V2 completion percentage is established yet**. This document supplies a reproducible checkpoint scope and explicit next evidence tasks rather than inventing a release percent.
