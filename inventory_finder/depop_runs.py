"""Merge TinyFish browser-run results (saved JSON) into data/depop/pages.json."""

import glob
import json

PAGES = "data/depop/pages.json"


def main():
    pages = json.load(open(PAGES))
    for f in sorted(glob.glob("data/depop/runs/*.json")):
        for it in json.load(open(f))["result"]["items"]:
            if it.get("failed"):
                continue
            pages[it["url"]] = {
                "url": it["url"], "title": "", "desc": it.get("description", ""), "h1": "",
                "price": (it.get("price") or "").lstrip("$"), "was": (it.get("original_price") or "").lstrip("$"),
                "cond": it.get("condition", ""), "size": it.get("size", ""), "brand": it.get("brand", ""),
                "sold": bool(it.get("sold")), "bag": False, "via": "browser",
            }
    json.dump(pages, open(PAGES, "w"), indent=1)
    print(len(pages), "pages")


if __name__ == "__main__":
    main()
