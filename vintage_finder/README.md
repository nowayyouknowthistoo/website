# Vintage Finder

A gem.com-style search page for vintage band and rap shirts that runs on your own computer. It searches
Depop, eBay, Poshmark and Vinted **non-stop**, newest first, and new finds appear on the page within seconds
(the page checks for new listings every 3 seconds; turn on **Sound on new** for a ping).

- **Watch box:** type any search (a band, a tour, a year, a misspelling) and press Watch. It's searched on every
  site right away and then about every 45 seconds, ahead of everything else. Remove it with ×.
- **Fresh searches:** broad searches like "vintage band tee", "single stitch band tee", "vintage concert shirt" and
  "vintage rap tee" run about once a minute on every site, so shirts from bands *not* on your list still show up
  (under **Other band**).
- **Your band list** (Nirvana, Sade, Sub Pop bands, Pumpkins, Soundgarden, Oasis, Green Day, Radiohead, NIN,
  Wu-Tang, Tupac and other rap tees, and more) is searched in rotation, each search about every 10 minutes.
- **Hide reprints & modern**, **Looks 90s only**, **Underpriced only**, **New since last visit**, tag filter
  (old tag / no tag), site and max price filters.

## Start it

1. Install Python 3.10+ from python.org if you don't have it.
2. Double-click **start-mac.command** (Mac) or **start-windows.bat** (Windows) in the repo folder.
   The first start installs what it needs. Your browser then opens http://localhost:8765.
3. Leave the window open. New listings show up on the page by themselves within seconds.

From a terminal instead: `pip install -r requirements.txt` then `python -m vintage_finder`.

## Make eBay faster and more reliable (optional, free)

Create a free eBay developer account at https://developer.ebay.com, make a production keyset,
and start the finder with:

    EBAY_CLIENT_ID=your-app-id EBAY_CLIENT_SECRET=your-cert-id python -m vintage_finder

It then uses eBay's official search API instead of the public search page.

## Change what it looks for

Easiest: use the Watch box on the page. For permanent changes edit `vintage_finder/config.py`: bands and
searches in `SEARCHES`, broad searches in `FRESH`, and the timers `WATCH_SECONDS`, `FRESH_SECONDS`, `BAND_SECONDS`.
The rules for what counts as vintage, modern or underpriced are in `vintage_finder/vintage.py`.

## If a site shows "blocked" on the page

Sites sometimes rate-limit. The finder keeps going with the other sites and retries next pass.
Each site gets one request every `REQUEST_GAP_SECONDS` (3 s). If a site is blocked often, raise it to 5–8.
