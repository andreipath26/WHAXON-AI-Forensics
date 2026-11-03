"""Durable Engine V2 run-intent queue shared by API and headless workers.

A queued request survives client/server exit. Running requests are never
replayed automatically after lease loss: the outcome of the external effect
must be reconciled first. Task-level leases and authorization remain owned by
the existing workflow scheduler.
"""
from __future__ import annotations

import json
import math
import time
import uuid


class WorkflowRunQueue:
    def __init__(self, store):
        self.store = store
        with store._lock:
            conn = store._conn()
            try:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS workflow_run_requests (
                        id TEXT PRIMARY KEY,
                        plan_id TEXT NOT NULL,
                        plan_digest TEXT NOT NULL,
                        limits_json TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'queued',
                        owner TEXT,
                        lease_token TEXT,
                        submitted_at REAL NOT NULL,
                        started_at REAL,
                        heartbeat_at REAL,
                        completed_at REAL,
                        error TEXT
                    );
                    CREATE UNIQUE INDEX IF NOT EXISTS
                      idx_workflow_run_open_plan
                      ON workflow_run_requests(plan_id)
                      WHERE status IN ('queued','running','uncertain');
                    CREATE INDEX IF NOT EXISTS idx_workflow_run_queue
                      ON workflow_run_requests(status,submitted_at);
                """)
            finally:
                conn.close()

    @staticmethod
    def _check_limits(limits):
        expected = {"max_tasks", "max_attempts", "max_concurrency"}
        if not isinstance(limits, dict) or set(limits) != expected:
            raise ValueError("exact workflow execution limits are required")
        if any(type(limits[key]) is not int or not 1 <= limits[key] <= 1000
               for key in expected):
            raise ValueError("workflow execution limits must be positive and bounded")

    @staticmethod
    def _format(row):
        data = dict(row)
        data["limits"] = json.loads(data.pop("limits_json"))
        return data

    def enqueue(self, plan_id: str, *, limits: dict) -> dict:
        self._check_limits(limits)
        now = time.time()
        request_id = uuid.uuid4().hex
        with self.store._lock:
            conn = self.store._conn()
            try:
                conn.execute("BEGIN IMMEDIATE")
                plan = conn.execute(
                    "SELECT digest, status FROM workflow_plans WHERE id=?",
                    (plan_id,),
                ).fetchone()
                if plan is None:
                    raise ValueError("unknown workflow plan")
                if plan["status"] == "cancel_requested":
                    raise ValueError("cannot enqueue cancelled workflow")
                existing = conn.execute(
                    "SELECT * FROM workflow_run_requests WHERE plan_id=? "
                    "AND status IN ('queued','running','uncertain')",
                    (plan_id,),
                ).fetchone()
                if existing is not None:
                    if json.loads(existing["limits_json"]) != limits:
                        raise ValueError("active workflow request has different limits")
                    conn.execute("COMMIT")
                    return self._format(existing)
                conn.execute(
                    "INSERT INTO workflow_run_requests "
                    "(id,plan_id,plan_digest,limits_json,submitted_at) "
                    "VALUES (?,?,?,?,?)",
                    (request_id, plan_id, plan["digest"],
                     json.dumps(limits, sort_keys=True), now),
                )
                row = conn.execute(
                    "SELECT * FROM workflow_run_requests WHERE id=?",
                    (request_id,),
                ).fetchone()
                conn.execute("COMMIT")
                return self._format(row)
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
            finally:
                conn.close()

    def get(self, request_id: str) -> dict | None:
        """Public inspection excludes the private worker fencing credential."""
        conn = self.store._conn()
        try:
            row = conn.execute(
                "SELECT * FROM workflow_run_requests WHERE id=?",
                (request_id,),
            ).fetchone()
            if row is None:
                return None
            value = self._format(row)
            value.pop("lease_token", None)
            return value
        finally:
            conn.close()

    def claim(self, owner: str) -> dict | None:
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("worker owner required")
        with self.store._lock:
            conn = self.store._conn()
            try:
                conn.execute("BEGIN IMMEDIATE")
                # Quarantine bounded malformed/obsolete queue heads instead of
                # starving valid requests behind them. All decisions and the
                # eventual claim share this one SQLite write transaction.
                for _ in range(64):
                    row = conn.execute(
                        "SELECT * FROM workflow_run_requests "
                        "WHERE status='queued' "
                        "ORDER BY submitted_at,id LIMIT 1",
                    ).fetchone()
                    if row is None:
                        conn.execute("COMMIT")
                        return None
                    plan = conn.execute(
                        "SELECT digest,status FROM workflow_plans WHERE id=?",
                        (row["plan_id"],),
                    ).fetchone()
                    if plan is None or plan["digest"] != row["plan_digest"]:
                        reason = (
                            "source plan missing before dispatch"
                            if plan is None else "plan digest changed before dispatch"
                        )
                        conn.execute(
                            "UPDATE workflow_run_requests SET status='uncertain', "
                            "completed_at=?,error=? WHERE id=? AND status='queued'",
                            (time.time(), reason, row["id"]),
                        )
                        continue
                    if plan["status"] == "cancel_requested":
                        conn.execute(
                            "UPDATE workflow_run_requests SET status='cancelled', "
                            "completed_at=?,error='plan cancelled before run claim' "
                            "WHERE id=? AND status='queued'",
                            (time.time(), row["id"]),
                        )
                        continue
                    try:
                        # Persisted limits are untrusted after restart, manual
                        # recovery or storage damage. A malformed payload must
                        # never acquire a worker lease or starve later work.
                        self._check_limits(json.loads(row["limits_json"]))
                    except (TypeError, ValueError):
                        conn.execute(
                            "UPDATE workflow_run_requests SET status='uncertain', "
                            "completed_at=?,error='invalid persisted execution limits' "
                            "WHERE id=? AND status='queued'",
                            (time.time(), row["id"]),
                        )
                        continue
                    token = uuid.uuid4().hex
                    now = time.time()
                    conn.execute(
                        "UPDATE workflow_run_requests SET status='running', "
                        "owner=?,lease_token=?,started_at=?,heartbeat_at=? "
                        "WHERE id=? AND status='queued'",
                        (owner, token, now, now, row["id"]),
                    )
                    claimed = conn.execute(
                        "SELECT * FROM workflow_run_requests WHERE id=?",
                        (row["id"],),
                    ).fetchone()
                    conn.execute("COMMIT")
                    return self._format(claimed)
                # A poisoned backlog larger than one bounded pass is
                # reconciled by subsequent polls; no unbounded lock hold.
                conn.execute("COMMIT")
                return None
            except Exception:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
            finally:
                conn.close()

    def cancel_queued(self, plan_id: str) -> int:
        """Close only unclaimed requests; a running effect is not stopped."""
        with self.store._lock:
            conn = self.store._conn()
            try:
                cursor = conn.execute(
                    "UPDATE workflow_run_requests SET status='cancelled',"
                    "completed_at=?,error='plan cancelled before run claim' "
                    "WHERE plan_id=? AND status='queued'",
                    (time.time(), plan_id),
                )
                return cursor.rowcount
            finally:
                conn.close()

    def heartbeat(self, request_id: str, token: str) -> bool:
        with self.store._lock:
            conn = self.store._conn()
            try:
                cursor = conn.execute(
                    "UPDATE workflow_run_requests SET heartbeat_at=? "
                    "WHERE id=? AND status='running' AND lease_token=?",
                    (time.time(), request_id, token),
                )
                return cursor.rowcount == 1
            finally:
                conn.close()

    def finish(self, request_id: str, token: str, *, status: str,
               error: str = "") -> bool:
        if status not in {"completed", "incomplete", "failed", "uncertain"}:
            raise ValueError("invalid run request outcome")
        with self.store._lock:
            conn = self.store._conn()
            try:
                cursor = conn.execute(
                    "UPDATE workflow_run_requests SET status=?,error=?,"
                    "completed_at=?,owner=NULL,lease_token=NULL "
                    "WHERE id=? AND status='running' AND lease_token=?",
                    (status, error, time.time(), request_id, token),
                )
                return cursor.rowcount == 1
            finally:
                conn.close()

    def summary(self, *, stale_after_s: float = 120.0) -> dict:
        """Read-only persisted queue health, never a worker-liveness assertion.

        A recent heartbeat is evidence of a timestamp, not proof of a live
        worker or authorized external effect. No lease token is disclosed.
        """
        if (isinstance(stale_after_s, bool)
                or not isinstance(stale_after_s, (int, float))
                or not math.isfinite(stale_after_s) or stale_after_s <= 0):
            raise ValueError("stale_after_s must be finite and positive")
        now = time.time()
        conn = self.store._conn()
        try:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS count "
                "FROM workflow_run_requests GROUP BY status",
            ).fetchall()
            counts = {
                status: 0 for status in (
                    "queued", "running", "uncertain", "completed",
                    "incomplete", "failed", "cancelled",
                )
            }
            counts.update({row["status"]: int(row["count"]) for row in rows})
            queued = conn.execute(
                "SELECT MIN(submitted_at) AS oldest "
                "FROM workflow_run_requests WHERE status='queued'",
            ).fetchone()["oldest"]
            stale = conn.execute(
                "SELECT COUNT(*) AS total FROM workflow_run_requests "
                "WHERE status='running' AND "
                "(heartbeat_at IS NULL OR heartbeat_at<?)",
                (now - stale_after_s,),
            ).fetchone()["total"]
            return {
                "schema_version": "whaxon.workflow-run-queue-summary.v1",
                "snapshot_at": now,
                "counts": counts,
                "total": sum(counts.values()),
                "oldest_queued_age_s": (
                    max(0.0, now - queued) if queued is not None else None
                ),
                "stale_running_count": int(stale),
                "uncertain_count": counts["uncertain"],
                "requires_reconciliation_count": counts["uncertain"] + int(stale),
                "stale_after_s": float(stale_after_s),
                "worker_liveness_verified": False,
                "automatic_uncertain_replay": False,
            }
        finally:
            conn.close()

    def reconcile_stale(self, *, older_than_s: float = 120) -> int:
        if (isinstance(older_than_s, bool)
                or not isinstance(older_than_s, (int, float))
                or not math.isfinite(older_than_s) or older_than_s <= 0):
            raise ValueError("stale timeout must be finite and positive")
        with self.store._lock:
            conn = self.store._conn()
            try:
                cursor = conn.execute(
                    "UPDATE workflow_run_requests SET status='uncertain',"
                    "error='run worker lost; reconcile task attempts before any retry',"
                    "completed_at=?,owner=NULL,lease_token=NULL "
                    "WHERE status='running' AND (heartbeat_at IS NULL OR heartbeat_at<?)",
                    (time.time(), time.time() - older_than_s),
                )
                return cursor.rowcount
            finally:
                conn.close()
