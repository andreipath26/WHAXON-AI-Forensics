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
