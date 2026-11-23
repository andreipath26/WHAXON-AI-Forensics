# Engine V2 E5 — caller and execution-authority inventory with rollback controls

**Status:** evidence-backed inventory, **not** E5 engineering phase acceptance.
**Inspected implementation:** E5 PR #124 head `fe628013bf04309f262224f62179ff9c3438c1a2`.
**Governing rules:** master roadmap P2/P3, G05/G07; E5-A/E5-B/E5-C/E5-G; architecture crosswalk §14.7; engineering execution model.

## Observed execution paths and ownership

| Surface | Source/contract | Durable V2 authority | Current limit |
|---|---|---|---|
| V2 run API | `src/whaxon/interfaces/web/server.py`: `POST /api/v2/workflows/<plan_id>/run` | `Core.enqueue_workflow_run` commits before HTTP 202 | In unsupervised legacy web mode, best-effort process-local wakeup remains; HTTP 202 is not execution success |
| V2 status/reconnect | `GET /api/v2/workflow-runs/<id>`, `/snapshot`, `/summary`, `POST /cancel` | `Core.workflow_run_request`, `workflow_run_snapshot`, `workflow_run_queue_summary`, `cancel_workflow_run_request` | Run snapshot reads request and task progress in one SQLite read transaction; worker liveness is **not verified** |
| V2 CLI request | `src/whaxon/interfaces/cli/workflow_cmd.py`: `plan submit-run` | Same Core enqueue and bounded identity as API | No direct execution claim or task success on submission |
| V2 CLI inspection | `plan queue-summary`, `run-request`, `run-snapshot`, `cancel-request`, `progress`, `readiness`, `evidence` | Same Core/store paths as web API | Not a full proof that every legacy frontend uses these services |
| Headless worker | `plan serve-requests` | `Core.serve_workflow_run_requests` polls and calls `drain_workflow_run_requests` | One worker process can own claims with fencing; no automatic replay of uncertain effects |
| Manual queue drain | `plan drain-requests` | Same Core transactional queue and lease fencing | Should not run ad hoc in paired supervision without operator coordination |
| Gunicorn web factory | `create_app_factory()` | When `WHAXON_V2_EXTERNAL_WORKER=1`, no web-startup local V2 drainer | Without the flag, backwards-compatible process-local wakeup remains |
| Flask V2 run route | `workflow_v2_run()` | Same external-worker flag suppresses per-request web drainer | The persisted 202 remains available even if worker is down |
| systemd web + worker | `whaxon.service`, `whaxon-workflow-worker.service` | Web unit sets external-worker mode; worker runs CLI `serve-requests` | Unit definitions and static tests are not successful host installation |
| Docker web + worker | `docker-compose.e5.yml`; `Dockerfile` | Web external-worker mode, dedicated worker, common `/data` volume | CI launch/persistence tests are an engineering surrogate, not production-host sign-off |
| CLI workflow run | `workflow_cmd.py`: `plan run`; `interfaces/cli/run_cmd.py` | Persisted V2 run requests use the durable queue and supervised worker; direct legacy ToolRunner/session execution remains explicit compatibility mode | Default run/proposal paths do not directly dispatch. `--legacy` compatibility behavior remains in the migration inventory and is not V2-owned. |
| Retired web tool/AI routes and remaining Metasploit paths | `server.py`: `POST /api/run`, `POST /api/ai/run`, AI answer, plus Metasploit routes | Tool/AI compatibility routes return HTTP 410 without dispatch; Metasploit/session/port-forward paths remain gated legacy integrations | The direct tool/AI web authorities are retired. Platform-wide migration remains open for Metasploit, legacy CLI/session, validation/retest, and other documented compatibility paths. |
| External effect scheduler | `Core.run_workflow_plan`, workflow scheduling, `WorkflowRunQueue.claim/finish/reconcile_stale` | Task-level authorization/lease and request-level fencing | Failed/expired worker effects become uncertain, never silently requeued |

**Important distinction:** the new paired deployment has a single **V2 durable run-request drainer** by default. WHAXON still contains legacy direct execution paths and interfaces. E5-A cannot be fully accepted until their permitted coexistence, migration, security boundary and rollback are explicitly reviewed.

## Current evidence (not whole-phase sign-off)

- `tests/test_workflow_run_requests.py`: request persistence, deduplication, cancellation, reconnect, external-worker mode and cross-client submission parity.
- `tests/test_workflow_run_requests.py::test_e5_run_snapshot_pins_request_and_progress_to_one_db_snapshot`: a cancellation committed between the two projections stays invisible to both halves of the existing read snapshot.
- `tests/test_workflow_continuous_worker.py`: shutdown, poll, lost lease and bounded queue continuation.
- `tests/test_engine_v2_e5_queue_head_recovery.py`: poisoned heads, bounded quarantine and stale lease recovery.
- `tests/test_engine_v2_e5_systemd_deployment.py`: two-unit contract with matched identity and shared state.
- `tests/test_engine_v2_e5_docker_compose.py`: isolated Compose deployment, image resources and hardening.
- `tests/test_engine_v2_e5_state_snapshot.py`: SQLite+configuration+evidence snapshot, checksum verification, tampering and no-overwrite restore.
- `.github/workflows/ci.yml`: paired Docker web/worker launch, inert request, worker restart, cold offline snapshot and isolated restored mission check.
- The exact final E5 PR-head CI run and supervised real-host/service deployment evidence must be recorded before E5-F/E5-E are closed.

## Controlled rollout and rollback

1. Before rollout, select the authorized deployment target, persist the exact artifact digest/commit, documented scope, credentials and endpoint exposure plan. Identify a responsible operator and establish an external evidence/manifest witness.
2. Prevent new submissions, stop **both** web and worker services, and take an offline full-state snapshot with `python -m whaxon.core.state_snapshot backup`. Retain the resulting manifest SHA-256 **outside** WHAXON data and verify it independently.
3. Deploy the matching web and worker package/image as a pair. Use `WHAXON_V2_EXTERNAL_WORKER=1` for the web side so the web accepts durable requests but does not separately drain them. Keep the worker under systemd or Compose supervision.
4. Check readiness truthfulness and queue status. Use only explicitly approved inert/sandboxed workflow targets for admission, reconnect, cancellation and restart checks; record request IDs and exact result evidence. A 202 or successful health probe is never proof of external execution.
5. On failure, stop new intake, stop both processes and inspect all running, stale and uncertain attempts. Do **not** downgrade SQLite/schema, auto-requeue uncertain requests, blindly delete credentials, or convert queued work into a success claim.
6. Restore only a verified matching-version full-state snapshot into a new protected directory. Verify manifest against its externally retained digest; restore operator-controlled secrets, scope and permissions separately where needed. Validate queue reconciliation before a deliberate cutover.
7. Do not remove external-worker mode to fall back to web-only execution while old accepted queued work is present without explicit policy review: startup web draining could begin execution unexpectedly. Version rollback and schema migration require independent compatibility tests and operator approval.

## E5-A through E5-G decision

All seven whole-phase engineering gates remain **OPEN** until the acceptance file records a checked source baseline, exhaustive supported-path matrix, cross-client contracts, adversarial and live service evidence, exact-head CI for required platforms, migration/rollback verification and an explicit engineering acceptance decision. Final production lab, host/container, independent audit anchor and real external-target acceptance remain additional non-waivable deployment gates under the master roadmap.

This inventory does not authorize direct security tooling, scanner use or any unapproved target.

## Atomic reconnect snapshot — 2026-11-21

`GET /api/v2/workflow-runs/<id>/snapshot` reads the durable request row and
workflow progress inside one SQLite read transaction. A concurrent cancellation
cannot produce a mixed view such as a queued request paired with a cancelled
plan. The response schema is unchanged, lease tokens remain redacted, and
`worker_liveness_verified` remains false. The race regression commits a real
cancellation after the request row is read but before progress is projected,
then verifies the first response is consistent and the next read observes the
cancellation.
