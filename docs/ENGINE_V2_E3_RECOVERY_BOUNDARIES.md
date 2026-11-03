# Engine V2 E3 — Durable recovery boundary hardening (2026-11-03)

**Scope:** One implementation batch, no scheduler/provider/transport redesign.

- Duplicate run-request submissions now compare the existing persisted request's plan digest with the current source plan digest. A changed digest refuses the duplicate submission and keeps the historical queue record intact for safe claim-time quarantine/reconciliation. This check applies to queued, running and uncertain active requests; it does not grant authority or rebind any plan.
- Task-attempt stale-lease recovery rejects boolean, nonfinite and invalid timeout thresholds **before** acquiring the reconciliation transaction. A NaN threshold must not silently make stale recovery a no-op.
- Focused tests in `tests/test_engine_v2_e3_recovery_boundaries.py` cover queued and running plan drift, preserved worker-token privacy, existing claim-time quarantine, invalid-threshold no-mutation and valid fresh-lease preservation.

**Limits:** These are concrete safety hardenings, not proof of real scanner-effect cancellation, complete external-effect reconciliation, independent audit integrity, outbox delivery or the full E3 acceptance gate. CI execution results belong to the exact PR/head revision and must not be assumed from source inspection.

## Coordinated E3 atomicity/recovery batch

- **Cancellation-to-completion fence:** run-request terminal status and plan cancellation are serialized in the same SQLite write transaction. Any worker completion after a cancellation is recorded as `uncertain` with one durable `workflow_run_uncertain` event, never as success. Missing source plan cannot certify a completed run.
- **Audit fail-closed:** an audit insert failure rolls back the run-request status transition. Regression tests use real SQLite `RAISE(ABORT)` triggers to inject write failures at cancellation completion, stale run recovery, claim-time changed-digest quarantine, and task-attempt recovery. These are local database atomicity checks, **not** an externally anchored audit delivery guarantee.
- **Bounded stale reconciliation:** task and run queue recovery each operate on at most 128 stale rows per transaction, preserving predictable writer lock time. Remaining rows require further calls/poll cycles; the service already repeats its queue reconciliation.
- **Integration contract:** no change to automatic retry of uncertain external effects, no authority escalation or provider redesign. Full E3 acceptance still requires real external-effect crash/side-effect validation, independent trust anchor/outbox delivery semantics, whole-lifecycle worker deployment and exact-head CI evidence.
