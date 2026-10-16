"""Extract listing details from saved Depop product-page fetches (html format)."""

import glob
import html
import json
import re
import sys


def clean(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).strip()


def details(r):
    t = r.get("text") or ""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    prices = re.findall(r"\$([\d,]+\.\d\d)", t[:20000])
    cond = re.search(r"(Brand new|Like new|Excellent|Good|Fair)[^<]{0,12}condition", t)
    size = re.search(r">Size ([^<]{1,20})<", t)
    sold = bool(re.search(r">\s*Sold\s*<", t[:30000]))
    return {
        "url": r["url"], "title": r.get("title", "").replace(" | Depop", ""),
        "desc": (r.get("description") or "").split(" - Sold by @")[0],
        "h1": clean(h1.group(1)) if h1 else "", "price": prices[0] if prices else "",
        "was": prices[1] if len(prices) > 1 else "", "cond": cond.group(0) if cond else "",
        "size": size.group(1) if size else "", "sold": sold, "bag": "bag" in t and "person" in t,
    }


if __name__ == "__main__":
    out = {}
    try:
        out = json.load(open("data/depop/pages.json"))
    except FileNotFoundError:
        pass
    for f in sorted(glob.glob("data/depop/pages/*.json")):
        for r in json.load(open(f))["results"]:
            out[r["url"]] = details(r)
    json.dump(out, open("data/depop/pages.json", "w"), indent=1)
    for f in sys.argv[1:]:
        d = json.load(open(f))
        for r in d["results"]:
            x = out[r["url"]]
            print(x["price"], x["was"], x["size"], x["cond"], "SOLD" if x["sold"] else "", x["url"].split("/products/")[1][:45], "::", x["desc"][:260].replace("\n", " "), sep=" | ")
        print("failed:", len(d["errors"]))
