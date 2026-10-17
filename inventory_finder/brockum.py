"""Collect Brockum / Winterland shirts under a price cap from saved search pages (eBay, Poshmark,
Vinted, Mercari, Depop) and write a list for the user to check by eye.

  python3 -I -m inventory_finder.brockum
"""

import glob
import html
import json
import re
import sys
from pathlib import Path

MAX_PRICE = 35.0
LABEL = r"brock?um|brockam|winter ?land"
# Only drop listings that say they're modern / reproductions. Era (Y2K, 2004…) is shown, not filtered:
# Winterland printed band merch into the 2000s and you'll judge those yourself.
MODERN = (r"\bmodern\b|reprint|re-print|reproduction|\brepro\b|vintage[- ]style|vintage inspired|retro style|"
          r"\bnwt\b|new with tags|brand new")
NOT_SHIRT = (r"\b(hat|cap|snapback|beanie|jacket|poster|pin|pins|patch|sticker|button|program|tour book|ticket|"
             r"vhs|dvd|cd|vinyl|lp|cassette|bandana|scarf|bag|backpack|mug|keychain|cards?|rockcards?|"
             r"trading|stamp|ornament|pajama|pants|shorts|socks|blanket|tapestry|flag|figure|figurine|book|plate|"
             r"votives?|boots?|sweater|sleeper|nightgown|sweats|jogger|dress|skirt|kids?|toddler|baby|youth|"
             r"juniors|girls?|boys?|wonderful winterland|nordic winterland|transfer|iron[- ]on)\b")
CLOTHING = r"\b(tee|t[- ]?shirt|tshirt|shirt|tank|top|sweatshirt|crewneck|crew neck|long ?sleeve|l/s|hoodie)\b"
KID_SIZE = r"\((girl|boy|juniors)\)|\b\d+t\b|\d+-\d+m\b|months?|\bnb\b"
# Sizes that mean "not clothing" on Poshmark/Vinted.
NOT_CLOTHING_SIZE = {"OS", "Standard", "OS (Boy)", "Various sizes", "Lot", ""}


def text_of(block):
    return [t for t in (html.unescape(x).strip() for x in re.findall(r">([^<>]+)<", block)) if t]


def ebay_cards(page):
    out, seen = [], set()
    for b in re.split(r'<li[^>]+class="[^"]*\bs-(?:card|item)\b', page)[1:]:
        m = re.search(r'href="(https://www\.ebay\.com/itm/(\d+))', b)
        if not m or m.group(2) in seen:
            continue
        seen.add(m.group(2))
        t = [x for x in text_of(b) if x.upper() not in ("NEW LOW PRICE", "NEW LISTING", "SPONSORED", "BRAND NEW")
             and not x.startswith("Opens in a new")]
        if not t or t[0].startswith("Shop on eBay"):
            continue
        prices = [float(p.replace(",", "")) for p in re.findall(r"^\$([\d,]+\.\d\d)$", "\n".join(t), re.M)]
        ship = next((x for x in t if "delivery" in x or "shipping" in x.lower()), "")
        cond = next((x for x in t if x in ("Pre-Owned", "New (Other)", "Brand New", "New with tags",
                                           "New without tags", "Parts Only")), "")
        size = next((x.replace("Size ", "").strip(" ·") for x in t if x.startswith("Size ")), "")
        img = re.search(r'<img[^>]+(?:src|data-src)="(https://i\.ebayimg\.com/[^"]+)"', b)
        out.append({
            "site": "eBay", "id": m.group(2), "url": m.group(1), "title": t[0],
            "price": prices[0] if prices else None, "was": prices[1] if len(prices) > 1 else None,
            "size": size, "cond": cond, "ship": ship,
            "offer": "or Best Offer" in t, "bids": next((x for x in t if re.search(r"\d+ bids?$", x)), ""),
            "text": " | ".join(t[1:8]), "image": img.group(1) if img else "",
        })
    return out


def mercari_cards(page):
    out = []
    for href, iid, inner in re.findall(r'<a[^>]+href="(/us/item/(m\d+)/)[^"]*"[^>]*>(.*?)</a>', page, re.S):
        t = text_of(">" + inner + "<")
        t = [x for x in t if not re.fullmatch(r"\d+%", x)]
        prices = [float(x[1:].replace(",", "")) for x in t if re.fullmatch(r"\$[\d,]+\.\d\d", x)]
        if not t or not prices:
            continue
        img = re.search(r'<img[^>]+src="([^"]+)"', inner)
        out.append({"site": "Mercari", "id": iid, "url": "https://www.mercari.com" + href, "title": t[0],
                    "price": prices[0], "was": prices[1] if len(prices) > 1 else None, "size": "", "cond": "",
                    "ship": "", "offer": True, "bids": "", "text": "", "image": img.group(1) if img else ""})
    return out


def keep(it):
    text = f'{it["title"]} {it.get("text", "")}'.lower()
    if not re.search(LABEL, text) or it["price"] is None or it["price"] > MAX_PRICE:
        return False
    if re.search(MODERN, text) or re.search(NOT_SHIRT, it["title"].lower()):
        return False
    if re.search(KID_SIZE, (it.get("size") or "").lower()):
        return False
    # The label has to be the shirt's brand or in the title, and the listing has to read like a shirt.
    if it["site"] != "eBay" and not re.search(CLOTHING, it["title"].lower()):
        return False
    return True


def collect():
    items = {}
    for f in sorted(glob.glob("data/brockum/*.json")):
        d = json.load(open(f))
        for r in d.get("results", []):
            page = r.get("text") or ""
            if "ebay.com" in r["url"]:
                for it in ebay_cards(page):
                    items.setdefault(("eBay", it["id"]), it)
    for f in sorted(glob.glob("data/brockum/mercari*.html.json")):
        for r in json.load(open(f)).get("results", []):
            for it in mercari_cards(r.get("text") or ""):
                items.setdefault(("Mercari", it["id"]), it)
    from .tinyfish_ingest import parse_poshmark, parse_vinted
    for site, pat, fn in (("Poshmark", "posh*.md.json", parse_poshmark), ("Vinted", "vinted*.md.json", parse_vinted)):
        for f in sorted(glob.glob(f"data/brockum/{pat}")):
            for r in json.load(open(f)).get("results", []):
                for l in fn(r):
                    if l.size.strip() in NOT_CLOTHING_SIZE:
                        continue
                    items.setdefault((site, l.url), {
                        "site": site, "id": l.url, "url": l.url, "title": l.title, "price": l.price,
                        "was": l.original_price, "size": l.size, "cond": l.condition, "ship": "",
                        "offer": site == "Poshmark", "bids": "", "text": l.brand, "image": "",
                    })
    return [it for it in items.values() if keep(it)]


if __name__ == "__main__":
    rows = collect()
    print(len(rows), "kept", file=sys.stderr)
    for r in sorted(rows, key=lambda r: r["price"]):
        print(r["site"], r["price"], r["size"], r["cond"], r["title"][:80], sep="\t")
