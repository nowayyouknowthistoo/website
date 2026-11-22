# Vintage Finder

An inbox of **newly posted** vintage shirts from Depop, eBay, Poshmark and Vinted, running on your own computer.

- **Only new posts.** The first time each search runs, it just learns what's already listed (hidden). From then on,
  anything that shows up is a fresh post and lands in your inbox. "Include ones already up" shows the rest.
- **Look, then refresh.** The page checks every 3 seconds but doesn't move while you're looking. New finds collect in
  the red **▲ N new shirts posted — show** button at the top (and the tab title). Click it, or press **R**, to see them.
  Listings you've opened are dimmed; "Hide ones I opened" removes them.
- **Search for anything.** Type in the **Watch** box: a band, "t shirt", "band shirt", "metallica", "pink floyd", a
  misspelling. It's searched on every site right away and then about every 45 seconds.
- **Not limited to band names.** Broad searches ("band shirt", "vintage t shirt", "vintage concert shirt", "vintage rap
  tee"…) run about every 90 seconds, and every shirt they find is kept even if the title doesn't name a band
  (shown as **Other band**). Only non-shirts (hats, pants, shoes, posters, vinyl…) are dropped.
- **Your bands** (Nirvana, Sade, Sub Pop bands, Pumpkins, Soundgarden, Oasis, Green Day, Radiohead, NIN, Metallica,
  Pink Floyd, Wu-Tang, Tupac and other rap tees, and more) are each checked about every 2 minutes.
- Filters: hide reprints & modern, looks 90s only, underpriced only, old tag / no tag, site, max price, sound on new.

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
