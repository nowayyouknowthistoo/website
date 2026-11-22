"""Parse Vinted catalog search pages fetched as markdown (with links) by TinyFish fetch_content.

Each card renders as three lines: brand (or the title when no brand is set), "size · condition", price.
The item links come in the same order and carry the full title in their slug; item ids rise over time.
"""
import re


def cards(result):
    text, links = result.get("text") or "", result.get("links") or []
    items = []
    for u in links:
        m = re.search(r"/items/(\d+)-([^?]+)", u)
        if m and m.group(1) not in [x[0] for x in items]:
            items.append((m.group(1), m.group(2)))
    body = text.split("results.", 1)[-1]
    lines = [x.strip() for x in body.split("\n") if x.strip()]
    blocks = []
    for i, x in enumerate(lines):
        if re.fullmatch(r"\$[\d,]+\.\d\d", x):
            price = float(x[1:].replace(",", ""))
            if " · " in lines[i - 1]:
                blocks.append((lines[i - 2], lines[i - 1], price))
            else:  # card without a size/condition line
                blocks.append((lines[i - 1], "", price))
    if len(blocks) != len(items):
        return []
    out = []
    for (iid, slug), (brand, sc, price) in zip(items, blocks):
        size, _, cond = sc.partition(" · ")
        out.append({"site": "Vinted", "id": iid, "url": f"https://www.vinted.com/items/{iid}-{slug}",
                    "title": slug.replace("-", " "), "brand": brand, "size": size, "cond": cond, "price": price})
    return out
