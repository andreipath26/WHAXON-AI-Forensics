# E3 — Auditing uncertain durable run requests

Engine V2 run requests are persisted independently from task-attempt records.
When an unclaimed request's persisted plan digest changes, the queue
conservatively transitions it to `uncertain`. When a running request's
heartbeat expires or is missing, reconciliation likewise marks it `uncertain`
rather than replaying its possible external effects.

This batch adds a **same-transaction** `workflow_run_uncertain` event to the
existing `workflow_events` feed for each such transition where the plan is
still present. The event carries only the run request ID and one bounded
reason (`plan_digest_changed` or `worker_lease_lost`); it does **not**
expose lease tokens, worker identifiers, task inputs, or other secrets.
Reconciliation is idempotent: a second inspection of an already uncertain
request does not write another event.

If a workflow plan has been deleted, its queue row may still be quarantined,
but no now-orphaned plan event is fabricated.

These events improve persistence and operator traceability; they are **not**
a tamper-proof independent trust anchor, verified external-effect outcome,
or complete transactional outbox implementation. The E3/P2 and G04/G05
crash, audit-failure, recovery and release acceptance gates remain open.
