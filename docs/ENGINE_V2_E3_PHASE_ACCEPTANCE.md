# Engine V2 E3 — whole-phase acceptance register

**Scope:** E3 durable operations, on the sole E3 integration PR #122. The master roadmap §0/P2 and the V2 crosswalk §14 are authoritative.

**Decision:** **OPEN / NOT ACCEPTED** until exact-head CI, controlled authorized integration and external audit anchoring requirements have verifiable evidence. Source tests below are test *definitions*, not claims of observed passing results until a cited exact-head run succeeds. Zero additional phase PRs or premature merge permitted.

| Gate | Required behavior and evidence | Source/test candidate | Current decision |
|---|---|---|---|
| E3-A | Durable mission, plan, task and attempt lifecycle across reopen | `store.py`, `tests/test_workflow.py` | SOURCE_PRESENT, acceptance open |
| E3-B | Atomic claims, multi-process workers, no double ownership | `tests/test_engine_v2_e3_process_boundaries.py` | SOURCE_PRESENT, acceptance open |
| E3-C | Plan and mission attempt, concurrency, deadline, rate, cost budgets enforced during claim and dispatch | `tests/test_workflow.py`; `tests/test_engine_v2_e3_dispatch_gate_classification.py` | SOURCE_PRESENT, acceptance open |
| E3-D | Cancellation and stop intent durably fenced through final run-request completion | `tests/test_engine_v2_e3_queue_atomicity.py` | SOURCE_PRESENT, acceptance open |
| E3-E | Expired task/request leases fenced and reconciled without blind replay | `tests/test_engine_v2_e3_process_boundaries.py`; `tests/test_engine_v2_e3_recovery_boundaries.py` | SOURCE_PRESENT, acceptance open |
| E3-F | Actual controlled external HTTP side effect, worker hard kill and response disconnect; no retry | `tests/test_engine_v2_e3_external_effect_crash.py` | NEW TEST DEFINED, CI pending |
| E3-G | Corrupt run-request limit/digest, plan drift and missing source fail closed | `tests/test_engine_v2_e3_e5_queue_integrity.py`; `tests/test_engine_v2_e3_completion_identity.py` | SOURCE_PRESENT, acceptance open |
| E3-H | Audit event/state write failure rolls back all related transitions | `tests/test_engine_v2_e3_queue_atomicity.py` | NEW TEST DEFINED, CI pending |
| E3-I | Event cursors monotone and persisted; at-least-once replay after unacknowledged delivery | `tests/test_workflow.py::test_workflow_event_cursor_is_durable_monotone_and_plan_scoped` | SOURCE_PRESENT, full delivery lab open |
| E3-J | Semantic audit integrity cross-check and fail-closed reporting | `tests/test_engine_v2_e3_audit_semantic_integrity.py` | NEW TEST DEFINED, CI pending |
| E3-K | Lifecycle snapshot stable across restart; changed event/attempt/task detected against caller-held digest | `tests/test_engine_v2_e3_audit_snapshot_anchor.py`; `tests/test_engine_v2_e3_audit_cli.py` | NEW TEST DEFINED, CI pending |
| E3-L | Independently protected trust anchor, retention and deletion contract verified under database tampering | Operator-controlled external anchor and witness evidence required | **OPEN: NOT IMPLEMENTATION-ACCEPTED** |
| E3-M | Real authorized scanner external effects plus crash, network failure, host restart and independent reconciliation | Approved lab target, recorded run, side-effect ledger and recovery transcript required | **OPEN: LAB NOT RUN** |
| E3-N | Production multi-worker/service/database-backup and restored-client operational recovery | Systemd deployment, backup including config/evidence, supported host, recovery evidence required | **OPEN: E3/E5 INTEGRATION** |
| E3-O | Supported Python/platform lint, mypy, tests, package and security checks on exact PR SHA | GitHub Actions workflow `.github/workflows/ci.yml` | **OPEN until exact-head CI succeeds** |
| E3-P | Signed reviewer/operator acceptance, SHA, test commands, environment, residuals and rollback | Final acceptance record | **OPEN** |

## Coordinated workstreams and integration rules

- **W1 — durable queue/worker ownership:** `workflow_requests.py`, process and recovery tests. Own enqueue/claim/finish/cancel lease transitions and reconciliation.
- **W2 — scheduler and persisted budgets:** `scheduler.py`, `store.py`, budget/deadline/concurrency and cancellation correctness, with one integration owner for shared `store.py`.
- **W3 — audit/outbox integrity:** event cursors, transaction rollback tests, immutable snapshot reference API and external anchor delivery contract. Never claim local hashing proves immutability.
- **W4 — independent adversarial validation:** loopback HTTP crash/disconnect, process kill, multi-worker races, corrupted ledger and audit writes; controlled authorized scanner effects remain a separate E3-M gate.
- **W5 — operator surface, evidence and integration:** CLI/Core audit interfaces, exact-head CI results, E3/E5 operational handoff, recovery/rollback documentation and the single-PR merge gate.

Workstreams may proceed concurrently only with stable contracts and explicit file ownership. A single integration owner combines shared-file changes. Parallel source reads do not count as independently implemented engineering.

## Required exact-head gate evidence

Record, on the *final* PR SHA: Python 3.11/3.12/3.13 CI job names and conclusions, all E3-focused test names and outcomes, real process/network failure evidence, environment and commands, deployment/recovery lab constraints, an independently retained audit snapshot witness, limitations, reviewer and rollback decision.

**Never infer a phase-completion percentage from this register's number of SOURCE_PRESENT rows.** Until every required gate is accepted, E3's formal status is open. The implementation may be substantial without full acceptance.

## Operator lifecycle audit snapshot workflow

Run `whaxon workflow --data-dir <state> plan audit-snapshot --id <plan>` and **save the displayed digest outside the WHAXON host/database in an independently protected store**, with plan ID, UTC time, environment and code SHA. Later run `whaxon workflow --data-dir <state> plan audit-verify --id <plan> --expected-digest <64-hex-reference>`. A result of `digest_matches_reference: true` proves equality to the caller-provided reference for the documented snapshot scope only. It does **not** authenticate the source of that reference. Both subcommands are read-only.
