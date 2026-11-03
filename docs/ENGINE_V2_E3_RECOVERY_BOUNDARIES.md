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

## Scheduler dispatch gate classification

- `mark_workflow_dispatch_started()` can refuse dispatch due to cancellation **or** a newly expired deadline/tightened mission or plan budget. The scheduler now records a non-cancellation refusal as **blocked** rather than falsely labelling it **cancelled**. A true durable cancellation remains **cancelled**. No refused task invokes a provider.
- Parameterized scheduler tests tighten the plan deadline, exhaust mission cost permission and request cancellation *after the second policy check but before external dispatch*. These verify exact terminal status and absence of `dispatch_started` evidence.

## Controlled external network side-effect crash validation

- `tests/test_engine_v2_e3_external_effect_crash.py` uses a bound 127.0.0.1 HTTP server, not a simulated local-file-only callback. A child process sends a real POST, receives HTTP 204, and is killed before reporting an attempt result. Stale lease reconciliation must mark the external outcome **uncertain**, refuse retry, keep readiness unaccepted, and leave the receiver's side effect count at exactly one.
- A second test has the HTTP receiver accept the POST and deliberately disconnect without a response. The scheduler must record an **uncertain** post-dispatch exception; subsequent invocations must not retry.
- These tests are **controlled local-only network effects**, not proof of behavior with production scanners, live pivoting, remote servers or a verified independent trust anchor. They are designed to execute in the existing exact-head Python CI matrix.

## Completion-time plan identity and worker uncertainty

- The terminal write transaction now checks both the cancellation state **and the original bound plan digest**. A changed plan digest cannot produce `completed`, `incomplete` or `failed` final status under the obsolete intent. The run is `uncertain`, its original digest is preserved, and an audit event is committed atomically.
- A worker explicitly reporting `uncertain` also produces exactly one transactional, bounded reason-coded `workflow_run_uncertain` event. Raw provider error text is not copied into the audit detail. Audit insertion failure rolls back the queue transition.
- Missing source plans remain uncertain but cannot write a plan-scoped event to a nonexistent plan; the queue row retains the failure reason. This is an explicit operational limitation, not proof of independent auditing.
