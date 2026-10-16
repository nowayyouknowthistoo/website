"""Re-runs every saved search on every site, forever, and stores what's new."""

import time
import traceback

from . import config
from .net import session
from .sources import depop, ebay, poshmark, vinted

SOURCES = {"depop": depop, "ebay": ebay, "poshmark": poshmark, "vinted": vinted}


def run_once(store, sites=None, log=print):
    s = session()
    total_new = 0
    for site in sites or config.SITES:
        for band, queries in config.SEARCHES.items():
            for q in queries:
                try:
                    items = SOURCES[site].search(q, s)
                    new = store.save(items, query=q, band_hint=band)
                    store.log_run(site, q, len(items), new)
                    total_new += new
                    if new:
                        log(f"  {site:8} +{new:3} new  '{q}'")
                except Exception as e:  # one bad site or search shouldn't stop the rest
                    store.log_run(site, q, 0, 0, f"{type(e).__name__}: {e}"[:300])
                    log(f"  {site:8} failed '{q}': {type(e).__name__}: {str(e)[:120]}")
                time.sleep(config.REQUEST_GAP_SECONDS)
    return total_new


def forever(store, log=print):
    while True:
        started = time.time()
        try:
            n = run_once(store, log=log)
            log(f"pass done: {n} new listings in {time.time() - started:.0f}s")
        except Exception:
            traceback.print_exc()
        time.sleep(max(0, config.POLL_MINUTES * 60 - (time.time() - started)))
