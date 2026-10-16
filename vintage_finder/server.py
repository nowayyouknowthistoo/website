"""Local web page: http://localhost:<PORT>/ shows the listings, /api/listings serves them as JSON."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = (Path(__file__).parent / "page.html").read_text()


def serve(store, port):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/api/listings"):
                body = json.dumps({"listings": store.listings(), "status": store.status()}).encode()
                ctype = "application/json"
            elif self.path in ("/", "/index.html"):
                body, ctype = PAGE.encode(), "text/html; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
