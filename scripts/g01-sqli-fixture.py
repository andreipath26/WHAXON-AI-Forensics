from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
        value = query.get("id", [""])[0].lower()
        if path == "/health":
            status, body = 200, b"ok"
        elif path in {"/admin", "/robots.txt"}:
            status, body = 200, b"fixture"
        elif path == "/search":
            # Deterministic boolean oracle for the fixed SQLmap smoke. A quote
            # probe emits a parser marker; boolean conditions vary only a
            # constant response and never access or mutate a database.
            if "'" in value:
                status, body = 500, b"SQLite error: near quote: syntax error"
            elif " and " in value and any(a != b for a, b in __import__("re").findall(r"(\d+)=(\d+)", value)):
                status, body = 200, b"No products found"
            else:
                status, body = 200, b"Product: fixture-item"
        else:
            status, body = 404, b"not found"
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
