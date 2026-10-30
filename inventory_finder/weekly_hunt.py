"""Past-week vintage shirt hunt across eBay / Poshmark / Mercari, in three lists:
  bands  – 80s/90s/early-00s shirts for Nirvana, Pumpkins, Green Day, Soundgarden, Radiohead, Pixies, Manson, Dino Jr and peers
  sade   – any vintage Sade shirt
  subpop – Sub Pop label bands (matched by band name) and Sub Pop's own shirts

  python3 -m inventory_finder.weekly_hunt            # summary
  python3 -m inventory_finder.weekly_hunt --report   # output/weekly_hunt/*.html + .csv
"""
import csv, glob, json, re, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .brockum import mercari_cards
from .ebay_md import cards as ebay_cards
from .tinyfish_ingest import parse_poshmark

DATA = Path("data/hunt_oct30")
OUT = Path("output/weekly_hunt")
TODAY = date(2026, 10, 30)
SINCE = TODAY - timedelta(days=7)

CORE = {
    "Nirvana": r"nirvana|kurt cobain|cobain", "Smashing Pumpkins": r"smashing pumpkins|billy corgan",
    "Green Day": r"green ?day", "Soundgarden": r"soundgarden|chris cornell", "Radiohead": r"radiohead",
    "Pixies": r"\bpixies\b|frank black", "Marilyn Manson": r"marilyn manson|\bmanson\b",
    "Dinosaur Jr": r"dinosaur jr", "Sonic Youth": r"sonic youth", "Pavement": r"\bpavement\b",
    "Hole": r"courtney love|\bhole\b.*(band|tour|doll|celebrity skin|live through)", "Weezer": r"weezer",
    "Alice in Chains": r"alice in chains", "Pearl Jam": r"pearl jam", "Nine Inch Nails": r"nine inch nails|\bnin\b",
    "The Breeders": r"breeders", "Beck": r"\bbeck\b.*(odelay|loser|mellow gold|tour|mutations|midnite)",
    "Melvins": r"melvins", "Stone Temple Pilots": r"stone temple pilots|\bstp\b", "Foo Fighters": r"foo fighters",
    "Jane's Addiction": r"jane'?s addiction", "Mudhoney": r"mudhoney",
}
SUBPOP = {
    "Sub Pop (label)": r"sub ?pop", "Mudhoney": r"mudhoney", "Tad": r"\btad\b", "Dickless": r"dickless",
    "Green River": r"green river", "Screaming Trees": r"screaming trees", "L7": r"\bl7\b",
    "Babes in Toyland": r"babes in toyland", "Afghan Whigs": r"afghan whigs", "Beat Happening": r"beat happening",
    "Fluid": r"\bthe fluid\b|\bfluid\b.*(band|sub ?pop|denver)", "Sebadoh": r"sebadoh", "Codeine": r"\bcodeine\b.*(band|tour|frigid|sub ?pop)",
    "Love Battery": r"love battery", "Seaweed": r"\bseaweed\b.*(band|tour|sub ?pop|spanaway)",
    "Sunny Day Real Estate": r"sunny day real estate|\bsdre\b", "Supersuckers": r"supersuckers",
    "Combustible Edison": r"combustible edison", "Six Finger Satellite": r"six finger satellite",
    "Red Red Meat": r"red red meat", "Earth": r"\bearth\b.*(drone|dylan carlson|sub ?pop)", "Dwarves": r"dwarves",
    "Hazel": r"\bhazel\b.*(band|portland|sub ?pop)", "Velocity Girl": r"velocity girl", "Spinanes": r"spinanes",
    "Eric's Trip": r"eric'?s trip", "The Vaselines": r"vaselines", "Fastbacks": r"fastbacks", "Walkabouts": r"walkabouts",
    "Murder City Devils": r"murder city devils", "The Shins": r"\bthe shins\b", "Postal Service": r"postal service",
    "Blood Circus": r"blood circus", "Thrown Ups": r"thrown ups", "Pigeonhed": r"pigeonhed",
    "Big Chief": r"big chief", "Rein Sanction": r"rein sanction", "Jale": r"\bjale\b", "Pond": r"\bpond\b.*(band|sub ?pop|portland)",
    "Mark Lanegan": r"lanegan", "The Gits": r"\bthe gits\b|mia zapata",
    "Nirvana (Sub Pop era)": r"nirvana.*(sub ?pop|bleach|blew|love buzz|sliver)|(sub ?pop|bleach).*nirvana",
    "Soundgarden (Sub Pop era)": r"soundgarden.*(sub ?pop|screaming life|fopp)",
}
SADE = {"Sade": r"\bsade\b"}

NOT_SHIRT = (r"\b(hat|cap|snapback|beanie|jacket|poster|pins?|patch|sticker|button|program|tour ?book|ticket|vhs|dvd|"
             r"\bcd\b|vinyl|\blp\b|cassette|bandana|bag|backpack|mug|keychain|cards?|flag|tapestry|figure|book|magazine|"
             r"photo|lithograph|pick|toddler|baby|onesie|cardigan|sweater|knit|shorts|pants|socks|dress|skirt|tin set|postcards?|"
             r"boxers?|pajama|canvas print|hoodie|pullover|zip)\b")
MODERN = (r"reprint|re-print|reproduction|\brepro\b|vintage[- ]style|vintage inspired|retro style|\bnwt\b|new with tags|"
          r"brand new|recreation|remake|fan made|custom|handmade|homemade|bravado|hot topic|urban outfitters|"
          r"s-5xl|s ?- ?\dxl|all size|unisex short sleeve|gift for|\b20(0[5-9]|1\d|2\d)\b|"
          r"[‘’'](0[5-9]|1\d|2\d)\b|\b(2010s|2020s)\b|\bmodern\b|cotton tee shirt men women|eleven paris|parody|\byouth\b|\bkids\b|\bcute\b|cotton on|anniversary|preowned (small|medium|large|xl)")
ERA = (r"\b19[89]\d\b|\b200[0-4]\b|\b(80|90)'?s\b|\b(00s|y2k)\b|single[- ]?stitch|single stich|\bvtg\b|vintage|"
       r"\boriginal\b|\bog\b|bootleg|tour|concert|giant|brockum|winterland|screen stars|oneita|tultex|signal|tee jays")
AGE = [("single stitch", r"single[- ]?stitch|single stich"), ("80s/90s", r"\b19[89]\d\b|\b(80|90)'?s\b"),
       ("early 00s", r"\b200[0-4]\b|\by2k\b|\b00s\b"),
       ("old tag", r"\bgiant\b|brockum|screen stars|oneita|tultex|winterland|tee jays|\bm&o\b|anvil|fruit of the loom|"
                   r"hanes beefy|signal|stanley desantis|murina|jerzees|delta|stedman|hanes"),
       ("made in USA", r"made in usa|usa made"), ("bootleg", r"bootleg"),
       ("tour / concert", r"\btour\b|concert|\blive\b"), ("long sleeve", r"long ?sleeve|\bl/s\b"),
       ("double sided", r"double[- ]sided|2[- ]sided|front (and|&) back|back print")]


# Band names that are also ordinary words: the title must also read like a band shirt.
AMBIGUOUS = {"Green River", "Postal Service", "Dwarves", "Babes in Toyland", "L7", "Pond", "Tad", "Hazel", "Earth",
             "Big Chief", "Jale", "Codeine", "Seaweed", "Fluid", "Fastbacks", "Walkabouts", "Thrown Ups"}
BANDISH = r"\bband\b|tour|concert|sub ?pop|grunge|punk|seattle|\brock\b|album|records?\b|indie|emo|alternative|90s band|\bep\b|single stitch|giant|brockum"
SADE_JUNK = r"washed|vale (dreams|forever)|valley dream|andre 3000|andré 3000|janelle|whitney|cpfm|aaliyah|png|svg|sublimation"


def key_min(bands):
    return 25 if bands is CORE else 0


def posh_date(url):
    """Poshmark listing ids are Mongo ObjectIds: the first 8 hex digits are the creation time."""
    m = re.search(r"-([0-9a-f]{24})$", url)
    return datetime.fromtimestamp(int(m.group(1)[:8], 16), timezone.utc).date() if m else None


def mercari_md(result):
    """Mercari search pages fetched as markdown: after the filter list, each card is a title line optionally
    followed by a price line ("$60.00$75.00" = sale and original). Item links come in the same order."""
    text, links = result.get("text") or "", result.get("links") or []
    urls = []
    for u in links:
        m = re.search(r"/us/item/(m\d+)/", u)
        if m and m.group(1) not in [x[0] for x in urls]:
            urls.append((m.group(1), f"https://www.mercari.com/us/item/{m.group(1)}/"))
    body = text.split("\nStatus\n", 1)[-1].split("Sell or buy. Almost anything.")[0]
    lines = [x.strip() for x in body.split("\n") if x.strip() and not re.fullmatch(r"\d+%", x.strip())]
    cards = []
    for x in lines:
        if x.startswith("$"):
            price = float(re.match(r"\$([\d,]+\.\d\d)", x).group(1).replace(",", ""))
            if cards and cards[-1][1] is None:
                cards[-1][1] = price
            else:  # a price with no title above it: a card whose title didn't render
                cards.append([None, price])
        else:
            cards.append([x, None])
    if len(cards) != len(urls):
        return []
    return [{"site": "Mercari", "id": i, "url": u, "title": t, "price": p, "size": "", "cond": "", "bids": ""}
            for (i, u), (t, p) in zip(urls, cards) if t]


def load():
    items = {}
    for f in sorted(DATA.glob("ebay_*.json")):
        for r in json.load(open(f))["results"]:
            for c in ebay_cards(r, TODAY):
                items.setdefault(c["url"], {**c, "query": re.search(r"nkw=([^&]+)", r["url"]).group(1).replace("+", " ")})
    for f in sorted(p for p in DATA.glob("posh_*.json") if "manual" not in p.name):
        for r in json.load(open(f))["results"]:
            for l in parse_poshmark(r):
                items.setdefault(l.url, {"site": "Poshmark", "id": l.url, "url": l.url, "title": l.title, "price": l.price,
                                         "size": l.size, "brand": l.brand, "cond": "", "bids": "", "where": "",
                                         "listed": posh_date(l.url), "query": l.query})
    for f in sorted(DATA.glob("posh_*_manual.json")):  # small Poshmark result sets copied by hand
        for l in json.load(open(f)):
            items.setdefault(l["url"], {"site": "Poshmark", "id": l["url"], "url": l["url"], "title": l["title"],
                                        "price": float(l["price"]), "size": l["size"], "brand": "", "cond": "", "bids": "",
                                        "where": "", "listed": posh_date(l["url"]), "query": "sade"})
    for f in sorted(DATA.glob("mercmd_*.json")):
        for r in json.load(open(f))["results"]:
            for c in mercari_md(r):
                items.setdefault(c["url"], {**c, "brand": "", "where": "", "listed": None,
                                            "query": re.search(r"keyword=([^&]+)", r["url"]).group(1).replace("%20", " ").replace("%27", "'")})
    for f in sorted(DATA.glob("merc_*.json")):
        for r in json.load(open(f))["results"]:
            for c in mercari_cards(r.get("text") or ""):
                items.setdefault(c["url"], {**c, "brand": "", "where": "", "listed": None,
                                            "query": re.search(r"keyword=([^&]+)", r["url"]).group(1).replace("%20", " ")})
    return list(items.values())


def judge(it, bands, need_era=True, any_date=False):
    t = it["title"].lower()
    full = f'{t} {it.get("brand", "")}'.lower()
    band = next((b for b, p in bands.items() if re.search(p, t)), None)
    if not band or it["price"] is None or re.search(NOT_SHIRT, t) or re.search(MODERN, full):
        return None
    if it.get("cond") == "New (Other)" and not re.search(r"deadstock|\bnos\b|19[89]\d", t):
        return None  # mostly new reprints shipped from overseas
    if band in AMBIGUOUS and (not re.search(BANDISH, t) or re.search(r"bardo pond|disney|seven dwarves|festival|usps|day ?care|little charmers|ll ?bean", t)):
        return None
    if key_min(bands) and it["price"] < key_min(bands):
        return None
    if band == "Sade" and (re.search(SADE_JUNK, t) or it["price"] < 40):
        return None
    if need_era and not re.search(ERA, full):
        return None
    if not any_date and it["listed"] and it["listed"] < SINCE:
        return None
    tags = [label for label, p in AGE if re.search(p, full)]
    year = re.search(r"\b(19[89]\d|200[0-4])\b", t)
    return {**it, "band": band, "tags": tags, "year": year.group(1) if year else "",
            "score": sum(2 if x in ("single stitch", "old tag", "80s/90s", "made in USA") else 1 for x in tags),
            "listed": it["listed"].isoformat() if it["listed"] else ""}


def lists():
    items = load()
    out = {}
    for key, bands, need in (("bands", CORE, True), ("sade", SADE, True), ("subpop", SUBPOP, False)):
        q = {"bands": None, "sade": "sade", "subpop": None}[key]
        rows = []
        for it in items:
            if key == "sade" and "sade" not in it["query"]:
                continue
            if key == "subpop" and it["query"].replace("vintage ", "").replace(" shirt", "") not in SUBPOP_QUERIES:
                continue
            r = judge(it, bands, need, any_date=(key in ("sade", "subpop")))
            if r and (key != "subpop" or re.search(ERA, r["title"].lower()) or "sub" in r["title"].lower()):
                rows.append(r)
        out[key] = sorted(rows, key=lambda r: (r["listed"] or "0"), reverse=True)
    return out


SUBPOP_QUERIES = set(json.load(open(DATA / "subpop_queries.json"))) if (DATA / "subpop_queries.json").exists() else set()

if __name__ == "__main__":
    L = lists()
    from collections import Counter
    for k, v in L.items():
        print(k, len(v), Counter(r["site"] for r in v), Counter(r["band"] for r in v).most_common(8))
    if "--report" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        keys = ["list", "listed", "band", "site", "price", "size", "brand", "cond", "bids", "where", "year", "tags", "score", "title", "url"]
        with open(OUT / "weekly_hunt.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for k, v in L.items():
                for r in v:
                    w.writerow({**r, "list": k, "tags": ", ".join(r["tags"])})
        page = (Path(__file__).with_name("weekly_hunt.html").read_text()
                .replace("__DATA__", json.dumps({k: [{x: r.get(x) for x in keys} for r in v] for k, v in L.items()}).replace("</", "<\\/"))
                .replace("__SINCE__", f"{SINCE:%b %-d}").replace("__TODAY__", f"{TODAY:%b %-d, %Y}"))
        (OUT / "weekly_hunt.html").write_text(page)
        print("->", OUT)
