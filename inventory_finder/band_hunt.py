"""Collect older (80s/90s) grunge, alt, industrial and nu-metal band shirts in a price range
from saved eBay / Poshmark / Vinted / Mercari search pages.

  python3 -m inventory_finder.band_hunt            # print a summary
  python3 -m inventory_finder.band_hunt --report   # write output/bands90s/*.html and .csv
"""

import csv
import glob
import json
import re
import sys
from datetime import date
from pathlib import Path

from .brockum import ebay_cards, mercari_cards

LOW, HIGH = 80.0, 250.0
DATA = Path("data/bands90s")
OUT = Path("output/bands90s")

# Band name -> pattern matched against the title. Order matters: first match wins.
BANDS = {
    "Nirvana / Kurt Cobain": r"nirvana|kurt cobain|cobain",
    "Marilyn Manson": r"marilyn manson|\bmanson\b",
    "Soundgarden": r"soundgarden|chris cornell",
    "Foo Fighters": r"foo fighters",
    "Pearl Jam": r"pearl jam",
    "Alice in Chains": r"alice in chains",
    "Smashing Pumpkins": r"smashing pumpkins",
    "Stone Temple Pilots": r"stone temple pilots|\bstp\b",
    "Nine Inch Nails": r"nine inch nails|\bnin\b",
    "Babes in Toyland": r"babes in toyland",
    "Hole / Courtney Love": r"\bhole\b.*courtney|courtney love|\bhole (band|live|tour|celebrity|doll)",
    "Mudhoney": r"mudhoney",
    "Melvins": r"melvins",
    "Sonic Youth": r"sonic youth",
    "Tool": r"\btool\b.*(band|tour|aenima|undertow|opiate|lateralus)|(aenima|undertow)",
    "Rage Against the Machine": r"rage against the machine|\bratm\b",
    "Deftones": r"deftones",
    "Korn": r"\bkorn\b",
    "White Zombie / Rob Zombie": r"white zombie|rob zombie",
    "Type O Negative": r"type o negative",
    "Jane's Addiction": r"jane'?s addiction",
    "Bush": r"\bbush\b.*(band|tour|sixteen|razorblade|gavin)|gavin rossdale",
    "Silverchair": r"silverchair",
    "Screaming Trees": r"screaming trees",
    "L7": r"\bl7\b",
    "Babes in Toyland": r"babes in toyland",
    "Ministry": r"\bministry\b",
    "Butthole Surfers": r"butthole surfers",
    "Red Hot Chili Peppers": r"red hot chil+i peppers|\brhcp\b",
    "Weezer": r"weezer",
    "Green Day": r"green day",
    "Radiohead": r"radiohead",
    "Beck": r"\bbeck\b.*(odelay|loser|mellow gold|tour)",
    "Primus": r"\bprimus\b",
    "Helmet": r"\bhelmet\b.*(band|tour|meantime|betty)",
    "Faith No More": r"faith no more",
    "Danzig": r"\bdanzig\b",
    "Temple of the Dog": r"temple of the dog",
    "Mad Season": r"mad season",
    "Smashing / Pixies": r"\bpixies\b",
    "Tori / Bjork / PJ Harvey": r"pj harvey|bjork|björk",
    "Lollapalooza": r"lollapalooza",
    "The Cure": r"\bthe cure\b",
    "Morrissey / Smiths": r"morrissey|the smiths",
    "Sublime": r"\bsublime\b",
    "The Cranberries": r"cranberries",
    "Garbage": r"\bgarbage\b.*(band|tour|shirley)",
    "Filter / Static-X / Godsmack": r"static[- ]x|godsmack|\bfilter\b.*(band|tour)",
    "Slipknot": r"slipknot",
    "Pantera": r"pantera",
    "Metallica": r"metallica",
    "Megadeth": r"megadeth",
    "Slayer": r"(?<!vampire )\bslayer\b",
    "Sepultura": r"sepultura",
    "Misfits": r"\bmisfits\b",
}
NOT_SHIRT = (r"\b(hat|cap|snapback|beanie|jacket|poster|pins?|patch|sticker|button|program|tour book|ticket|"
             r"vhs|dvd|cd|vinyl|lp|cassette|bandana|bag|backpack|mug|keychain|cards?|flag|tapestry|figure|"
             r"book|magazine|photo|lithograph|guitar pick|kids?|toddler|baby|youth|onesie|cardigan|sweater|knit|"
             r"jersey|shorts|pants|socks|dress|skirt)\b")
MODERN = (r"\bmodern\b|reprint|re-print|reproduction|\brepro\b|vintage[- ]style|vintage inspired|retro style|"
          r"\bnwt\b|new with tags|brand new|\by2k\b|2000s|2010s|\b20[0-2]\d\b|recreation|remake|"
          r"fan made|custom|handmade|homemade|bravado|hot topic|urban outfitters|gildan heavy|"
          r"[\u2018\u2019'](0\d|1\d|2\d)\b")  # '06, '12 …
AGE = [("single stitch", r"single[- ]?stitch|single stich"),
       ("80s/90s", r"\b19[89]\d\b|\b(80|90)'?s\b|early 90|late 80"),
       ("old tag", r"\bgiant\b|brockum|screen stars|oneita|tultex|winterland|tee jays|\bm&o\b|anvil|"
                   r"fruit of the loom|hanes beefy|signal|stanley desantis|murina|sportswear|jerzees"),
       ("made in USA", r"made in usa|usa made"),
       ("bootleg", r"bootleg|\bboot\b"),
       ("tour shirt", r"\btour\b|concert"),
       ("long sleeve", r"long ?sleeve|\bl/s\b"),
       ("double sided", r"double[- ]sided|2[- ]sided|front (and|&) back")]


def band_of(title):
    t = title.lower()
    return next((b for b, p in BANDS.items() if re.search(p, t)), None)


def load_all():
    items = {}
    for f in sorted(glob.glob(str(DATA / "ebay*.json"))):
        for r in json.load(open(f)).get("results", []):
            for it in ebay_cards(r.get("text") or ""):
                items.setdefault(("eBay", it["id"]), it)
    for f in sorted(glob.glob(str(DATA / "mercari*.json"))):
        for r in json.load(open(f)).get("results", []):
            for it in mercari_cards(r.get("text") or ""):
                items.setdefault(("Mercari", it["id"]), it)
    from .tinyfish_ingest import parse_poshmark, parse_vinted
    for site, pat, fn in (("Poshmark", "posh*.json", parse_poshmark), ("Vinted", "vinted*.json", parse_vinted)):
        for f in sorted(glob.glob(str(DATA / pat))):
            for r in json.load(open(f)).get("results", []):
                for l in fn(r):
                    items.setdefault((site, l.url), {
                        "site": site, "id": l.url, "url": l.url, "title": l.title, "price": l.price,
                        "was": l.original_price, "size": l.size, "cond": l.condition, "ship": "",
                        "offer": site == "Poshmark", "bids": "", "text": l.brand, "image": ""})
    return list(items.values())


def judge(it):
    """Return the row to keep, or None with nothing printed."""
    title = it["title"]
    t = f'{title} {it.get("text", "")}'.lower()
    if it["price"] is None or not (LOW <= it["price"] <= HIGH):
        return None
    band = band_of(title)
    if not band or re.search(NOT_SHIRT, title.lower()) or re.search(MODERN, t):
        return None
    if not re.search(r"vintage|\bvtg\b|single[- ]?stitch|\b19[6-9]\d\b|\b(80|90)'?s\b|original|og\b|bootleg", t):
        return None  # must at least claim to be old
    tags = [label for label, p in AGE if re.search(p, t)]
    year = re.search(r"\b(19[6-9]\d)\b", title)
    return {**it, "band": band, "tags": tags, "year": year.group(1) if year else "",
            "age_score": sum(2 if x in ("single stitch", "old tag", "80s/90s", "made in USA") else 1 for x in tags)}


def rows():
    return sorted(filter(None, map(judge, load_all())), key=lambda r: (-r["age_score"], r["price"]))


if __name__ == "__main__" and "--report" not in sys.argv:
    R = rows()
    from collections import Counter
    print(len(R), "kept;", dict(Counter(r["site"] for r in R)))
    print(Counter(r["band"] for r in R).most_common())


def report():
    R = rows()
    OUT.mkdir(parents=True, exist_ok=True)
    keys = ["band", "site", "price", "was", "size", "cond", "ship", "year", "tags", "age_score", "title", "url"]
    with open(OUT / "vintage_band_shirts_80_250.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in R:
            w.writerow({**r, "tags": ", ".join(r["tags"])})
    data = [{k: r.get(k) for k in keys} for r in R]
    bands = sorted({r["band"] for r in R}, key=lambda b: -sum(r["band"] == b for r in R))
    from collections import Counter
    sites = Counter(r["site"] for r in R)
    page = (Path(__file__).with_name("band_report.html").read_text()
            .replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
            .replace("__BANDS__", json.dumps(bands))
            .replace("__TOTAL__", str(len(R)))
            .replace("__NBANDS__", str(len(bands)))
            .replace("__SITES__", " · ".join(f"{k} {v}" for k, v in sites.most_common()))
            .replace("__DATE__", f"{date.today():%b %d, %Y}"))
    (OUT / "vintage_band_shirts_80_250.html").write_text(page)
    print(len(R), "listings ->", OUT)


if __name__ == "__main__" and "--report" in sys.argv:
    report()
