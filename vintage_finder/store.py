"""SQLite storage: every listing ever seen, when it was first seen, and its vintage verdict."""

import json
import sqlite3
import threading
import time
from pathlib import Path

from .vintage import analyse

SCHEMA = """
create table if not exists listings (
  key text primary key, site text, url text, title text, price real, was real, size text, brand text,
  image text, descr text, band text, query text, score int, modern int, flags text, tag text,
  first_seen real, last_seen real
);
create index if not exists by_seen on listings(first_seen);
create table if not exists runs (site text, query text, at real, found int, new int, error text);
"""


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.lock = threading.Lock()

    def save(self, items, query="", band_hint=None):
        """Insert new listings, refresh known ones. Returns how many were new."""
        now, new = time.time(), 0
        with self.lock, self.db:
            for it in items:
                v = analyse(it["title"], it.get("brand", ""), it.get("desc", ""), it.get("price"))
                band = v["band"] or band_hint
                if not band or not v["shirt"]:
                    continue
                key = f'{it["site"]}:{it["id"]}'
                cur = self.db.execute("update listings set price=?, was=?, last_seen=? where key=?",
                                      (it.get("price"), it.get("was"), now, key))
                if cur.rowcount:
                    continue
                new += 1
                self.db.execute(
                    "insert into listings values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (key, it["site"], it["url"], it["title"], it.get("price"), it.get("was"), it.get("size", ""),
                     it.get("brand", ""), it.get("image", ""), it.get("desc", ""), band, query, v["score"],
                     int(v["modern"]), json.dumps(v["flags"]), v["tag"], it.get("first_seen", now), now))
        return new

    def log_run(self, site, query, found, new, error=""):
        with self.lock, self.db:
            self.db.execute("insert into runs values (?,?,?,?,?,?)", (site, query, time.time(), found, new, error))

    def listings(self, since_days=30, limit=3000):
        rows = self.db.execute("select * from listings where last_seen > ? order by first_seen desc limit ?",
                               (time.time() - since_days * 86400, limit)).fetchall()
        return [{**dict(r), "flags": json.loads(r["flags"])} for r in rows]

    def status(self):
        rows = self.db.execute(
            "select site, max(at) at, sum(new) new, sum(error != '') errors, count(*) runs "
            "from runs where at > ? group by site", (time.time() - 3600,)).fetchall()
        return [dict(r) for r in rows]
