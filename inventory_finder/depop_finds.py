"""Sort saved Depop search cards into 90s Nirvana / RHCP shirts and flag underpriced ones.

  python -m inventory_finder.depop_finds data/depop/d*.json
"""

import json
import re
import sys
from pathlib import Path

from .depop_parse import load

BANDS = {
    "Nirvana": r"nirvan+a|nervana|kurt|cobain|kobain|nevermind|in-utero|incesticide|insecticide|sliver|bleach",
    "Red Hot Chili Peppers": r"chil+i|rhcp|peppers|red-hot|lollapalooza|blood-sugar|magik|one-hot-minute|mothers-milk",
}
NOT_THE_BAND = r"manic-nirvana|robert-plant|philly-peppers|kurt-adler|kurt-s-adler|radiohead|dinosaur|metallica|" \
               r"def-leppard|deftones|morrissey|mccartney|liquid-blue|weird-al|guitar-player|playboy"
NOT_A_SHIRT = r"\bcd\b|-cd-|vinyl|cassette|poster|keychain|patch|magazine|\blp\b|-lp-|signed|cardigan|sweater|" \
              r"knit|corset|flannel|framed|hoodie|zip-up|skirt|military|ornament|-pin-"
MODERN = (r"reprint|modern|-style|inspired|y2k|2000s|00s|2010s|20[0-2]\d|bravado|hot-topic|divided|"
          r"\bhm\b|-hm-|h-m|urban-outfitters|pacsun|forever-21|american-eagle|abercrombie|spencer|cotton-on|"
          r"supreme|cropped|baby-tee|open-back|upcycled|reworked|kids|size-8|grunge-not-dead")
MODERN_BRANDS = {"H&M", "Divided by H&M", "Hot Topic", "Gildan", "Bravado", "Urban Outfitters", "PacSun",
                 "Forever 21", "American Eagle", "Abercrombie & Fitch", "Spencer's", "Cotton On", "Supreme",
                 "NBA", "!M?ERFECT"}
TELLS = [
    (r"single-?stitch|single-stich|-single-", 3, "single stitch"),
    (r"19[89]\d|-9[0-9]-|-8[0-9]s|90s|80s|1990s|-92-|-93-", 3, "dated 80s/90s"),
    (r"bootleg|-boot-|parking-lot|no-tag", 1, "bootleg"),
    (r"true-?vintage|real-vintage|authentic|original|grail|rare|deadstock", 1, "claims original"),
    (r"vintage|vtg|vitnage", 1, "says vintage"),
]
OLD_BRANDS = {"Giant": 3, "Brockum": 3, "Screen Stars": 3, "Oneita": 3, "Anvil": 1, "Tultex": 1,
              "Fruit of the Loom": 1, "Hanes": 1, "Delta Pro Weight": 0, "Woodstock": 1}


def band_of(slug, query=""):
    for text in (slug, query):
        for b, p in BANDS.items():
            if re.search(p, text.replace("+", "-").replace("%20", "-")):
                return b
    return None


def score(c):
    slug, brand = c["slug"], (c["text"][0] if c["text"] else "")
    pts, why = 0, []
    for p, n, label in TELLS:
        if re.search(p, slug):
            pts += n
            why.append(label)
    if OLD_BRANDS.get(brand):
        pts += OLD_BRANDS[brand]
        why.append(f"{brand} tag")
    return pts, why, brand


def classify(cards):
    rows = []
    for c in cards.values():
        slug = c["slug"]
        band = band_of(slug, c.get("query", ""))
        if not band or re.search(NOT_THE_BAND, slug) or re.search(NOT_A_SHIRT, slug):
            continue
        pts, why, brand = score(c)
        modern = bool(re.search(MODERN, slug)) or brand in MODERN_BRANDS
        rows.append({**c, "band": band, "brand": brand, "size": c["text"][1] if len(c["text"]) > 1 else "",
                     "score": pts, "why": why, "modern": modern})
    return rows


def main(paths):
    rows = classify(load(paths))
    keep = sorted((r for r in rows if not r["modern"] and r["score"] >= 3), key=lambda r: (-r["score"], r["price"] or 0))
    Path("output/depop").mkdir(parents=True, exist_ok=True)
    Path("output/depop/candidates.json").write_text(json.dumps(keep, indent=1))
    for r in keep:
        print(r["score"], r["price"], r["band"][:7], r["brand"], r["size"], r["slug"], ",".join(r["why"]), sep="\t")
    print(len(rows), "band shirts,", len(keep), "with 90s tells", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
