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
create table if not exists searched (site text, query text, primary key (site, query));
"""


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        cols = {r[1] for r in self.db.execute("pragma table_info(listings)")}
        if "baseline" not in cols:  # older databases: everything already stored counts as old
            self.db.execute("alter table listings add column baseline int default 1")
            self.db.commit()
        self.lock = threading.Lock()

    def save(self, items, query="", band_hint=None, site=None, old=False):
        """Insert new listings, refresh known ones. Returns how many were newly posted.

        The first time a search runs on a site, everything it returns was already up before we started
        looking, so those listings are stored as baseline (old) and never shown as new.
        """
        now, new = time.time(), 0
        with self.lock, self.db:
            first_run = old
            if site and items:  # an empty or blocked result doesn't count as the first look
                first_run = self.db.execute("insert or ignore into searched values (?,?)", (site, query)).rowcount == 1
            for it in items:
                v = analyse(it["title"], it.get("brand", ""), it.get("desc", ""), it.get("price"))
                band = v["band"] or band_hint or "Other band"
                if not v["shirt"]:
                    continue
                key = f'{it["site"]}:{it["id"]}'
                cur = self.db.execute("update listings set price=?, was=?, last_seen=? where key=?",
                                      (it.get("price"), it.get("was"), now, key))
                if cur.rowcount:
                    continue
                new += not first_run
                self.db.execute(
                    "insert into listings values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (key, it["site"], it["url"], it["title"], it.get("price"), it.get("was"), it.get("size", ""),
                     it.get("brand", ""), it.get("image", ""), it.get("desc", ""), band, query, v["score"],
                     int(v["modern"]), json.dumps(v["flags"]), v["tag"], it.get("first_seen", now), now, int(first_run)))
        return new

    def log_run(self, site, query, found, new, error=""):
        with self.lock, self.db:
            self.db.execute("insert into runs values (?,?,?,?,?,?)", (site, query, time.time(), found, new, error))

    def listings(self, since_days=30, limit=3000, after=0.0, include_old=False):
        """Newly posted listings (not the baseline found by each search's first run), newest first.
        With after, only those first seen after that time; include_old adds the baseline ones."""
        rows = self.db.execute("select * from listings where last_seen > ? and first_seen > ? "
                               "and (baseline = 0 or ?) order by first_seen desc limit ?",
                               (time.time() - since_days * 86400, after, int(include_old), limit)).fetchall()
        return [{**dict(r), "flags": json.loads(r["flags"])} for r in rows]

    def counts(self):
        r = self.db.execute("select count(*) n, sum(baseline = 1) old from listings").fetchone()
        return {"total": r["n"] or 0, "already_up": r["old"] or 0, "new": (r["n"] or 0) - (r["old"] or 0)}

    def status(self):
        rows = self.db.execute(
            "select site, max(at) at, sum(new) new, sum(found) found, sum(error != '') errors, count(*) runs, "
            "(select error from runs r2 where r2.site = runs.site and r2.error != '' order by at desc limit 1) last_error "
            "from runs where at > ? group by site", (time.time() - 600,)).fetchall()
        return [dict(r) for r in rows]
