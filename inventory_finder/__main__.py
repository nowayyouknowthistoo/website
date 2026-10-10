"""Find vintage tees / crewnecks / snapbacks on Poshmark and Vinted.

  python -m inventory_finder                 # live scrape (run on your own computer)
  python -m inventory_finder --from-tinyfish data/raw/*.json
  python -m inventory_finder --max-price 40 --min-score 6
"""

import argparse
from pathlib import Path

from .formula import MIN_SCORE, evaluate
from .queries import QUERIES
from .report import write_csv, write_html


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-tinyfish", nargs="+", metavar="JSON",
                    help="parse saved TinyFish fetch results instead of scraping live")
    ap.add_argument("--sites", nargs="+", default=list(QUERIES), choices=list(QUERIES))
    ap.add_argument("--min-score", type=int, default=MIN_SCORE)
    ap.add_argument("--max-price", type=float, help="drop listings above this price")
    ap.add_argument("--out", default="output", help="output folder")
    args = ap.parse_args()

    if args.from_tinyfish:
        from .tinyfish_ingest import load
        listings = load(args.from_tinyfish)
    else:
        from .live import fetch_all
        listings = fetch_all({s: QUERIES[s] for s in args.sites})
    listings = [l for l in listings if l.site in args.sites]

    seen, unique = set(), []
    for l in listings:
        if l.url not in seen:
            seen.add(l.url)
            unique.append(l)

    scored = [(l, evaluate(l.title, l.brand, l.size, l.price)) for l in unique]
    matches = [(l, v) for l, v in scored
               if v.match and v.score >= args.min_score
               and (args.max_price is None or (l.price or 0) <= args.max_price)]
    matches.sort(key=lambda lv: (-lv[1].score, lv[0].price or 0))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(matches, out / "leads.csv")
    write_csv(sorted(scored, key=lambda lv: -lv[1].score), out / "all_scored.csv")
    stats = (f"{len(unique)} listings scanned ({len(listings) - len(unique)} duplicates removed), "
             f"{len(matches)} match the formula")
    write_html(matches, out / "leads.html", stats)
    print(stats)
    print(f"wrote {out/'leads.csv'}, {out/'leads.html'}, {out/'all_scored.csv'}")


if __name__ == "__main__":
    main()
