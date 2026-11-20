# Engine V2 E1/E5 — Run-queue lease credential isolation

The durable run queue uses a private `lease_token` to fence worker heartbeat and
completion operations. This credential must not be returned to callers that
submit workflow execution requests.

Previously, `WorkflowRunQueue.get()` redacted the token, while
`WorkflowRunQueue.enqueue()` returned a raw row. Submitting the same plan
again while a worker was running returned the existing raw row, including its
active fencing token.

This batch introduces a shared `_public_record()` transformation and applies
it to **new enqueue**, **duplicate queued/running/uncertain enqueue** and
**request status lookup**. Only `claim()` retains the raw lease credential for
the worker that owns it. Heartbeat and finish still require the correct token,
and no queued or uncertain job is automatically replayed.

Regression coverage in `tests/test_engine_v2_e1_queue_lease_privacy.py`
checks fresh and duplicate submissions, an actively running private worker,
uncertain requests, Core/Web API response paths, and continued fencing.

**Acceptance boundary:** This is a concrete credential-confidentiality fix,
not complete authentication isolation, transport isolation, queue-operation
authorization or E1/E5 acceptance. The API's existing authentication and policy
configuration still require separate security verification.
