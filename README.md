# Vintage inventory finder

Pulls listings from **Poshmark** and **Vinted** and keeps the ones that fit the shop's formula:

- **Item type:** t-shirts, crewneck sweatshirts, snapbacks only (hoodies, jackets, jerseys, tanks, crop/baby tees, kids sizes are dropped)
- **Niche:** music / bands / rap, pop culture (movies, TV, games, wrestling, comics), cartoons, sports
- **Vintage tells raise the score:** single stitch, made in USA, a year of 2005 or earlier, 80s/90s, tags like Screen Stars, Brockum, Giant, Winterland, Stedman, Starter, Logo 7, Salem, Nutmeg, AJD
- **Red flags lower it:** "vintage style", reprint/repro, Gildan/Softstyle, mall retailers (Hot Topic, Urban Outfitters, H&M), licensed-reissue labels (Junk Food, Amplified), a recent year

Each match gets a score: **9+ = strong lead**, **6–8 = possible**. All the keyword lists and weights live in `inventory_finder/formula.py`. Edit them to tune what gets through. Search terms are in `inventory_finder/queries.py`.

## Output

`output/leads.html` is a sortable, filterable lead sheet (tier, site, item type, max price, title search).
`output/leads.csv` has the same leads for a spreadsheet, and `output/all_scored.csv` has every listing scanned with the reason it was kept or dropped.

## Running it

```bash
pip install requests beautifulsoup4

# Live scrape. Run this from your own computer.
python -m inventory_finder

# Only cheap stuff, only strong leads, only Vinted
python -m inventory_finder --max-price 30 --min-score 9 --sites vinted

# Re-score the saved first pull (no network needed)
python -m inventory_finder --from-tinyfish data/raw/*.json
```

The first pull (`data/raw/`) was made through the TinyFish web fetcher, because the cloud environment it was built in can't reach either site directly. The live mode (`inventory_finder/live.py`) calls the sites directly: Poshmark search pages are parsed from HTML, and Vinted uses its public catalog API. Both sites change their pages and may rate-limit scrapers, so the script waits 3 seconds between searches. If a site starts returning 0 listings, its selectors or API probably changed.
