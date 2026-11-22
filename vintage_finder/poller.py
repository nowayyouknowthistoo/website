"""Keeps every site searching non-stop: your watches first, then the broad fresh searches, then the band list.

Each site runs in its own thread, one request every REQUEST_GAP_SECONDS, always picking whichever search is
most overdue. New listings are stored the moment they're seen and the page picks them up within seconds.
"""

import json
import threading
import time
import traceback
from pathlib import Path

from . import config
from .net import session
from .sources import depop, ebay, poshmark, vinted

SOURCES = {"depop": depop, "ebay": ebay, "poshmark": poshmark, "vinted": vinted}


def load_watches():
    try:
        return [w for w in json.loads(Path(config.WATCHES_PATH).read_text()) if isinstance(w, str) and w.strip()]
    except (OSError, ValueError):
        return []


def save_watches(watches):
    Path(config.WATCHES_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(config.WATCHES_PATH).write_text(json.dumps(watches, indent=1))


def jobs():
    """(query, band hint, re-run interval) for everything that should be searched."""
    out = [(w, w.title(), config.WATCH_SECONDS) for w in load_watches()]
    out += [(q, None, config.FRESH_SECONDS) for q in config.FRESH]
    out += [(q, band, config.BAND_SECONDS) for band, qs in config.SEARCHES.items() for q in qs]
    return out


def run_one(store, site, s, q, band, log=print):
    try:
        items = SOURCES[site].search(q, s)
        new = store.save(items, query=q, band_hint=band)
        store.log_run(site, q, len(items), new)
        if new:
            log(f"  {site:8} +{new:3} new  '{q}'")
        return new
    except Exception as e:  # one bad site or search shouldn't stop the rest
        store.log_run(site, q, 0, 0, f"{type(e).__name__}: {e}"[:300])
        log(f"  {site:8} failed '{q}': {type(e).__name__}: {str(e)[:120]}")
        return 0


def site_loop(store, site, log=print):
    s, last_run = session(), {}
    while True:
        try:
            now = time.time()
            # Most overdue first; a search never run (e.g. a watch you just added) is the most overdue of all.
            q, band, every = max(jobs(), key=lambda j: (now - last_run.get(j[0], 0)) / j[2])
            if now - last_run.get(q, 0) < every:
                time.sleep(1)
                continue
            last_run[q] = now
            run_one(store, site, s, q, band, log)
        except Exception:
            traceback.print_exc()
        time.sleep(config.REQUEST_GAP_SECONDS)


def forever(store, log=print):
    for site in config.SITES:
        threading.Thread(target=site_loop, args=(store, site, log), daemon=True).start()
    while True:
        time.sleep(3600)


def run_once(store, sites=None, log=print):
    s, total = session(), 0
    for site in sites or config.SITES:
        for q, band, _ in jobs():
            total += run_one(store, site, s, q, band, log)
            time.sleep(config.REQUEST_GAP_SECONDS)
    return total
