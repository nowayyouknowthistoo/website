"""Parse eBay search pages fetched as markdown (with links) by TinyFish fetch_content.

Each result card is a markdown bullet: title, size/brand, condition, price, shipping, location and the
listing start time ("Oct-30 10:22"). Item URLs come from the result's link list, one item id per card, in order.
"""
import re
from datetime import date

MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def listed_on(text, today):
    m = re.search(r"^\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{1,2}) \d\d:\d\d\s*$", text, re.M)
    if not m:
        return None
    mon, day = MONTHS[m.group(1)], int(m.group(2))
    for year in range(today.year, today.year - 4, -1):  # no year shown; take the latest past date that exists (Feb 29)
        try:
            d = date(year, mon, day)
        except ValueError:
            continue
        if d <= today:
            return d
    return None


def cards(result, today):
    text, links = result.get("text") or "", result.get("links") or []
    ids = []
    for m in re.findall(r"/itm/(\d+)", " ".join(links)):
        if m not in ids:
            ids.append(m)
    blocks = [b for b in re.split(r"\n\* ", "\n" + text) if "Opens in a new window" in b]
    if len(blocks) != len(ids):  # can't pair titles with links safely
        return []
    out = []
    for iid, b in zip(ids, blocks):
        lines = [x.strip() for x in b.split("\n") if x.strip()]
        title = lines[0].split("Opens in a new window")[0].strip()
        prices = re.findall(r"^\$([\d,]+\.\d\d)$", "\n".join(lines), re.M)
        size = next((x.split(" · ")[0].removeprefix("Size ").strip() for x in lines if x.startswith("Size ")), "")
        brand = next((x.split(" · ", 1)[1] for x in lines if x.startswith("Size ") and " · " in x), "")
        out.append({
            "site": "eBay", "id": iid, "url": f"https://www.ebay.com/itm/{iid}", "title": title,
            "price": float(prices[0].replace(",", "")) if prices else None, "size": size, "brand": brand,
            "cond": next((x for x in lines if x in ("Pre-Owned", "New (Other)", "Brand New", "New with tags")), ""),
            "bids": next((x for x in lines if re.fullmatch(r"\d+ bids?", x)), ""),
            "where": next((x.removeprefix("Located in ") for x in lines if x.startswith("Located in")), ""),
            "listed": listed_on(b, today),
        })
    return out
