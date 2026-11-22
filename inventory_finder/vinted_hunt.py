"""Newest Vinted listings for vintage band and rap tees, split into Nirvana / Sade / Sub Pop / rap / other bands.

  python3 -m inventory_finder.vinted_hunt --report   # output/vinted_hunt/vinted_hunt.html + .csv
"""
import csv, glob, json, re, sys
from pathlib import Path

from .vinted_md import cards
from .weekly_hunt import AGE, NOT_SHIRT

DATA = Path("data/vinted_nov22")
OUT = Path("output/vinted_hunt")

GROUPS = {
    "nirvana": {"Nirvana / Kurt Cobain": r"nirvana|cobain"},
    "sade": {"Sade": r"\bsade\b"},
    "subpop": {"Sub Pop (label)": r"sub ?pop", "Mudhoney": r"mudhoney", "L7": r"\bl7\b", "Screaming Trees": r"screaming trees",
               "Tad": r"\btad\b", "Hazel": r"\bhazel\b", "Babes in Toyland": r"babes in toyland"},
    "rap": {"Tupac": r"tupac|2pac|\bpac\b|makaveli", "Biggie": r"biggie|notorious|\bbig\b.*smalls", "Dr. Dre": r"dr\.? ?dre",
            "Wu-Tang": r"wu ?tang|ol dirty|odb|method man|ghostface", "Snoop Dogg": r"snoop", "Eazy-E / NWA": r"eazy|\bnwa\b|n w a",
            "Rap tee (other)": r"\brap\b|hip ?hop|aaliyah|outkast|nas\b|jay ?z|bone thugs|cypress hill|ice cube|lauryn|missy"},
    "bands": {"Smashing Pumpkins": r"smashing pumpkins|corgan", "Soundgarden": r"soundgarden|cornell", "Oasis": r"\boasis\b",
              "Green Day": r"green ?day", "Radiohead": r"radiohead", "Dinosaur Jr": r"dinosaur jr", "Red Hot Chili Peppers": r"chili peppers|\brhcp\b",
              "Butthole Surfers": r"butthole surfers", "Stone Temple Pilots": r"stone temple|\bstp\b", "Nine Inch Nails": r"nine inch nails|\bnin\b",
              "The Cranberries": r"cranberries", "Siouxsie": r"siouxsie"},
}
QUERY_GROUP = [("nirvana", r"nirvana|cobain"), ("sade", r"sade"), ("subpop", r"sub%20pop|mudhoney|l7|screaming|tad|hazel|babes"),
               ("rap", r"tupac|dre|wu%20tang|rap|biggie"), ("bands", r".")]

OLD_TAGS = (r"giant|brockum|winterland|screen stars|oneita|tultex|anvil|fruit of the loom|hanes|signal|stanley desantis|murina|"
            r"tee jays|jerzees|delta|changes|sportswear|all sport|liquid blue|stedman|m&o|rap tees|blue hole|wild oats")
MODERN_BRAND = (r"^(gildan|cotton on|urban outfitters|american eagle|zara|h&m|free people|daydreamer|hot topic|rock off|bravado|"
                r"artist merch|amplified|primark|pull&bear|forever 21|shein|boxlunch|target|walmart|old navy|uniqlo|spencer)")
MODERN = (r"reprint|re print|not vintage|vintage style|vintage inspired|retro style|modern|repro|custom|bootleg style|"
          r"\b20(0[5-9]|1\d|2\d)\b|2010s|2020s|new with tags|s 5xl|unisex|gift|fan art|handmade")
ERA = r"vintage|\bvtg\b|\b19[89]\d\b|\b200[0-4]\b|\b(80|90)s\b|single stitch|original|\bog\b|deadstock|tour|concert|memorial"


def group_of(url):
    q = url.split("search_text=")[1].split("&")[0]
    return next(g for g, p in QUERY_GROUP if re.search(p, q))


def rows():
    out, seen = {g: [] for g in GROUPS}, set()
    for f in sorted(glob.glob(str(DATA / "v_*.json"))):
        for res in json.load(open(f))["results"]:
            g = group_of(res["url"])
            for c in cards(res):
                if c["id"] in seen:
                    continue
                t = c["title"].lower()
                brand = c["brand"].lower()
                full = f"{t} {brand}"
                band = next((b for b, p in GROUPS[g].items() if re.search(p, t) or re.search(p, brand)), None)
                if not band or re.search(NOT_SHIRT, t) or re.search(MODERN, f"{full} {c['cond'].lower()}") or re.search(MODERN_BRAND, brand):
                    continue
                if not (re.search(ERA, full) or re.search(OLD_TAGS, brand)):
                    continue
                if re.search(r"\d+ ?(m|t)\b|months|toddler|kids|youth|baby", c["size"].lower()):
                    continue
                tags = [label for label, p in AGE if re.search(p, full)]
                if re.search(OLD_TAGS, brand) and "old tag" not in tags:
                    tags.append("old tag")
                strong = {"single stitch", "old tag", "80s/90s", "made in USA"} & set(tags)
                if re.search(r"\bstyle\b|vintage wash|washed|classic fit|oversized|cropped|retro|aesthetic|inspired|palaye|practice", t) and not strong:
                    continue
                if c["price"] < 20 and not strong:
                    continue  # Vinted is full of $2-15 new prints; keep cheap ones only with a real sign of age
                if g == "nirvana" and re.search(r"\by2k\b|2000s|\b00s\b|\b200\d\b", t):
                    continue
                seen.add(c["id"])
                tags = [label for label, p in AGE if re.search(p, full)]
                if re.search(OLD_TAGS, brand) and "old tag" not in tags:
                    tags.append("old tag")
                year = re.search(r"\b(19[89]\d|200[0-4])\b", t)
                out[g].append({**c, "band": band, "tags": tags, "year": year.group(1) if year else "", "listed": "",
                               "where": c["cond"], "bids": "",
                               "score": sum(2 if x in ("single stitch", "old tag", "80s/90s", "made in USA") else 1 for x in tags)})
    for g in out:  # newest first: Vinted ids rise over time
        out[g].sort(key=lambda r: int(r["id"]), reverse=True)
    return out


if __name__ == "__main__":
    L = rows()
    from collections import Counter
    for g, v in L.items():
        print(g, len(v), Counter(r["band"] for r in v).most_common(8))
    if "--report" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        keys = ["list", "band", "site", "price", "size", "brand", "cond", "year", "tags", "score", "title", "url", "listed", "where", "bids"]
        with open(OUT / "vinted_hunt.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for g, v in L.items():
                for r in v:
                    w.writerow({**r, "list": g, "tags": ", ".join(r["tags"])})
        notes = {"nirvana": "Nirvana and Kurt Cobain tees on Vinted that claim to be old (vintage, a 1980–2004 date, single stitch, tour/memorial) or carry an old tag brand in Vinted's brand field (Giant, Brockum, Anvil, Tultex, Screen Stars…).",
                 "sade": "Every Sade tee on Vinted that claims to be old or has an old tag.",
                 "subpop": "Sub Pop label shirts plus Mudhoney, L7, Screaming Trees, Tad, Hazel and Babes in Toyland.",
                 "rap": "Rap tees: Tupac (incl. memorial tees), Biggie, Dr. Dre, Wu-Tang and other vintage rap tees.",
                 "bands": "Smashing Pumpkins, Soundgarden, Oasis, Green Day, Radiohead, Dinosaur Jr, RHCP, Butthole Surfers, STP, NIN, Cranberries, Siouxsie."}
        labels = {"nirvana": "Nirvana", "sade": "Sade", "subpop": "Sub Pop", "rap": "Rap tees", "bands": "Other bands"}
        page = (Path(__file__).with_name("weekly_hunt.html").read_text()
                .replace("<title>Weekly Vintage Hunt</title>", "<title>Vinted Vintage Pulls</title>")
                .replace("This week's vintage pulls", "Vinted · newest pulls")
                .replace("__DATA__", json.dumps({g: [{k: r.get(k) for k in keys} for r in v] for g, v in L.items()}).replace("</", "<\\/"))
                .replace("const NOTES={", "const NOTES=" + json.dumps(notes)[:-1] + ",")
                .replace("const LABEL={", "const LABEL=" + json.dumps(labels)[:-1] + ",")
                .replace('<p class="sub">Listings on eBay, Poshmark and Mercari that claim', '<p class="sub">Vinted listings, newest first (Vinted shows no listing date, so order comes from its item numbers), that claim')
                .replace("The band tab only shows listings put up between __SINCE__ and __TODAY__. ", "Pulled Nov 22, 2026. ")
                .replace("Listing dates come from eBay's start time and from the creation time encoded in Poshmark's listing id. Mercari doesn't show dates, so Mercari rows are its newest results.", "Vinted's \"brand\" column is what the seller picked, which is often the tag (Giant, Brockum, Anvil, Tultex). Condition is Vinted's own rating.")
                .replace(" eBay prices are before shipping.", " Vinted prices are before buyer protection and shipping; make offers."))
        (OUT / "vinted_hunt.html").write_text(page)
        print("->", OUT)
