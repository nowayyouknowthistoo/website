"""Merge every source gathered for the photo hunt into one candidate list."""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from .photo_match import classify
from .tinyfish_ingest import load as load_market

RAW = Path("data/raw_photos")

# Pages that are searches, categories or articles rather than one listing.
NOT_A_LISTING = re.compile(
    r"/sch/|/b/|/shop/|/market/|/search|/browse/|/catalog|/collections/|/str/|"
    r"pinterest|youtube|spotify|discogs|genius|albumism|highsnobiety|livenirvana|"
    r"wikipedia|amazon\.|walmart|tiktok|rakuten|kakaku|wwdjapan|vice\.com|lifeonline|"
    r"etsy\.com/[a-z-]+/?$|ebay\.com/?$")
REFERENCE = re.compile(r"instagram|facebook\.com/(?!marketplace)|reddit|defunkd|valueyourmusic|tshirtslayer|worthpoint")
# Junk that slipped through keyword searches: official store pages, kids sizes,
# hoodies/sweatshirts, current mall merch, guides, designer collabs.
JUNK = re.compile(r"shop\.nirvana\.com|nirvanaclothing\.shop|buynirvana\.shop|vintageconcerttshirts\.com|ragstock|"
                  r"toddler|12 months|hoodie|sweatshirt|crewneck|thermal sz xs|vintage look|vintage like|"
                  r"number\(n\)ine|daydreamer|grateful dead|robert plant|poshmark\.com/brand|grailed\.com/(designers|browse)|"
                  r"red long sleeve tee with blue logo|in utero red distressed|smiley.*(burnout|tie dye long sleeve shirt kurt)|"
                  r"modern nevermind|archive\.org", re.I)
ETSY_KEEP = {  # vintage Nirvana long sleeves among the Etsy market results
    "4392468052", "4543106210", "4566858557", "4569343641", "4572289436",
    "4567836993", "4510709789", "4544426996", "1799159435", "1822129127",
}


def site_of(url):
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for name in ("ebay", "grailed", "depop", "etsy", "poshmark", "mercari", "vinted", "gem.app",
                 "instagram", "facebook", "reddit", "defunkd", "yahoo"):
        if name in host:
            return name.replace(".app", "")
    return host


def norm(url):
    u = url.split("?")[0].rstrip("/")
    m = re.search(r"ebay\.[a-z.]+/itm/(\d+)", u)
    return f"ebay:{m.group(1)}" if m else u.lower()


def collect():
    rows = []
    # 1. hand-recorded search results
    for line in (RAW / "search_items.tsv").read_text().splitlines():
        url, title, note = (line.split("\t") + ["", ""])[:3]
        rows.append({"url": url, "title": title, "note": note, "source": "web search"})
    # 2. DuckDuckGo results
    for x in json.loads((RAW / "ddg_parsed.json").read_text()):
        rows.append({"url": x["url"], "title": x["title"], "note": x["snippet"], "source": "duckduckgo"})
    # 3. Etsy market pages (title from the URL slug)
    for r in json.loads((RAW / "etsy-1.json").read_text())["results"]:
        for l in r["links"]:
            m = re.search(r"/listing/(\d+)/([^?]+)", l)
            if m and m.group(1) in ETSY_KEEP:
                rows.append({"url": l.split("?")[0], "title": m.group(2).replace("-", " "),
                             "note": "Etsy (title from URL, may be cut short)", "source": "etsy"})
    # 4. Poshmark / Vinted searches: long sleeves that look older than current merch
    for l in load_market(sorted(RAW.glob("tf-*.json"))):
        t = l.title.lower()
        if "nirvana" in t and re.search(r"long ?sleeve|longsleeve", t) and re.search(
                r"vintage|90s|199\d|boot|euro|single stitch|giant|brockum|hot-ice", t):
            rows.append({"url": l.url, "title": l.title, "price": l.price, "size": l.size,
                         "note": f"{l.site} search", "source": l.site})

    out, seen = [], set()
    for r in rows:
        if NOT_A_LISTING.search(r["url"]) and not ETSY_KEEP & set(re.findall(r"\d+", r["url"])):
            continue
        k = norm(r["url"])
        if k in seen:
            continue
        seen.add(k)
        text = f"{r['title']} {r.get('note', '')}"
        if "nirvana" not in text.lower() and "cobain" not in text.lower() and "ニルヴァーナ" not in text:
            continue
        c = classify(r["title"], r.get("note", ""))
        if JUNK.search(r["url"]) or JUNK.search(r["title"]):
            continue
        r.update(c)
        r["site"] = site_of(r["url"])
        r["kind"] = "reference" if REFERENCE.search(r["url"]) else "listing"
        if not r.get("price"):
            m = re.search(r"(?:US )?\$\s?([\d,]+(?:\.\d\d)?)", text)
            r["price"] = float(m.group(1).replace(",", "")) if m else None
        out.append(r)
    return out


# ---- manual review (Oct 16 2026) -------------------------------------------
# url fragment -> fields to override after reading titles/snippets by hand.
MODERN = ["336706506867", "336817293932", "4574519173", "4574519073", "gol9en_vintagera",
          "336035924032", "397828404496", "tiejneystumpf", "407167872221", "188386142753",
          "188725677432", "vintagenclassic", "Smiley-Face-Long-Sleeve-Tee-Blue", "Acid-Wash-TieDye",
          "4574404553", "9158358910", "Smiley-Long-Sleeve-Shirt", "Nirvana-In-Utero-Long-Sleeve-Te"]
NOT_DESIGN = ["EURO-LOT-BOOTLEG", "85961680", "104006430", "20076661", "157211324241", "204521505410",
              "407204358295", "nirvana-90s-nevermind-bootleg-shirt", "vintage-nirvana-nevermind-european-tour",
              "24429136434", "307187518077"]
DROP = ["gem.app/product/90s-nirvana-kurt-cobain-memorial", "gem.app/product/vtg-1991", "Memorial-1994-Single-Stitch-6acb12d9",
        "Kurt-Cobain-Memorial-Nirvana-19", "Rare-Vintage-Nirvana-Kurt-Cobai-6a6", "shop.app/", "1992-nirvana-vestibule-shirt-10162663",
        "Vintage-HotIce", "Nirvana-Kurt-Kobain-Band-Concer", "oldvintagedepop", "4459183443", "236475939665",
        "178226520833", "1990s-nirvana-smiley-shirt-03012417", "1990s-nirvana-smiley-sh"]


def review(rows):
    out = []
    for r in rows:
        u = r["url"]
        if any(d.lower() in u.lower() for d in DROP):
            continue
        if any(m.lower() in u.lower() for m in MODERN):
            r["reprint"] = True
        if any(n.lower() in u.lower() for n in NOT_DESIGN):
            r["design"], r["design_name"] = None, ""
        if r["kind"] == "reference" or r["sold"]:
            group = "Sold / reference (price comps)"
        elif r["reprint"] or r["modern_brand"]:
            group = "Reprint or modern: avoid"
        elif r["design"]:
            group = "Your designs: possible originals"
        else:
            group = "Same family: 90s bootleg / Euro long sleeves"
        r["group"] = group
        out.append(r)
    return out


if __name__ == "__main__":
    rows = review(collect())
    Path("output/photo_hunt").mkdir(parents=True, exist_ok=True)
    Path("output/photo_hunt/candidates.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    from collections import Counter
    print(len(rows), Counter(r["group"] for r in rows), Counter(r["design"] for r in rows))
    print(Counter(r["site"] for r in rows))


