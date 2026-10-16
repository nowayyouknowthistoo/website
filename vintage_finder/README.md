# Vintage Finder

A gem.com-style search page for vintage band shirts that runs on your own computer. It searches
Depop, eBay, Poshmark and Vinted every 5 minutes for 90s Nirvana and Red Hot Chili Peppers
shirts, newest first, and shows them on one page with vintage filters:

- **Hide reprints & modern:** drops listings whose title or description says reprint, brand new,
  Gildan, Hot Topic, H&M, Bravado and so on.
- **Tag filter:** old tag (Giant, Brockum, Screen Stars, Oneita, Tultex…) or no tag / cut tag.
- **Looks 90s only:** needs at least one sign of age (single stitch, 80s/90s date, old tag, made in USA,
  bootleg, original owner).
- **Underpriced only:** strong signs of age at a low price.
- **New since last visit:** only what showed up since you last opened the page.
- Misspelled titles (Nirvanna, Kurt Kobain, Red Hot Chilli…) are searched on purpose and flagged.

## Start it

1. Install Python 3.10+ from python.org if you don't have it.
2. Double-click **start-mac.command** (Mac) or **start-windows.bat** (Windows) in the repo folder.
   The first start installs what it needs. Your browser then opens http://localhost:8765.
3. Leave the window open. New listings show up on the page by themselves (it refreshes every 30 s).

From a terminal instead: `pip install -r requirements.txt` then `python -m vintage_finder`.

## Make eBay faster and more reliable (optional, free)

Create a free eBay developer account at https://developer.ebay.com, make a production keyset,
and start the finder with:

    EBAY_CLIENT_ID=your-app-id EBAY_CLIENT_SECRET=your-cert-id python -m vintage_finder

It then uses eBay's official search API instead of the public search page.

## Change what it looks for

Edit `vintage_finder/config.py`: add bands or searches to `SEARCHES`, change `POLL_MINUTES`.
The rules for what counts as vintage, modern or underpriced are in `vintage_finder/vintage.py`.

## If a site shows "blocked" on the page

Sites sometimes rate-limit. The finder keeps going with the other sites and retries next pass.
Raise `REQUEST_GAP_SECONDS` in config.py if one site is blocked often.
