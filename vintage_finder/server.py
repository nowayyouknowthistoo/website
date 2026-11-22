"""Local web page: http://localhost:<PORT>/ shows the listings.

  GET  /api/listings[?after=<unix time>][&old=1]   newly posted listings (only newer ones with after;
                                                   old=1 adds what was already up), status and watches
  POST /api/watch    {"add": "..."} or {"remove": "..."}   change the Watch list
"""

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .poller import load_watches, save_watches

PAGE = (Path(__file__).parent / "page.html").read_text()


def serve(store, port):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, body, ctype="application/json"):
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/api/listings":
                qs = parse_qs(u.query)
                after = float((qs.get("after") or ["0"])[0] or 0)
                old = (qs.get("old") or ["0"])[0] == "1"
                self.reply(json.dumps({"listings": store.listings(after=after, include_old=old), "status": store.status(), "counts": store.counts(),
                                       "watches": load_watches(), "now": time.time()}).encode())
            elif u.path in ("/", "/index.html"):
                self.reply(PAGE.encode(), "text/html; charset=utf-8")
            else:
                self.send_error(404)

        def do_POST(self):
            if urlparse(self.path).path != "/api/watch":
                self.send_error(404)
                return
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            except ValueError:
                self.send_error(400)
                return
            watches = load_watches()
            add, remove = str(req.get("add") or "").strip()[:80], str(req.get("remove") or "").strip()
            if add and add.lower() not in (w.lower() for w in watches):
                watches.insert(0, add)
            if remove:
                watches = [w for w in watches if w.lower() != remove.lower()]
            save_watches(watches)
            self.reply(json.dumps({"watches": watches}).encode())

        def log_message(self, *a):
            pass

    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
