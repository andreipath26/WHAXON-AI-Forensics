# Engine V2 E3 — Durable recovery boundary hardening (2026-11-03)

**Scope:** One implementation batch, no scheduler/provider/transport redesign.

- Duplicate run-request submissions now compare the existing persisted request's plan digest with the current source plan digest. A changed digest refuses the duplicate submission and keeps the historical queue record intact for safe claim-time quarantine/reconciliation. This check applies to queued, running and uncertain active requests; it does not grant authority or rebind any plan.
- Task-attempt stale-lease recovery rejects boolean, nonfinite and invalid timeout thresholds **before** acquiring the reconciliation transaction. A NaN threshold must not silently make stale recovery a no-op.
- Focused tests in `tests/test_engine_v2_e3_recovery_boundaries.py` cover queued and running plan drift, preserved worker-token privacy, existing claim-time quarantine, invalid-threshold no-mutation and valid fresh-lease preservation.

**Limits:** These are concrete safety hardenings, not proof of real scanner-effect cancellation, complete external-effect reconciliation, independent audit integrity, outbox delivery or the full E3 acceptance gate. CI execution results belong to the exact PR/head revision and must not be assumed from source inspection.

## Coordinated E3 atomicity/recovery batch

- **Cancellation-to-completion fence:** run-request terminal status and plan cancellation are serialized in the same SQLite write transaction. Any worker completion after a cancellation is recorded as `uncertain` with one durable `workflow_run_uncertain` event, never as success. Missing source plan cannot certify a completed run.
- **Audit fail-closed:** an audit insert failure rolls back the run-request status transition. Regression tests use real SQLite `RAISE(ABORT)` triggers to inject write failures at cancellation completion, stale run recovery, claim-time changed-digest quarantine, and task-attempt recovery. These are local database atomicity checks, **not** an externally anchored audit delivery guarantee.
- **Bounded recovery pages:** stale durable run-request reconciliation processes at most 128 requests per transaction; continuous workers revisit the remaining backlog on later polls. Task-attempt recovery now also processes at most 128 stale attempts per transaction. `Core.initialize()` repeats those bounded pages until no stale attempts remain, before reporting the Core ready. The regression creates 129 stale attempts and verifies the startup drain processes `128 + 1 + 0`; a single page call is intentionally not a complete sweep.
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

## Audit semantic integrity and readiness

- The internal, non-cryptographic workflow audit consistency check now rejects terminal event names that disagree with their attempt's persisted terminal status, terminal events attached to still-running attempts, duplicate dispatch-intent events and events referencing unknown attempt IDs. All findings fail readiness closed. This does not independently prove that an attacker did not modify **both** the event table and attempt table.
- The readiness flag `requires_manual_reconciliation` now reports whether an in-flight or uncertain attempt actually needs manual reconciliation, rather than returning true for every ordinary healthy pre-dispatch attempt. In-flight effects after dispatch remain explicitly in need of reconciliation until confirmed.
- Regressions mutate real SQLite rows (not fake mocks), then check both audit diagnostics and success readiness.

## Externally anchorable read-only lifecycle digest

- `JobStore.get_workflow_audit_snapshot(plan_id)` hashes the versioned plan identity, ordered durable task/attempt state and persisted event stream from one SQLite read transaction. It exposes only the SHA-256 digest and counts, not raw event details, inputs or stored results.
- `verify_workflow_audit_snapshot(plan_id, expected_digest)` compares a caller-retained reference with the current snapshot. A separate operator-controlled, immutable or independently protected location must retain **the original digest** (and associated plan, SHA, environment and observation time) before this protects against rewriting the local database. Tests mutate event, task and attempt records and detect mismatch across restarts.
- **Not a shipped independent trust anchor.** This API cannot prove its own previous digest was retained externally; it is no substitute for a signed/anchored audit log or an approved operational retention/deletion procedure. The snapshot does not cover external provider-side effects, legacy jobs outside this workflow, or binary evidence files. `independent_anchor_verified` remains `False`.

## Operator-facing shared CLI/Core service

- `Core.workflow_audit_snapshot()` and `Core.verify_workflow_audit_snapshot()` surface the store's read-only versioned lifecycle digest. `whaxon workflow plan audit-snapshot --id ...` prints the digest; `audit-verify --id ... --expected-digest ...` returns nonzero on mismatch.
- The CLI explicitly emits `independent_anchor_verified: false` even on a matching caller-provided digest. Operator-managed independent retention and a recorded witness are mandatory for external trust assurance. See `docs/ENGINE_V2_E3_PHASE_ACCEPTANCE.md`.

## At-least-once lifecycle outbox delivery

- `WorkflowEventOutbox.deliver()` and shared `Core.deliver_workflow_outbox_events()` deliver a bounded page of persisted events to a caller-provided trusted transport callback, checkpointing its consumer cursor **only after** each callback returns successfully. A failed callback never advances its event checkpoint. Each consumer has an independently durable cursor across restarts.
- A simulated downstream effect followed by an exception leaves the event deliberately unacknowledged and proves duplicate delivery on retry; receivers **must** deduplicate by `(plan_id, event.id)`. An internally inconsistent workflow audit refuses publication. The service makes no exactly-once claims and does not configure or authenticate an external transport by itself.
- Consumer cursors advance only when acknowledging the next persisted event for that plan. An out-of-order acknowledgement is rejected transactionally, preventing concurrent publishers or direct cursor callers from advancing past an unacknowledged earlier event. Regression: `test_consumer_checkpoint_cannot_skip_an_unacknowledged_event`.
- Remaining E3 acceptance requires an actual independently supervised publisher process/transport, authenticated downstream sink, external receipt evidence, fault/restart tests and external protected audit anchor.

- The current synchronous outbox contract refuses an awaitable/coroutine return (with no acknowledgement); otherwise accidentally passing an async callback could checkpoint an event before the coroutine ever executes. An asynchronous transport needs a separately awaited publisher boundary and its own acceptance tests.

## Fail-closed provider-result recovery validation

- Before an uncertain attempt can be recovered from a terminal V2-owned provider job, persisted finding rows are checked for nonnegative sequence identities, string-valued finding fields and JSON-object `data`/`enrichment` payloads. Malformed rows leave the attempt uncertain and unsealed; recovery never repairs or rewrites provider output.
- `tests/test_engine_v2_e3_provider_job_recovery.py` corrupts both finding payload forms in SQLite and verifies the recovery path refuses them while preserving the uncertain attempt.
- This validates the shape of persisted finding rows, not provider-specific semantic completeness, binary-artifact integrity, production scanner behavior or an independent audit anchor. Those E3 boundaries remain open.


## Provider completion snapshot before uncertain recovery — 2026-11-23

- A V2-owned provider job records a versioned SHA-256 snapshot of its persisted job, output lines, findings, coverage, and evidence metadata only after the provider has parsed and persisted its complete output. The generic `JobFinished` event is not the seal boundary because ToolRunner emits findings afterward.
- Lost-ack recovery and ordinary success terminalization require the matching completion snapshot. Added, removed, or changed persisted output after that final seal leaves the attempt uncertain for manual reconciliation.
- Result-only recovery requires a positive capability allowlist and a plan-pinned provider ID, version, and manifest fingerprint. It verifies the registered manifest's impact, permissions and declared effects, and refuses file-backed evidence whose bytes are outside the database digest.
- Regressions cover findings persisted after `JobFinished` but before final sealing, output mutation after sealing, unpinned and alternate provider identities, nonzero durable job exit under a caller-reported success, and file-backed evidence refusal.
- This is a local database drift check, not an independent trust anchor; it does not validate provider-specific semantic completeness, evidence-file contents, or production scanner effects. Those E3 and G05 obligations remain open.


## Capability-level effect recovery policy — 2026-11-23

- Result-only recovery is restricted to an explicit positive allowlist of catalog, semantic-operation, and first-party observation capabilities. Verification/retest probes, SQLMap, the Samba user-map initial-access provider, stale aliases and unknown tool-prefixed IDs require operator reconciliation.
- Every provider dispatcher records the exact capability, provider ID, provider version, and manifest fingerprint before its external effect. Recovery rechecks that immutable registration, the task permission/impact contract, declared side effects, and any provider identity pinned into plan metadata.
- Both ordinary success terminalization and lost-ack recovery compare the persisted output with the completion-time snapshot. A post-completion database change cannot be sealed as success. Lost-ack recovery also refuses provider evidence that points to an external file because file bytes are not covered by the database digest.
- Regressions exercise denied capabilities, changed output at both success and recovery boundaries, file-backed evidence refusal, and a registered passive-DNS provider as the first-party recovery example. The stale `recon.http` alias is not registered on this branch and is deliberately excluded.
- These are local database and declared-contract checks, not proof that a production provider's external effects were independently witnessed. G05 real-effect and production qualification remain open.
