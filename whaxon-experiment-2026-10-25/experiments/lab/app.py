"""Real SQLite-backed lab fixture with genuine ground truth.

Why this exists (replaces the string-simulated benchmark used earlier):
sqlmap performs heuristic and differential probing; a page that merely prints
an error string for any quote is not a credible injection target, and sqlmap
correctly reported "does not seem to be injectable" (job 6f5b6e2a80f7). The
fixture is therefore fixed so that ground truth is produced by a real database
engine rather than by string comparison.

Endpoints (same shape as DVWA's SQLi module):

    /low?id=N    string concatenation into the query  -> genuinely injectable
    /safe?id=N   parameterized query (bound parameter) -> NOT injectable

Ground truth is by construction:
    low  = SELECT ... WHERE user_id = '<id>'      (unescaped concatenation)
    safe = SELECT ... WHERE user_id = ?           (bound parameter)

Behavioural checks are in ground_truth.py; they are what the experiment scores
against, not the comments above.
"""
from __future__ import annotations

import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DB = Path(__file__).resolve().parent / "lab.db"
PAGE = "<html><body><h1>{case}</h1>{body}</body></html>"


def init_db() -> None:
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)")
    con.executemany("INSERT INTO users VALUES (?,?,?)",
                    [(1, "admin", "admin"), (2, "gordonb", "brown"), (3, "1337", "me")])
    con.commit()
    con.close()


def query(sql: str) -> str:
    """Run a query and render rows the way DVWA does.

    SQLite errors are rendered into the response body, mirroring a PHP
    deployment with display_errors=On (the configuration observed on the
    authorised DVWA target). Without this, the client sees an empty 200 and
    error-based detection has nothing to work with.
    """
    con = sqlite3.connect(DB)
    try:
        rows = con.execute(sql).fetchall()
    except sqlite3.Error as exc:
        return ("<br /><pre>Fatal error: Uncaught SQLiteException: "
                f"{exc} in {sql!r} on line 1</pre>")
    finally:
        con.close()
    if not rows:
        return "<p>ID: not in the database</p>"
    return "".join(f"<p>ID: {r[0]} :: First name: {r[1]} :: Surname: {r[2]}</p>" for r in rows)


def query_safe(value: str) -> str:
    """Bound-parameter query: the value can never change query structure."""
    con = sqlite3.connect(DB)
    try:
        rows = con.execute(
            "SELECT user_id, first_name, last_name FROM users WHERE user_id = ?",
            (value,)).fetchall()
    except sqlite3.Error as exc:
        return f"<br /><pre>Fatal error: Uncaught SQLiteException: {exc}</pre>"
    finally:
        con.close()
    if not rows:
        return "<p>ID: not in the database</p>"
    return "".join(f"<p>ID: {r[0]} :: First name: {r[1]} :: Surname: {r[2]}</p>" for r in rows)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        case = parsed.path.strip("/")
        q = {k: v[0] for k, v in parse_qs(parsed.query, keep_blank_values=True).items()}
        if case == "low":
            # DVWA low: unsanitised string concatenation.
            body = query(f"SELECT user_id, first_name, last_name FROM users "
                         f"WHERE user_id = '{q.get('id', '')}'")
        elif case == "safe":
            # Parameterized: the value can never change the query structure.
            body = query_safe(q.get("id", ""))
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        raw = PAGE.format(case=case, body=body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def serve(port: int) -> ThreadingHTTPServer:
    init_db()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


if __name__ == "__main__":
    srv = serve(8100)
    print(f"lab listening on http://127.0.0.1:{srv.server_address[1]}")
    threading.Event().wait()
