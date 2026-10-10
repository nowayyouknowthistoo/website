"""Parse saved TinyFish `fetch_content` results for Poshmark/Vinted search pages.

The cloud environment this tool was first run in cannot reach Poshmark or
Vinted directly, so search pages were rendered through TinyFish with:

  Poshmark: include_selectors=["[data-et-name='listing']"], links=true
  Vinted:   include_selectors=["[data-testid^='product-item-id-']"], links=true

Each saved file is the raw JSON response ({"results": [...], "errors": [...]}).
"""

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .listing import Listing, parse_price

PRICE = re.compile(r"^\$[\d,]+(\.\d\d)?$")


def _query(url: str) -> str:
    qs = parse_qs(urlparse(url).query)
    return unquote((qs.get("query") or qs.get("search_text") or [""])[0])


def _unique(links, needle):
    return list(dict.fromkeys(l for l in links if needle in l))


def parse_poshmark(result) -> list[Listing]:
    """Poshmark serves two tile layouts:
      new: title / price [newline original price] / size
      old: title / price / "Size: X" newline brand / seller / [like count]
    Both have the title right before the price block and the size right after."""
    urls = _unique(result.get("links", []), "/listing/")
    blocks = [b.strip() for b in result["text"].split("\n\n") if b.strip()]
    price_at = [i for i, b in enumerate(blocks)
                if i > 0 and all(PRICE.match(x) for x in b.split("\n"))]
    # Link order usually matches card order, but not always (some tiles have
    # no link in the rendered markup), so pair them by the title in the URL.
    def key(t):
        return re.sub(r"[^a-z0-9]", "", t.lower())[:30]
    by_key = {}
    for u in urls:
        slug = urlparse(u).path.rsplit("/", 1)[-1].rsplit("-", 1)[0]
        by_key.setdefault(key(slug), u)
    q = _query(result["url"])
    out = []
    for i in price_at:
        url = by_key.get(key(blocks[i - 1]))
        if not url:
            continue
        prices = blocks[i].split("\n")
        size_lines = blocks[i + 1].split("\n") if i + 1 < len(blocks) else [""]
        size = size_lines[0].removeprefix("Size:").strip()
        brand = size_lines[1] if len(size_lines) > 1 else ""
        out.append(Listing("poshmark", blocks[i - 1], parse_price(prices[0]), size, url,
                           brand=brand,
                           original_price=parse_price(prices[1]) if len(prices) > 1 else None,
                           query=q))
    return out


def _title_from_vinted_url(url: str) -> str:
    slug = urlparse(url).path.rsplit("/", 1)[-1]
    slug = re.sub(r"^\d+-", "", slug)
    return slug.replace("-", " ")


def parse_vinted(result) -> list[Listing]:
    """Cards are rendered as: [fav count] / brand-or-title / [Bumped] /
    'size · condition' / price / 'price incl.'. The full title is only in the
    item URL slug, so we take it from there."""
    urls = _unique(result.get("links", []), "/items/")
    blocks = [b.strip() for b in result["text"].split("\n\n") if b.strip()]
    cards, cur = [], []
    for b in blocks:
        cur.append(b)
        if b.endswith("incl."):
            cards.append(cur)
            cur = []
    if len(cards) != len(urls):
        raise ValueError(f"vinted: {len(cards)} cards vs {len(urls)} links for {result['url']}")
    q = _query(result["url"])
    out = []
    for card, url in zip(cards, urls):
        body = [b for b in card if not b.isdigit() and b != "Bumped"]
        price = parse_price(body[-2]) if len(body) >= 2 else None
        size_cond = body[-3] if len(body) >= 3 else ""
        size, _, cond = size_cond.partition(" · ")
        if "·" not in size_cond:  # no size shown, only a condition
            size, cond = "", size_cond
        head = body[-4] if len(body) >= 4 else ""
        slug_title = _title_from_vinted_url(url)
        # `head` is either the seller's (possibly cut-off) title or just a
        # brand name; the URL slug always carries the full title.
        is_title = len(head.split()) > 4
        brand = "" if is_title else head
        title = head if is_title and len(head) >= len(slug_title) else slug_title
        out.append(Listing("vinted", title, price, size.strip(), url.split("?")[0],
                           brand=brand, condition=cond.strip(), query=q))
    return out


def load(paths) -> list[Listing]:
    listings = []
    for path in paths:
        data = json.loads(Path(path).read_text())
        for r in data["results"]:
            host = urlparse(r["url"]).netloc
            if "poshmark" in host:
                listings += parse_poshmark(r)
            elif "vinted" in host:
                listings += parse_vinted(r)
    return listings
