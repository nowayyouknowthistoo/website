"""Vintage Finder: searches Depop, eBay, Poshmark and Vinted every few minutes and shows
new 90s Nirvana / RHCP shirts on a local web page.

  python -m vintage_finder              # search forever + open http://localhost:8765
  python -m vintage_finder --once       # one search pass, then exit
  python -m vintage_finder --sites ebay vinted
"""

import argparse
import threading
import webbrowser

from . import config
from .poller import forever, run_once
from .seed import import_saved
from .server import serve
from .store import Store


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--once", action="store_true", help="run one search pass and exit")
    ap.add_argument("--sites", nargs="+", choices=config.SITES, help="only search these sites")
    ap.add_argument("--no-browser", action="store_true", help="don't open the page automatically")
    args = ap.parse_args()
    if args.sites:
        config.SITES = args.sites

    store = Store(config.DB_PATH)
    import_saved(store)
    if args.once:
        print(f"{run_once(store)} new listings")
        return
    threading.Thread(target=forever, args=(store,), daemon=True).start()
    url = f"http://localhost:{config.PORT}/"
    print(f"Vintage Finder running at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        serve(store, config.PORT)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
