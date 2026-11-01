import json
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, tool TEXT DEFAULT '', target TEXT DEFAULT '', status TEXT DEFAULT 'starting', exit_code INTEGER, error TEXT, started_at REAL, finished_at REAL, duration_s REAL, lease_owner TEXT, lease_token TEXT, heartbeat_at REAL);
CREATE TABLE IF NOT EXISTS lines (job_id TEXT, seq INTEGER, stream TEXT, text TEXT, PRIMARY KEY (job_id, seq));
CREATE TABLE IF NOT EXISTS findings (job_id TEXT, seq INTEGER, kind TEXT, severity TEXT, source TEXT, data_json TEXT, raw_line TEXT, enrichment_json TEXT DEFAULT '{}', verification_status TEXT DEFAULT 'candidate', verified_by TEXT DEFAULT 'engine', verification_reason TEXT DEFAULT '', PRIMARY KEY (job_id, seq));
CREATE TABLE IF NOT EXISTS coverage (job_id TEXT, seq INTEGER, tool_id TEXT, target TEXT, kind TEXT, detail TEXT, phase TEXT DEFAULT '', at REAL, PRIMARY KEY (job_id, seq));
CREATE INDEX IF NOT EXISTS idx_jobs_started ON jobs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_lines_job ON lines(job_id, seq);
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    host TEXT,
    type TEXT,
    info_json TEXT,
    opened_at REAL,
    last_seen REAL,
    status TEXT DEFAULT 'open'
);
CREATE TABLE IF NOT EXISTS evidence (
    job_id TEXT, seq INTEGER, kind TEXT, name TEXT, path TEXT, note TEXT, added_at REAL,
    PRIMARY KEY (job_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_evidence_job ON evidence(job_id, seq);
CREATE TABLE IF NOT EXISTS ai_runs (id TEXT PRIMARY KEY, goal TEXT NOT NULL, provider TEXT DEFAULT 'null', status TEXT DEFAULT 'running', started_at REAL, finished_at REAL, error TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS ai_run_steps (run_id TEXT, seq INTEGER, action_json TEXT, result_json TEXT, created_at REAL, PRIMARY KEY (run_id, seq));
CREATE INDEX IF NOT EXISTS idx_ai_runs_started ON ai_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_run_steps_run ON ai_run_steps(run_id, seq);
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY, objective TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft',
    metadata_json TEXT NOT NULL DEFAULT '{}', created_at REAL NOT NULL, updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS workflow_plans (
    id TEXT PRIMARY KEY, mission_id TEXT NOT NULL, schema_version TEXT NOT NULL,
    digest TEXT NOT NULL, plan_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'proposed',
    created_at REAL NOT NULL, UNIQUE(mission_id, digest)
);
CREATE INDEX IF NOT EXISTS idx_workflow_plans_mission ON workflow_plans(mission_id, created_at);
CREATE TABLE IF NOT EXISTS workflow_tasks (
    id TEXT PRIMARY KEY, task_key TEXT NOT NULL, plan_id TEXT NOT NULL, capability_id TEXT NOT NULL,
    target TEXT NOT NULL, inputs_json TEXT NOT NULL, depends_on_json TEXT NOT NULL,
    permissions_json TEXT NOT NULL, impact TEXT NOT NULL, timeout_s REAL NOT NULL,
    idempotency_key TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'pending',
    result_json TEXT, error TEXT, active_attempt_id TEXT,
    created_at REAL NOT NULL, updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_tasks_plan ON workflow_tasks(plan_id);
CREATE TABLE IF NOT EXISTS capability_manifests (capability_id TEXT NOT NULL, provider_id TEXT NOT NULL, provider_version TEXT NOT NULL, fingerprint TEXT NOT NULL, manifest_json TEXT NOT NULL, registered_at REAL NOT NULL, PRIMARY KEY (capability_id, provider_id, provider_version));
CREATE TABLE IF NOT EXISTS task_attempts (
    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, attempt_no INTEGER NOT NULL,
    status TEXT NOT NULL, worker_id TEXT NOT NULL DEFAULT '', idempotency_key TEXT NOT NULL DEFAULT '',
    started_at REAL NOT NULL, finished_at REAL, result_json TEXT, error TEXT,
    UNIQUE(task_id, attempt_no)
);
CREATE INDEX IF NOT EXISTS idx_task_attempts_task ON task_attempts(task_id, attempt_no);
"""



def _signature_for(kind: str, data: dict) -> str:
    """Build a stable per-finding signature for dedup."""
    if kind == "open_port":
        return f"port:{data.get('port')}/{data.get('protocol', 'tcp')}"
    if kind == "web_issue":
        return f"path:{data.get('path') or data.get('location') or ''}"
    if kind == "found_path":
        # A path is not a single fact: different tools or runs can observe
        # different status codes and response sizes for the same URL. Include
        # the observed response attributes so target-level aggregation never
        # silently discards contradictory scanner evidence.
        return "path:%s|status:%s|size:%s" % (
            data.get("path") or "",
            data.get("status") if data.get("status") is not None else "unknown",
            data.get("size") if data.get("size") is not None else "unknown",
        )
    if kind == "sqli":
        return f"param:{data.get('parameter') or ''}"
    if kind == "sqli_database":
        return f"db:{data.get('name') or ''}"
    if kind == "sqli_table":
        return f"table:{data.get('database') or ''}.{data.get('table') or ''}"
    if kind.startswith("sqli_"):
        return f"key:{data.get('key') or ''}"
    if kind == "domain_expiry":
        return "domain_expiry"
    if kind == "registrar":
        return f"registrar:{data.get('registrar') or ''}"
    if kind == "nameserver":
        return f"ns:{data.get('ns') or ''}"
    if kind == "vulnerability":
        return f"template:{data.get('template') or ''}"
    if kind == "correlated":
        # Correlator findings carry pattern + service + version + cve.
        # Distinct service/version combos must not collapse.
        return "pattern:%s|%s|%s|%s" % (
            data.get("pattern") or "",
            data.get("service") or "",
            data.get("version") or "",
            data.get("cve") or "",
        )
    if kind == "msf_session":
        return "msf:%s" % (data.get("session_id") or data.get("sid") or "")
    if kind == "ntlm_hash":
        return "ntlm:%s" % (data.get("user") or data.get("username") or "")
    if kind == "hashcat_crack":
        return "hashcat:%s" % (data.get("hash") or "")[:32]
    # Fallback: a stable hash of the whole data dict, never just the
    # first value. Two distinct findings with different data must never
    # produce the same signature.
    import hashlib as _hashlib
    import json as _json
    blob = _json.dumps(data or {}, sort_keys=True, default=str)
    return "data:" + _hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

class JobStore:
    def __init__(self, db_path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        c = self._conn()
        try:
            c.executescript(SCHEMA)
            # Durable worker leases. Existing databases are upgraded in place.
            for column, definition in (
                ("lease_owner", "TEXT"),
                ("lease_token", "TEXT"),
                ("heartbeat_at", "REAL"),
            ):
                try:
                    c.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")
                except sqlite3.OperationalError:
                    pass
            # Migration: add phase column to ai_runs if absent (step 2 of the
            # agent-architecture migration plan). Idempotent: SQLite raises
            # if the column exists, which we swallow.
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN phase TEXT DEFAULT 'recon'")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN phase_history TEXT DEFAULT '[]'")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN pending_question TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN tokens_in INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN tokens_out INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN cost_usd REAL")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN owner TEXT DEFAULT 'local'")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN consecutive_failures INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE ai_runs ADD COLUMN auto INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE findings ADD COLUMN verification_status TEXT DEFAULT 'candidate'")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE findings ADD COLUMN verified_by TEXT DEFAULT 'engine'")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE findings ADD COLUMN verification_reason TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE coverage ADD COLUMN phase TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE workflow_tasks ADD COLUMN active_attempt_id TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                c.execute("ALTER TABLE workflow_tasks ADD COLUMN task_key TEXT")
            except sqlite3.OperationalError:
                pass
            c.execute("UPDATE workflow_tasks SET task_key=id WHERE task_key IS NULL")
            c.execute("CREATE TABLE IF NOT EXISTS approvals (run_id TEXT, seq INTEGER, user TEXT, answer TEXT, note TEXT, at REAL, PRIMARY KEY (run_id, seq))")
        finally: c.close()
    def _conn(self):
        c = sqlite3.connect(self.path, timeout=10.0, isolation_level=None)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=NORMAL")
        c.row_factory = sqlite3.Row
        return c
    def create(self, job_id):
        with self._lock:
            c = self._conn()
            try: c.execute("INSERT OR IGNORE INTO jobs (id, started_at) VALUES (?, ?)", (job_id, time.time()))
            finally: c.close()
    def set_started(self, job_id, tool, target, lease_token=None):
        with self._lock:
            c = self._conn()
            try:
                now = time.time()
                if lease_token:
                    cur = c.execute(
                        "UPDATE jobs SET status='running', tool=?, target=?, started_at=?, heartbeat_at=? "
                        "WHERE id=? AND status='running' AND lease_token=?",
                        (tool, target, now, now, job_id, lease_token),
                    )
                else:
                    cur = c.execute(
                        "UPDATE jobs SET status='running', tool=?, target=?, started_at=? WHERE id=?",
                        (tool, target, now, job_id),
                    )
                return cur.rowcount == 1
            finally:
                c.close()

    def create_pending(self, job_id, tool, target):
        """Queue a job durably; it remains pending until atomically leased."""
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "INSERT OR IGNORE INTO jobs (id, tool, target, status) VALUES (?, ?, ?, 'pending')",
                    (job_id, tool, target),
                )
            finally:
                c.close()

    def list_pending(self):
        c = self._conn()
        try:
            rows = c.execute(
                "SELECT id, tool, target FROM jobs WHERE status='pending' ORDER BY started_at"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            c.close()

    def claim_pending(self, *, exclude_ids=None, worker_id=None):
        """Atomically lease one pending job and return its fencing token."""
        import secrets

        excluded = tuple(exclude_ids or ())
        owner = str(worker_id or "worker")
        token = secrets.token_urlsafe(32)
        now = time.time()
        with self._lock:
            c = self._conn()
            try:
                where = "status='pending'"
                params = []
                if excluded:
                    placeholders = ",".join("?" for _ in excluded)
                    where += f" AND id NOT IN ({placeholders})"
                    params.extend(excluded)
                row = c.execute(
                    "UPDATE jobs SET status='running', started_at=?, lease_owner=?, "
                    "lease_token=?, heartbeat_at=? WHERE id=(SELECT id FROM jobs WHERE "
                    + where + " ORDER BY started_at, id LIMIT 1) "
                    "RETURNING id, tool, target, lease_owner, lease_token, heartbeat_at",
                    (now, owner, token, now, *params),
                ).fetchone()
                return dict(row) if row else None
            finally:
                c.close()

    def heartbeat_job(self, job_id, lease_token):
        """Renew a worker lease; false means ownership has been lost."""
        with self._lock:
            c = self._conn()
            try:
                cur = c.execute(
                    "UPDATE jobs SET heartbeat_at=? WHERE id=? AND status='running' AND lease_token=?",
                    (time.time(), job_id, lease_token),
                )
                return cur.rowcount == 1
            finally:
                c.close()

    def owns_lease(self, job_id, lease_token):
        if not lease_token:
            return True
        c = self._conn()
        try:
            return c.execute(
                "SELECT 1 FROM jobs WHERE id=? AND status IN ('running', 'finished') AND lease_token=?",
                (job_id, lease_token),
            ).fetchone() is not None
        finally:
            c.close()

    def release_lease(self, job_id, lease_token):
        """Release a terminal job lease after its event callbacks have persisted."""
        if not lease_token:
            return False
        with self._lock:
            c = self._conn()
            try:
                cur = c.execute(
                    "UPDATE jobs SET lease_owner=NULL, lease_token=NULL, heartbeat_at=NULL "
                    "WHERE id=? AND status IN ('finished', 'failed') AND lease_token=?",
                    (job_id, lease_token),
                )
                return cur.rowcount == 1
            finally:
                c.close()

    def reconcile_stale(self, older_than_s=120.0):
        """Fail expired running jobs without replaying uncertain side effects."""
        cutoff = time.time() - older_than_s
        now = time.time()
        with self._lock:
            c = self._conn()
            try:
                cur = c.execute(
                    "UPDATE jobs SET status='failed', "
                    "error='worker lease expired; execution outcome requires reconciliation', "
                    "finished_at=?, lease_owner=NULL, lease_token=NULL, heartbeat_at=NULL "
                    "WHERE status='running' AND COALESCE(heartbeat_at, started_at) < ?",
                    (now, cutoff),
                )
                return cur.rowcount
            finally:
                c.close()

    def append_line(self, job_id, stream, text):
        with self._lock:
            c = self._conn()
            try:
                row = c.execute("SELECT COALESCE(MAX(seq), -1) + 1 AS n FROM lines WHERE job_id=?", (job_id,)).fetchone()
                c.execute("INSERT INTO lines VALUES (?, ?, ?, ?)", (job_id, row["n"], stream, text))
            finally: c.close()
    def append_finding(self, job_id, f, seq):
        if hasattr(f, "to_dict"):
            f = f.to_dict()
        enrichment = {
            "remediation": f.get("remediation", ""),
            "impact": f.get("impact", ""),
            "cvss": f.get("cvss"),
            "cwe": f.get("cwe", ""),
            "references": f.get("references", []),
            "lookup_hint": f.get("lookup_hint", ""),
            # Keep the canonical request context alongside enrichment so it
            # survives the SQLite round trip without a destructive schema migration.
            "request_context": f.get("request_context") or {},
        }
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "INSERT INTO findings (job_id, seq, kind, severity, source, data_json, raw_line, enrichment_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (job_id, seq, f.get("kind",""), f.get("severity","info"), f.get("source",""), json.dumps(f.get("data",{})), f.get("raw_line",""), json.dumps(enrichment))
                )
            finally: c.close()

    def update_verification(self, job_id, seq, status, by="engine", reason=""):
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "UPDATE findings SET verification_status=?, verified_by=?, verification_reason=? WHERE job_id=? AND seq=?",
                    (status, by, reason, job_id, seq),
                )
            finally: c.close()

    def set_proof(self, job_id, seq, proof):
        """Save a reproducible proof (e.g., curl command) into the finding's enrichment."""
        with self._lock:
            c = self._conn()
            try:
                row = c.execute(
                    "SELECT enrichment_json FROM findings WHERE job_id=? AND seq=?",
                    (job_id, seq)
                ).fetchone()
                if not row:
                    return
                enrichment = json.loads(row["enrichment_json"] or "{}")
                enrichment["proof"] = proof
                c.execute(
                    "UPDATE findings SET enrichment_json=? WHERE job_id=? AND seq=?",
                    (json.dumps(enrichment), job_id, seq)
                )
            finally:
                c.close()

    def record_coverage(self, job_id, tool_id, target, kind, detail, phase=""):
        with self._lock:
            c = self._conn()
            try:
                n = c.execute("SELECT COUNT(*) FROM coverage WHERE job_id=?", (job_id,)).fetchone()[0]
                c.execute(
                    "INSERT INTO coverage (job_id, seq, tool_id, target, kind, detail, phase, at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (job_id, n, tool_id, target, kind, detail, phase, time.time()),
                )
            finally: c.close()

    def list_coverage(self, job_id):
        c = self._conn()
        try:
            rows = c.execute(
                "SELECT seq, tool_id, target, kind, detail, phase FROM coverage WHERE job_id=? ORDER BY seq",
                (job_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally: c.close()

    def set_finished(self, job_id, exit_code, duration_s, lease_token=None):
        with self._lock:
            c = self._conn()
            try:
                if lease_token:
                    cur = c.execute(
                        "UPDATE jobs SET status='finished', exit_code=?, duration_s=?, finished_at=? "
                        "WHERE id=? AND status='running' AND lease_token=?",
                        (exit_code, duration_s, time.time(), job_id, lease_token),
                    )
                else:
                    cur = c.execute(
                        "UPDATE jobs SET status='finished', exit_code=?, duration_s=?, finished_at=? WHERE id=?",
                        (exit_code, duration_s, time.time(), job_id),
                    )
                return cur.rowcount == 1
            finally:
                c.close()

    def set_failed(self, job_id, error, lease_token=None):
        with self._lock:
            c = self._conn()
            try:
                if lease_token:
                    cur = c.execute(
                        "UPDATE jobs SET status='failed', error=?, finished_at=?, "
                        "lease_owner=NULL, lease_token=NULL, heartbeat_at=NULL "
                        "WHERE id=? AND status='running' AND lease_token=?",
                        (error, time.time(), job_id, lease_token),
                    )
                else:
                    cur = c.execute(
                        "UPDATE jobs SET status='failed', error=?, finished_at=? WHERE id=?",
                        (error, time.time(), job_id),
                    )
                return cur.rowcount == 1
            finally:
                c.close()
    def add_evidence(self, job_id, kind, name, path=None, note=None):
        with self._lock:
            c = self._conn()
            try:
                row = c.execute(
                    "SELECT COALESCE(MAX(seq), -1) + 1 AS n FROM evidence WHERE job_id=?",
                    (job_id,)
                ).fetchone()
                seq = row["n"]
                c.execute(
                    "INSERT INTO evidence (job_id, seq, kind, name, path, note, added_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (job_id, seq, kind, name, path, note, time.time()),
                )
                return seq
            finally:
                c.close()

    def list_evidence(self, job_id):
        c = self._conn()
        try:
            rows = c.execute(
                "SELECT seq, kind, name, path, note, added_at FROM evidence "
                "WHERE job_id=? ORDER BY seq", (job_id,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            c.close()

    def remove_evidence(self, job_id, seq):
        with self._lock:
            c = self._conn()
            try:
                cur = c.execute("DELETE FROM evidence WHERE job_id=? AND seq=?", (job_id, seq))
                return cur.rowcount > 0
            finally:
                c.close()

    # ---- msf sessions ----

    def upsert_session(self, session_id, host, session_type, info=None):
        import json as _json
        with self._lock:
            c = self._conn()
            try:
                now = time.time()
                existing = c.execute(
                    "SELECT id FROM sessions WHERE id=?", (session_id,)
                ).fetchone()
                if existing:
                    c.execute(
                        "UPDATE sessions SET host=?, type=?, info_json=?, last_seen=?, status='open' WHERE id=?",
                        (host, session_type, _json.dumps(info or {}), now, session_id),
                    )
                else:
                    c.execute(
                        "INSERT INTO sessions (id, host, type, info_json, opened_at, last_seen, status) "
                        "VALUES (?, ?, ?, ?, ?, ?, 'open')",
                        (session_id, host, session_type, _json.dumps(info or {}), now, now),
                    )
            finally:
                c.close()

    def close_session(self, session_id):
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "UPDATE sessions SET status='closed', last_seen=? WHERE id=?",
                    (time.time(), session_id),
                )
            finally:
                c.close()

    def get_session(self, session_id):
        """Return one persisted session, including its authorization context."""
        import json as _json
        c = self._conn()
        try:
            row = c.execute(
                "SELECT id, host, type, info_json, opened_at, last_seen, status "
                "FROM sessions WHERE id=?",
                (str(session_id),),
            ).fetchone()
            if row is None:
                return None
            try:
                info = _json.loads(row["info_json"] or "{}")
            except (TypeError, ValueError):
                info = {}
            return {
                "id": row["id"], "host": row["host"], "type": row["type"],
                "info": info, "opened_at": row["opened_at"],
                "last_seen": row["last_seen"], "status": row["status"],
            }
        finally:
            c.close()

    def list_sessions(self, include_closed=False):
        import json as _json
        c = self._conn()
        try:
            if include_closed:
                rows = c.execute(
                    "SELECT id, host, type, info_json, opened_at, last_seen, status "
                    "FROM sessions ORDER BY opened_at DESC"
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT id, host, type, info_json, opened_at, last_seen, status "
                    "FROM sessions WHERE status='open' ORDER BY opened_at DESC"
                ).fetchall()
            out = []
            for r in rows:
                try:
                    info = _json.loads(r["info_json"] or "{}")
                except Exception:
                    info = {}
                out.append({
                    "id": r["id"], "host": r["host"], "type": r["type"],
                    "info": info, "opened_at": r["opened_at"],
                    "last_seen": r["last_seen"], "status": r["status"],
                })
            return out
        finally:
            c.close()

    def get(self, job_id):
        c = self._conn()
        try:
            j = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not j: return None
            lines = c.execute("SELECT stream, text FROM lines WHERE job_id=? ORDER BY seq", (job_id,)).fetchall()
            return {"id": j["id"], "tool": j["tool"], "target": j["target"], "status": j["status"], "exit_code": j["exit_code"], "error": j["error"], "duration_s": j["duration_s"], "lines": [{"stream": ln["stream"], "text": ln["text"]} for ln in lines]}
        finally: c.close()
    def get_findings(self, job_id):
        c = self._conn()
        try:
            if not c.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone(): return None
            rows = c.execute(
                "SELECT seq, kind, severity, source, data_json, raw_line, enrichment_json, verification_status, verified_by, verification_reason "
                "FROM findings WHERE job_id=? ORDER BY seq", (job_id,)
            ).fetchall()
            out = []
            for r in rows:
                enrichment = {}
                try:
                    enrichment = json.loads(r["enrichment_json"] or "{}")
                except (json.JSONDecodeError, TypeError):
                    pass
                out.append({
                    "seq": r["seq"],
                    "verification_status": r["verification_status"],
                    "verified_by": r["verified_by"],
                    "verification_reason": r["verification_reason"],
                    "kind": r["kind"],
                    "severity": r["severity"],
                    "source": r["source"],
                    "data": json.loads(r["data_json"]),
                    "raw_line": r["raw_line"],
                    "remediation": enrichment.get("remediation", ""),
                    "impact": enrichment.get("impact", ""),
                    "cvss": enrichment.get("cvss"),
                    "cwe": enrichment.get("cwe", ""),
                    "references": enrichment.get("references", []),
                    "lookup_hint": enrichment.get("lookup_hint", ""),
                    "proof": enrichment.get("proof", ""),
                    "request_context": enrichment.get("request_context") or {},
                })
            return out
        finally: c.close()
    def active_jobs(self):
        """Return currently running jobs for live operational controls."""
        c = self._conn()
        try:
            rows = c.execute(
                "SELECT id, tool, target, status, started_at FROM jobs "
                "WHERE status='running' ORDER BY started_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            c.close()

    def history(self, limit=50):
        c = self._conn()
        try:
            rows = c.execute("SELECT id, tool, target, status, exit_code, duration_s, started_at FROM jobs WHERE status IN ('finished','failed') ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
            out = []
            for r in rows:
                line_count = c.execute(
                    "SELECT COUNT(*) AS n FROM lines WHERE job_id=?", (r["id"],)
                ).fetchone()["n"]
                findings_count = c.execute(
                    "SELECT COUNT(*) AS n FROM findings WHERE job_id=?", (r["id"],)
                ).fetchone()["n"]
                out.append({
                    "id": r["id"],
                    "tool": r["tool"],
                    "target": r["target"],
                    "status": r["status"],
                    "exit_code": r["exit_code"],
                    "duration_s": r["duration_s"],
                    "started_at": r["started_at"],
                    "line_count": line_count,
                    "findings_count": findings_count,
                })
            return out
        finally: c.close()

    def findings_by_target(self, limit: int = 50) -> list[dict]:
        """Group findings by target, deduped by (kind, signature)."""
        with self._lock:
            c = self._conn()
            try:
                # Get all jobs with their targets
                job_rows = c.execute(
                    "SELECT id, tool, target, status, exit_code, started_at "
                    "FROM jobs WHERE target != '' "
                    "ORDER BY started_at DESC LIMIT ?",
                    (limit * 5,),
                ).fetchall()

                targets: dict = {}
                seen: dict = {}  # (target, kind, sig) -> index in targets[target]["findings"]

                from .scope import _normalize_target
                for j in job_rows:
                    # Group by host, not raw target: 172.17.0.3 and
                    # 172.17.0.3:80 are the same target to a pentester.
                    target = _normalize_target(j["target"])[0] or j["target"]
                    if target not in targets:
                        targets[target] = {
                            "target": target,
                            "job_count": 0,
                            "finding_count": 0,
                            "findings": [],
                            "jobs": [],
                        }
                    t = targets[target]
                    t["jobs"].append({
                        "id": j["id"],
                        "tool": j["tool"],
                        "status": j["status"],
                        "exit_code": j["exit_code"],
                        "started_at": j["started_at"],
                    })
                    t["job_count"] += 1

                    # Pull findings for this job
                    f_rows = c.execute(
                        "SELECT kind, severity, source, data_json, raw_line, enrichment_json "
                        "FROM findings WHERE job_id=? ORDER BY seq",
                        (j["id"],),
                    ).fetchall()
                    for f in f_rows:
                        import json as _json
                        try:
                            data = _json.loads(f["data_json"] or "{}")
                        except Exception:
                            data = {}
                        try:
                            enrich = _json.loads(f["enrichment_json"] or "{}")
                        except Exception:
                            enrich = {}

                        sig = _signature_for(f["kind"], data)
                        # Preserve source provenance for path discoveries:
                        # two tools may report the same path with conflicting
                        # status/size values. _signature_for includes the observed
                        # status and size, while source prevents same-shaped but
                        # independently produced observations from collapsing.
                        key = (
                            target, f["kind"], sig,
                            f["source"] if f["kind"] == "found_path" else "",
                        )
                        if key in seen:
                            idx = seen[key]
                            t["findings"][idx]["count"] += 1
                            t["finding_count"] += 1
                            continue

                        t["findings"].append({
                            "kind": f["kind"],
                            "severity": f["severity"],
                            "source": f["source"],
                            "signature": sig,
                            "count": 1,
                            "data": data,
                            "raw_line": f["raw_line"],
                            "remediation": enrich.get("remediation", ""),
                            "impact": enrich.get("impact", ""),
                            "cvss": enrich.get("cvss"),
                            "cwe": enrich.get("cwe", ""),
                        })
                        seen[key] = len(t["findings"]) - 1
                        t["finding_count"] += 1

                # Sort by most recent job
                result = sorted(
                    [t for t in targets.values() if t["finding_count"] > 0],
                    key=lambda x: x["jobs"][0]["started_at"] if x["jobs"] else 0,
                    reverse=True,
                )
                return result[:limit]
            finally:
                c.close()

    def save_capability_manifest(self, manifest):
        import hashlib
        encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        key = (manifest["capability_id"], manifest["provider_id"], manifest["provider_version"])
        fingerprint = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        with self._lock:
            c = self._conn()
            try:
                row = c.execute(
                    "SELECT fingerprint FROM capability_manifests WHERE capability_id=? AND provider_id=? AND provider_version=?",
                    key,
                ).fetchone()
                if row is not None:
                    if row["fingerprint"] != fingerprint:
                        raise ValueError("provider manifest version is immutable")
                    return False
                c.execute(
                    "INSERT INTO capability_manifests (capability_id, provider_id, provider_version, fingerprint, manifest_json, registered_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (*key, fingerprint, encoded, time.time()),
                )
                return True
            finally:
                c.close()

    def list_capability_manifests(self, capability_id=None):
        c = self._conn()
        try:
            if capability_id is None:
                rows = c.execute(
                    "SELECT manifest_json FROM capability_manifests ORDER BY capability_id, provider_id, provider_version"
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT manifest_json FROM capability_manifests WHERE capability_id=? ORDER BY provider_id, provider_version",
                    (capability_id,),
                ).fetchall()
            return [json.loads(row["manifest_json"]) for row in rows]
        finally:
            c.close()

    # --- Engine v2 mission and workflow persistence ----------------------

    def create_mission(self, mission_id, objective, metadata=None):
        """Persist a mission objective; repeated identical creation is idempotent."""
        if not mission_id or not str(mission_id).strip() or not objective or not str(objective).strip():
            raise ValueError("mission id and objective are required")
        now = time.time()
        encoded = json.dumps(metadata or {}, sort_keys=True)
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "INSERT OR IGNORE INTO missions "
                    "(id, objective, metadata_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (mission_id, objective, encoded, now, now),
                )
                row = c.execute("SELECT objective, metadata_json FROM missions WHERE id=?", (mission_id,)).fetchone()
                if row["objective"] != objective or row["metadata_json"] != encoded:
                    raise ValueError("mission id already exists with different content")
                return self.get_mission(mission_id)
            finally:
                c.close()

    def get_mission(self, mission_id):
        c = self._conn()
        try:
            row = c.execute("SELECT * FROM missions WHERE id=?", (mission_id,)).fetchone()
            if row is None:
                return None
            value = dict(row)
            value["metadata"] = json.loads(value.pop("metadata_json") or "{}")
            return value
        finally:
            c.close()

    def save_workflow_plan(self, plan_id, plan):
        """Persist an immutable validated plan with plan-local task identifiers."""
        import uuid
        from .workflow import WorkflowPlan
        if isinstance(plan, dict):
            plan = WorkflowPlan.from_dict(plan)
        if not isinstance(plan, WorkflowPlan):
            raise TypeError("plan must be a WorkflowPlan or its dictionary representation")
        if not plan_id or not str(plan_id).strip():
            raise ValueError("plan_id is required")
        encoded = json.dumps(plan.to_dict(), sort_keys=True, separators=(",", ":"))
        task_refs = {
            task.id: uuid.uuid5(uuid.NAMESPACE_URL, f"whaxon:{plan_id}:{task.id}").hex
            for task in plan.tasks
        }
        now = time.time()
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                if c.execute("SELECT 1 FROM missions WHERE id=?", (plan.mission_id,)).fetchone() is None:
                    raise ValueError(f"unknown mission: {plan.mission_id}")
                existing = c.execute(
                    "SELECT digest FROM workflow_plans WHERE id=?", (plan_id,)
                ).fetchone()
                if existing:
                    if existing["digest"] != plan.digest:
                        raise ValueError("workflow plan ids are immutable; create a new plan id")
                    c.execute("COMMIT")
                    return False
                c.execute(
                    "INSERT INTO workflow_plans "
                    "(id, mission_id, schema_version, digest, plan_json, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (plan_id, plan.mission_id, plan.schema_version, plan.digest, encoded, now),
                )
                for task in plan.tasks:
                    c.execute(
                        "INSERT INTO workflow_tasks "
                        "(id, task_key, plan_id, capability_id, target, inputs_json, depends_on_json, "
                        "permissions_json, impact, timeout_s, idempotency_key, created_at, updated_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            task_refs[task.id], task.id, plan_id, task.capability_id, task.target,
                            json.dumps(task.inputs, sort_keys=True),
                            json.dumps([task_refs[dep] for dep in task.depends_on]),
                            json.dumps(task.permissions), task.impact, task.timeout_s,
                            task.idempotency_key, now, now,
                        ),
                    )
                c.execute("COMMIT")
                return True
            except Exception:
                if c.in_transaction:
                    c.execute("ROLLBACK")
                raise
            finally:
                c.close()

    def get_workflow_plan(self, plan_id):
        c = self._conn()
        try:
            row = c.execute("SELECT * FROM workflow_plans WHERE id=?", (plan_id,)).fetchone()
            if row is None:
                return None
            value = dict(row)
            value["plan"] = json.loads(value.pop("plan_json"))
            return value
        finally:
            c.close()

    def list_workflow_tasks(self, plan_id):
        c = self._conn()
        try:
            rows = c.execute(
                "SELECT id AS task_ref, task_key AS id, plan_id, capability_id, target, "
                "inputs_json, depends_on_json, permissions_json, impact, timeout_s, "
                "idempotency_key, status, result_json, error, active_attempt_id, "
                "created_at, updated_at FROM workflow_tasks WHERE plan_id=? ORDER BY rowid",
                (plan_id,),
            ).fetchall()
            result = []
            for row in rows:
                value = dict(row)
                for column, key in (
                    ("inputs_json", "inputs"), ("depends_on_json", "depends_on"),
                    ("permissions_json", "permissions"), ("result_json", "result"),
                ):
                    raw = value.pop(column)
                    value[key] = json.loads(raw) if raw else (None if key == "result" else [])
                result.append(value)
            return result
        finally:
            c.close()

    def reconcile_workflow_attempts(self):
        """Mark orphaned running attempts uncertain; never replay unknown side effects."""
        now = time.time()
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                rows = c.execute(
                    "SELECT id, task_id FROM task_attempts WHERE status='running'"
                ).fetchall()
                for row in rows:
                    error = "worker stopped before recording an outcome; reconcile before retry"
                    c.execute(
                        "UPDATE task_attempts SET status='uncertain', finished_at=?, error=? "
                        "WHERE id=? AND status='running'",
                        (now, error, row["id"]),
                    )
                    c.execute(
                        "UPDATE workflow_tasks SET status='uncertain', error=?, "
                        "active_attempt_id=NULL, updated_at=? "
                        "WHERE id=? AND status='running' "
                        "AND (active_attempt_id=? OR active_attempt_id IS NULL)",
                        (error, now, row["task_id"], row["id"]),
                    )
                c.execute("COMMIT")
                return len(rows)
            except Exception:
                if c.in_transaction:
                    c.execute("ROLLBACK")
                raise
            finally:
                c.close()

    def claim_ready_workflow_task(self, plan_id, worker_id, max_attempts=3):
        """Atomically claim a DAG node using plan-scoped task references."""
        import uuid
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                candidates = c.execute(
                    "SELECT * FROM workflow_tasks WHERE plan_id=? AND status IN ('pending','failed') "
                    "ORDER BY created_at, task_key", (plan_id,),
                ).fetchall()
                for row in candidates:
                    count = c.execute(
                        "SELECT COUNT(*) AS n FROM task_attempts WHERE task_id=?", (row["id"],)
                    ).fetchone()["n"]
                    if count >= max_attempts:
                        continue
                    dependency_refs = json.loads(row["depends_on_json"] or "[]")
                    dependencies = []
                    if dependency_refs:
                        marks = ",".join("?" for _ in dependency_refs)
                        states = c.execute(
                            f"SELECT id, task_key, status FROM workflow_tasks WHERE id IN ({marks})",
                            tuple(dependency_refs),
                        ).fetchall()
                        if len(states) != len(dependency_refs):
                            continue
                        state_by_ref = {item["id"]: item for item in states}
                        failed_terminal = False
                        for dependency_ref in dependency_refs:
                            dependency = state_by_ref[dependency_ref]
                            if dependency["status"] in ("blocked", "cancelled", "uncertain"):
                                failed_terminal = True
                                break
                            if dependency["status"] == "failed":
                                dep_attempts = c.execute(
                                    "SELECT COUNT(*) AS n FROM task_attempts WHERE task_id=?",
                                    (dependency_ref,),
                                ).fetchone()["n"]
                                if dep_attempts >= max_attempts:
                                    failed_terminal = True
                                    break
                        if failed_terminal:
                            c.execute(
                                "UPDATE workflow_tasks SET status='blocked', "
                                "error='dependency did not complete successfully', updated_at=? WHERE id=?",
                                (time.time(), row["id"]),
                            )
                            continue
                        if any(state_by_ref[ref]["status"] != "succeeded" for ref in dependency_refs):
                            continue
                        dependencies = [state_by_ref[ref]["task_key"] for ref in dependency_refs]
                    attempt_no = count + 1
                    attempt_id = uuid.uuid4().hex
                    now = time.time()
                    cur = c.execute(
                        "UPDATE workflow_tasks SET status='running', active_attempt_id=?, "
                        "error=NULL, updated_at=? WHERE id=? AND status IN ('pending','failed')",
                        (attempt_id, now, row["id"]),
                    )
                    if cur.rowcount != 1:
                        continue
                    c.execute(
                        "INSERT INTO task_attempts "
                        "(id, task_id, attempt_no, status, worker_id, idempotency_key, started_at) "
                        "VALUES (?, ?, ?, 'running', ?, ?, ?)",
                        (attempt_id, row["id"], attempt_no, worker_id, row["idempotency_key"], now),
                    )
                    value = dict(row)
                    value.update({
                        "attempt_id": attempt_id, "attempt_no": attempt_no,
                        "worker_id": worker_id, "status": "running",
                        "task_ref": row["id"], "id": row["task_key"],
                        "inputs": json.loads(row["inputs_json"] or "{}"),
                        "depends_on": dependencies,
                        "permissions": json.loads(row["permissions_json"] or "[]"),
                    })
                    c.execute("COMMIT")
                    return value
                c.execute("COMMIT")
                return None
            except Exception:
                if c.in_transaction:
                    c.execute("ROLLBACK")
                raise
            finally:
                c.close()

    def start_task_attempt(
        self, attempt_id, task_id, attempt_no, worker_id="", idempotency_key="", plan_id=None,
    ):
        """Create one fenced attempt; task_id may be plan-local when unambiguous."""
        now = time.time()
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                if plan_id is None:
                    matches = c.execute(
                        "SELECT id FROM workflow_tasks WHERE id=? OR task_key=? LIMIT 2",
                        (task_id, task_id),
                    ).fetchall()
                    if len(matches) > 1:
                        raise ValueError("task id is ambiguous; supply plan_id")
                    task_ref = matches[0]["id"] if matches else None
                else:
                    match = c.execute(
                        "SELECT id FROM workflow_tasks WHERE plan_id=? AND (id=? OR task_key=?)",
                        (plan_id, task_id, task_id),
                    ).fetchone()
                    task_ref = match["id"] if match else None
                if task_ref is None:
                    raise ValueError(f"unknown workflow task: {task_id}")
                task = c.execute(
                    "SELECT status, idempotency_key FROM workflow_tasks WHERE id=?", (task_ref,)
                ).fetchone()
                if task["status"] in ("succeeded", "cancelled", "blocked", "uncertain"):
                    raise ValueError(f"task is terminal: {task_id}")
                if task["status"] == "running":
                    raise ValueError(f"task already has an active attempt: {task_id}")
                if task["status"] not in ("pending", "failed"):
                    raise ValueError(f"task is not claimable: {task_id}")
                if task["idempotency_key"] and idempotency_key != task["idempotency_key"]:
                    raise ValueError("task attempt idempotency key mismatch")
                c.execute(
                    "INSERT INTO task_attempts "
                    "(id, task_id, attempt_no, status, worker_id, idempotency_key, started_at) "
                    "VALUES (?, ?, ?, 'running', ?, ?, ?)",
                    (attempt_id, task_ref, int(attempt_no), worker_id, idempotency_key, now),
                )
                cur = c.execute(
                    "UPDATE workflow_tasks SET status='running', active_attempt_id=?, "
                    "error=NULL, updated_at=? WHERE id=? AND status IN ('pending','failed')",
                    (attempt_id, now, task_ref),
                )
                if cur.rowcount != 1:
                    raise ValueError(f"task is already claimed: {task_id}")
                c.execute("COMMIT")
                return True
            except Exception:
                if c.in_transaction:
                    c.execute("ROLLBACK")
                raise
            finally:
                c.close()

    def finish_task_attempt(self, attempt_id, status, result=None, error=""):
        """Record an attempt outcome and update its task in one transaction."""
        if status not in ("succeeded", "failed", "cancelled", "uncertain", "blocked"):
            raise ValueError(f"invalid terminal attempt status: {status}")
        now = time.time()
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                row = c.execute(
                    "SELECT task_id, status FROM task_attempts WHERE id=?", (attempt_id,)
                ).fetchone()
                if row is None:
                    raise ValueError(f"unknown task attempt: {attempt_id}")
                if row["status"] != "running":
                    raise ValueError("task attempt is already terminal")
                encoded = json.dumps(result, sort_keys=True) if result is not None else None
                c.execute(
                    "UPDATE task_attempts SET status=?, finished_at=?, result_json=?, error=? WHERE id=?",
                    (status, now, encoded, error, attempt_id),
                )
                cur = c.execute(
                    "UPDATE workflow_tasks SET status=?, result_json=?, error=?, "
                    "active_attempt_id=NULL, updated_at=? "
                    "WHERE id=? AND status='running' AND active_attempt_id=?",
                    (status, encoded, error, now, row["task_id"], attempt_id),
                )
                if cur.rowcount != 1:
                    raise ValueError("stale task attempt cannot update the workflow task")
                c.execute("COMMIT")
                return True
            except Exception:
                if c.in_transaction:
                    c.execute("ROLLBACK")
                raise
            finally:
                c.close()

    # --- AI runs ---------------------------------------------------------

    def create_ai_run(self, run_id, goal, provider="null", phase="recon", owner="local"):
        with self._lock:
            c = self._conn()
            try: c.execute("INSERT OR IGNORE INTO ai_runs (id, goal, provider, status, started_at, phase, owner) VALUES (?, ?, ?, 'running', ?, ?, ?)", (run_id, goal, provider, time.time(), phase, owner))
            finally: c.close()

    def append_ai_run_step(self, run_id, seq, action_json, result_json):
        with self._lock:
            c = self._conn()
            try: c.execute("INSERT OR REPLACE INTO ai_run_steps (run_id, seq, action_json, result_json, created_at) VALUES (?, ?, ?, ?, ?)", (run_id, seq, json.dumps(action_json), json.dumps(result_json), time.time()))
            finally: c.close()

    def set_ai_run_phase(self, run_id, phase, history_entry=None):
        with self._lock:
            c = self._conn()
            try:
                row = c.execute("SELECT phase_history FROM ai_runs WHERE id=?", (run_id,)).fetchone()
                history = json.loads(row["phase_history"]) if row and row["phase_history"] else []
                if history_entry is None:
                    history_entry = {"phase": phase, "at": time.time()}
                history.append(history_entry)
                c.execute("UPDATE ai_runs SET phase=?, phase_history=? WHERE id=?", (phase, json.dumps(history), run_id))
            finally: c.close()

    def set_ai_run_waiting(self, run_id, question_json):
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "UPDATE ai_runs SET status='waiting', pending_question=? WHERE id=?",
                    (question_json, run_id),
                )
            finally: c.close()

    def add_approval(self, run_id, seq, user, answer, note=""):
        """Record an answer and clear the run's waiting state.

        An approval answers the pending question, so the run is no
        longer waiting on it. Resume moves the run forward; if the
        loop pauses again, set_ai_run_waiting re-sets 'waiting'.
        """
        with self._lock:
            c = self._conn()
            try:
                c.execute("INSERT OR REPLACE INTO approvals (run_id, seq, user, answer, note, at) VALUES (?, ?, ?, ?, ?, ?)", (run_id, int(seq), user, answer, note, time.time()))
                c.execute("UPDATE ai_runs SET status='running', pending_question='' WHERE id=? AND status='waiting'", (run_id,))
            finally: c.close()

    def list_approvals(self, run_id):
        c = self._conn()
        try:
            rows = c.execute("SELECT run_id, seq, user, answer, note, at FROM approvals WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
            return [dict(r) for r in rows]
        finally: c.close()

    def last_approval(self, run_id):
        """Return the latest approval row for a run, or None."""
        c = self._conn()
        try:
            row = c.execute(
                "SELECT run_id, seq, user, answer, note, at "
                "FROM approvals WHERE run_id=? ORDER BY seq DESC LIMIT 1",
                (run_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            c.close()

    def list_pending_runs(self, owner=None):
        c = self._conn()
        try:
            base = "SELECT id, goal, owner, phase, pending_question, started_at FROM ai_runs WHERE status='waiting'"
            if owner:
                rows = c.execute(base + " AND owner=? ORDER BY started_at DESC", (owner,)).fetchall()
            else:
                rows = c.execute(base + " ORDER BY started_at DESC").fetchall()
            out = []
            for r in rows:
                d = dict(r)
                pq = d.get("pending_question")
                if isinstance(pq, str) and pq:
                    try:
                        d["pending_question"] = json.loads(pq)
                    except (ValueError, TypeError):
                        d["pending_question"] = None
                out.append(d)
            return out
        finally: c.close()

    def set_ai_run_usage(self, run_id, tokens_in, tokens_out, cost_usd=None):
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "UPDATE ai_runs SET tokens_in=?, tokens_out=?, cost_usd=? WHERE id=?",
                    (int(tokens_in), int(tokens_out), cost_usd, run_id),
                )
            finally: c.close()

    def set_ai_run_consecutive_failures(self, run_id, count):
        with self._lock:
            c = self._conn()
            try:
                c.execute(
                    "UPDATE ai_runs SET consecutive_failures=? WHERE id=?",
                    (int(count), run_id),
                )
            finally: c.close()

    def set_ai_run_finished(self, run_id, status="done", error=""):
        with self._lock:
            c = self._conn()
            try: c.execute("UPDATE ai_runs SET status=?, finished_at=?, error=? WHERE id=?", (status, time.time(), error, run_id))
            finally: c.close()

    def get_ai_run(self, run_id):
        c = self._conn()
        try:
            row = c.execute("SELECT * FROM ai_runs WHERE id=?", (run_id,)).fetchone()
            if row is None: return None
            out = dict(row)
            steps = c.execute("SELECT seq, action_json, result_json, created_at FROM ai_run_steps WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
            out["steps"] = [{"seq": r["seq"], "action": json.loads(r["action_json"]), "result": json.loads(r["result_json"]), "created_at": r["created_at"]} for r in steps]
            return out
        finally: c.close()

    def list_ai_runs(self, limit=50):
        c = self._conn()
        try:
            rows = c.execute("SELECT id, goal, provider, status, started_at, finished_at, error, phase FROM ai_runs ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally: c.close()

    def lines_since(self, job_id, since_seq=0):
        c = self._conn()
        try:
            rows = c.execute("SELECT seq, stream, text FROM lines WHERE job_id=? AND seq>=? ORDER BY seq", (job_id, since_seq)).fetchall()
            return [{"seq": r["seq"], "stream": r["stream"], "text": r["text"]} for r in rows]
        finally: c.close()