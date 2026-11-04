# Engine V2 E5 — whole-phase engineering acceptance register

**Status:** OPEN — implementation and exact-head phase acceptance not yet established.
**Authority:** master roadmap P2/P3, G05/G07; Engine V2 crosswalk §14.1, §14.2, §14.7–14.8 and binding execution rules; engineering execution model.
**Integration branch:** `engine-v2/e5-whole-phase-integration` (one phase, one PR, one final merge).

## Verified baseline / reuse, not acceptance

- Existing Core durable run-request enqueue, claim, stop-aware drain, continuous worker, fenced leases and conservative uncertain-effect reconciliation.
- Shared queue summary in Core, CLI and API; summary explicitly does not verify worker liveness.
- Packaged web and worker systemd units, restricted state directory, core/store readiness, SQLite snapshot regression and stale-worker no-replay tests.
- E3 merged on `main` as `ad192b931a1480eaad76d3a11735cbe1d85b4818`; retain its audit/outbox and durability contracts. Existing unit tests and prior CI are not proof of full E5.

## Whole-phase dependency graph and bounded workstreams

| Stream | Owner boundary | Dependencies | Engineering acceptance |
|---|---|---|---|
| S1 — shared application contract | Core mission/run/approval/progress/evidence service and versioned response semantics | E2/E3 durable state, E4 provider policy | CLI/API/headless invoke the same persisted service authority; no browser-owned execution or second scheduler; compatibility tests |
| S2 — worker lifecycle | Core worker, queue, stop/reconciliation and scheduler integration | S1 stable contracts; E3 fencing | Concurrent claims, SIGTERM/drain, heartbeat/lease loss, crash injection, no duplicate external effect or unsafe automatic replay |
| S3 — client reconnect and observability | API/CLI/UI integration through existing service endpoints | S1 persisted identifiers, S2 state | Disconnect/reconnect/restart can inspect truthful persisted status, progress, errors and reconciliation; no lease credential leakage |
| S4 — deployment and readiness | Headless entry points, health, packaging, service templates, secrets/configuration | S1–S3 behavior | Clean-wheel/sdist, CLI and worker unit parity, optional dependencies degrade independently, readiness never asserts worker liveness without proof |
| S5 — independent adversarial verification | Tests and acceptance register; no conflicting production source ownership | S1–S4 integrated revisions | Cross-process races, cancellation, failed audit/store, stale worker, corrupted state, replay denial, authorization/identity and migration regression; exact-head supported CI |

One integration owner coordinates changes to shared Core and service contracts. Workstreams may proceed in parallel only after their interfaces and ownership are stable. Do not merge partial work as a separate E5 PR.

## Engineering gates (all OPEN until evidenced)

- **E5-A:** Complete actual caller/endpoint/worker/service inventory and contract migration, including legacy paths and rollback; no second execution authority.
- **E5-B:** Durable mission/run/approval/progress/evidence/verification service parity across CLI/API/web/headless for supported operations.
- **E5-C:** Durable client disconnect/reconnect and process restart with truthful status, cancellation and no unapproved side effects.
- **E5-D:** Multi-worker claims, fencing, shutdown, lease expiry, uncertain-effect reconciliation and adversarial recovery tests.
- **E5-E:** Headless lifecycle, health/readiness, secret/path permissions, supported package/service modes and failure behavior verified at engineering-test level.
- **E5-F:** Exact-final-head lint, types, Python 3.11–3.13, cross-platform packaging, security and integration CI with recorded SHA, run links and limitations.
- **E5-G:** Explicit engineering review, rollback/migration plan, reconciled crosswalk/roadmap and controlled phase freeze decision.

## Final integrated V2 deployment gates — DEFERRED, NOT PASSED

Authorized real-scanner laboratory, production-like host/service/container and multi-worker recovery, full backup/restore of evidence/configuration, independent external audit anchor, and complete cross-client end-to-end deployment/operator sign-off are mandatory at the final Engine V2 deployment gate under the 2026-11-03 operator decision. They are **not** waived and no phase freeze implies production readiness.

**Next implementation target:** complete S1/S2/S3 source-level contract inventory and build coordinated functional and adversarial changes, not standalone documentation or superficial test-count milestones.


### Shared reconnect contract — engineering implementation in progress

The Core `workflow_run_snapshot(request_id)` contract returns the persisted
request and its durable workflow progress with explicit
`worker_liveness_verified=false` and `automatic_uncertain_replay=false`.
The web route `GET /api/v2/workflow-runs/<request_id>/snapshot` and
`whaxon plan run-snapshot --id <request_id>` consume this same Core
contract. A request is not proof of execution, and the read models are
individually persisted views, not an atomic cross-table snapshot.

Adversarial tests cover restart/reconnect, duplicate-submission fencing,
lease-token secrecy, bounded stale recovery, and durable-health fail-closed
behavior. **All test results and E5 gates remain unverified until exact-head
CI and applicable integration evidence are recorded.** No production or
deployment acceptance is claimed.


### Accepted-intent reconnect discovery

A successful `POST /api/v2/workflows/<plan_id>/run` returns HTTP 202,
`run_request_id`, `run_request_url`, `run_snapshot_url`, and the existing
`durable_progress_url`. The snapshot URL derives from the persisted request
identity and remains usable after a different web process starts against the
same data directory. Duplicate active submissions with identical bounds reuse
the same durable request identity. A 202 is **not** execution success.


### Bounded lost-lease reconciliation and stop behavior

The headless drain now repeats the existing 128-record transactional
stale-lease reconciliation until no stale leases remain before admitting
new work. A stop signal exits between bounded passes. This is recovery
bookkeeping only: no uncertain request is automatically re-executed.
The worker still requires exact-head CI and multi-process adversarial
acceptance before E5-D can close.


### Cancellation and lease-loss reconnect tests

The cross-process API acceptance suite now exercises queued cancellation,
durable cancellation after Core restart, stale-worker reconciliation, and
credential-free inspection of an uncertain request. These tests require
execution and exact-head CI evidence; their presence alone does not close
E5-C or E5-D.


### Request-identity cancellation

The Core `cancel_workflow_run_request(request_id)` operation and the
API `POST /api/v2/workflow-runs/<request_id>/cancel` and CLI
`plan cancel-request --id <request_id>` share the existing persisted
plan cancellation barrier. Unknown requests fail closed. Running external
effects are never represented as stopped by this acknowledgement. This
cancels the associated plan, not an isolated task.


### Adversarial concurrency coverage

Additional tests race 24 independent HTTP submissions against one durable
SQLite request and race request-identity cancellation against a worker claim.
The allowed cancellation/claim race outcomes are either cancellation before
claim or a previously claimed run with a durable stop barrier; neither permits
a second claim. These are engineering tests pending exact-head CI, not
production multi-host proof.


### Poisoned backlog progress in one-shot drains

The Core drain now retries a bounded number of claim passes when a
64-record poison quarantine yields no claim but queued intents remain.
This prevents one-shot headless/CLI drains from mistaking a bounded
quarantine yield for an empty queue. Retries are capped at 16 passes
per requested run to prevent starvation from an unbounded producer.
No uncertain intent is automatically replayed.

### E5 integration evidence update — backup and paired-container verification

The active E5 PR #124 now includes a separated `docker-compose.e5.yml`
web/worker deployment candidate, non-root state-volume preparation, and CI
that starts both containers, checks Core readiness, observes persisted state
across a worker restart, and requires an inert blocked workflow to be consumed
without launching an external scanner. A paired service smoke does not replace
real supported-host operation or prove production worker liveness.

An offline state snapshot module `src/whaxon/core/state_snapshot.py` and
`tests/test_engine_v2_e5_state_snapshot.py` cover SQLite plus scope/evidence
file preservation, per-file digest verification, symlink rejection, tamper
detection and no-overwrite restore. Services must be stopped by the operator;
the manifest does not authenticate itself and external evidence anchoring,
backup rotation, off-host retention and host-level disaster recovery remain
unaccepted. All additions are **candidates pending exact-head CI** and the
final E5-A through E5-G review; no deployment or phase sign-off is asserted.

### Durable run submission parity — implementation candidate

The E5 integration branch adds CLI `plan submit-run` using the same Core
`enqueue_workflow_run()` transaction and limits as API
`POST /api/v2/workflows/<plan_id>/run`. A cross-client test verifies that
identical CLI/API submissions deduplicate to one durable request and changed
limits fail closed, without starting external effects. This is *bounded run
submission parity*, not evidence that all legacy CLI direct execution paths
have migrated. E5-A and E5-B remain open pending exact-head CI and full
caller inventory.

## Caller-inventory and rollback checkpoint

Read [E5 caller and execution-authority inventory](ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md) before any claim of E5-A/G completion. It distinguishes the sole supervised V2 queue worker from preserved legacy CLI/web/AI tool execution and specifies fail-closed rollback and full-state recovery. As of this document update, **E5-A through E5-G remain OPEN** pending exact-head CI, remaining migration decisions and operator acceptance.

### Two independent worker processes — adversarial claim test

`tests/test_engine_v2_e5_process_claims.py` now starts two independent
Python processes against the same persisted SQLite run request, waits for
both to be ready, releases them together and requires only one claim/blocked
workflow result. This strengthens E5-D beyond thread-only tests. It uses an
unsupported fixture capability, **never** an actual scanner or target. The
whole gate remains OPEN until exact-head CI and wider failure injection,
restart and recovery evidence are accepted.

### E5 offline recovery verification expansion (pending exact-head CI)

A full-state restore regression now preserves a previously claimed request,
forces an expired lease after restore, and requires the outcome to become
`uncertain`. The restored worker cannot reclaim or mark that external effect
completed using the old fencing token. Scope and binary evidence are checked
alongside the same persisted run identity. Separate tests reject missing and
unexpected snapshot files. Evidence copies use bounded-memory streaming.
This does **not** simulate an actual power loss, prove host quiescence, establish
external evidence authenticity, or close E5-D/E5-E without the required
real-service recovery acceptance.

## Engineering exit review — 2026-11-04, E5 PR #124

**Decision state:** ENGINEERING ACCEPTANCE CANDIDATE; **NOT YET FROZEN OR MERGED**.
The implementation must pass exact-final-commit CI, and the reviewer must record
the complete SHA, check results and explicit decision before phase freeze.
Production release and final integrated Engine V2 deployment acceptance remain
separate, open milestones under the roadmap's E0–E9 phase-freeze policy.

### Whole-phase evidence and remaining boundaries

| Gate | Source and evidence | Engineering assessment |
|---|---|---|
| E5-A — shared execution authority | `src/whaxon/interfaces/web/server.py` `WHAXON_V2_EXTERNAL_WORKER=1` prevents web-owned V2 draining; `Core.enqueue_workflow_run`, `WorkflowRunQueue.claim`, `whaxon workflow plan submit-run`; `tests/test_workflow_run_requests.py`; `docs/ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md`; Docker CI stops worker, tests HTTP 202 remains queued and starts worker separately | One durable **V2** queue authority in paired deployment is implemented. **Legacy direct CLI/web/AI execution has NOT migrated**. It remains an explicitly enumerated P2/E4 cross-phase and final integration obligation; do not claim platform-wide single authority |
| E5-B — shared service model | Core methods for mission, approval, persisted plan/run/progress/evidence/audit/readiness; CLI `workflow_cmd.py` and web `server.py`; `tests/test_workflow_cli.py`, `tests/test_server_workflow_v2.py`, cross-client request parity in `tests/test_workflow_run_requests.py` | Supported V2 requests share the persisted Core authority; complete legacy frontend parity, all advertised features and independent verification are NOT inferred |
| E5-C — reconnect and cancellation | `test_e5_api_client_reconnect_after_server_restart_keeps_durable_identity`, `test_e5_run_snapshot_reconnect_and_lease_secrecy`, `test_e5_cancelled_intent_stays_cancelled_across_api_restart`; paired Docker and systemd smoke | Durable identity and bounded stop semantics supported; HTTP 202 never implies execution success |
| E5-D — adversarial worker safety | `tests/test_engine_v2_e5_process_claims.py` starts two independent Python processes; `tests/test_workflow_continuous_worker.py` kills a child worker; `tests/test_engine_v2_e5_queue_head_recovery.py` exercises poisoned heads and stale leases; `tests/test_engine_v2_e5_state_snapshot.py` checks restored stale claims never replay | Bounded claim, fencing and uncertain-effect tests; no exactly-once guarantee or production external-effect proof |
| E5-E — deployment candidate | `whaxon.service`, `whaxon-workflow-worker.service`, `docker-compose.e5.yml`, `Dockerfile`, `.dockerignore`, `docs/deployment.md`; CI paired-container job and actual Ubuntu systemd-host job use installed wheel and restore offline state | Supported engineering deployment smoke on ephemeral CI host/container. Network/TLS/secrets, production host, independent audit witness and real disaster-recovery acceptance remain OPEN |
| E5-F — exact-head validation | `.github/workflows/ci.yml` Python 3.11–3.13, Ruff, mypy, packaging, headless, cross-platform setup, E1 security, Docker, systemd. [11/11 passing on `11190f737`](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41814000683). New host test passed on `3e5f5fb` but full matrix had a timing-race failure in `test_killed_worker_request_requires_reconciliation_before_replay`; test updated to wait for complete child output on `7c6ba849` | **OPEN until all checks pass on exact final PR HEAD**, after this documentation update |
| E5-G — review and controlled freeze | This register, caller inventory/rollback, offline recovery runbook and limitations; master roadmap and `docs/ENGINEERING_EXECUTION_MODEL.md` remain binding | Await exact-head proof and an explicit dated engineering-review/freeze record. No implied sign-off |

### Explicit release deferrals, never waived

No unapproved real scanner or target execution, no externally retained immutable audit witness in a controlled enterprise environment, no independent production host crash/failover and network service recovery, and no end-to-end parity claim for retained legacy execution surfaces. Those are **not passed**. The engineering smoke is limited to inert unsupported fixture workflows and isolated ephemeral CI runners.

**Merge rule:** mark this PR ready and merge only after documented E5 engineering gates are passed for the supported V2 service scope and exact-final-head CI is green. Even then, E5 engineering freeze **does not authorize production deployment** or close the master roadmap's G01–G10 gates. Keep residual legacy migration assigned to E4/P2 and integrated validation to the final Engine V2 release gate.
