"""eBay newest listings.

With a free eBay developer key (EBAY_CLIENT_ID / EBAY_CLIENT_SECRET in the environment) this uses
eBay's official Browse API, the fastest and most reliable option. Without one it reads the
public search page.
"""

import base64
import html
import os
import re
import time
from urllib.parse import quote

from ..net import HEADERS

_token = {"value": None, "expires": 0}


def _api_token(s):
    if _token["value"] and time.time() < _token["expires"] - 60:
        return _token["value"]
    cid, secret = os.environ["EBAY_CLIENT_ID"], os.environ["EBAY_CLIENT_SECRET"]
    r = s.post("https://api.ebay.com/identity/v1/oauth2/token",
               headers={"Authorization": "Basic " + base64.b64encode(f"{cid}:{secret}".encode()).decode(),
                        "Content-Type": "application/x-www-form-urlencoded"},
               data="grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope",
               timeout=30)
    r.raise_for_status()
    j = r.json()
    _token.update(value=j["access_token"], expires=time.time() + j["expires_in"])
    return _token["value"]


def _api_search(q, s):
    r = s.get("https://api.ebay.com/buy/browse/v1/item_summary/search",
              params={"q": q, "sort": "newlyListed", "limit": 200, "category_ids": "11450"},  # clothing
              headers={"Authorization": f"Bearer {_api_token(s)}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"},
              timeout=30)
    r.raise_for_status()
    out = []
    for it in r.json().get("itemSummaries", []):
        out.append({
            "site": "ebay", "id": it["itemId"], "url": it["itemWebUrl"].split("?")[0], "title": it["title"],
            "price": float(it["price"]["value"]) if it.get("price") else None, "was": None,
            "brand": "", "size": "", "image": (it.get("image") or {}).get("imageUrl", ""),
            "desc": it.get("condition", ""), "listed_at": it.get("itemCreationDate"),
        })
    return out


def parse(page: str) -> list[dict]:
    """Public search page; handles both the s-item and newer s-card layouts."""
    out, seen = [], set()
    for block in re.split(r'<li[^>]+class="[^"]*\bs-(?:item|card)\b', page)[1:]:
        m = re.search(r'href="(https://www\.ebay\.com/itm/(\d+))', block)
        if not m or m.group(2) in seen:
            continue
        seen.add(m.group(2))
        title = re.search(r'class="[^"]*(?:s-item__title|s-card__title)[^"]*"[^>]*>(?:<[^>]+>)*([^<]{5,})', block)
        if not title or "Shop on eBay" in title.group(1):
            continue
        price = re.search(r"\$([\d,]+\.\d\d)", block)
        img = re.search(r'<img[^>]+(?:src|data-src)="(https://i\.ebayimg\.com/[^"]+)"', block)
        out.append({
            "site": "ebay", "id": m.group(2), "url": m.group(1), "title": html.unescape(title.group(1)).strip(),
            "price": float(price.group(1).replace(",", "")) if price else None, "was": None,
            "brand": "", "size": "", "image": img.group(1) if img else "",
        })
    return out


def search(q, s):
    if os.environ.get("EBAY_CLIENT_ID"):
        return _api_search(q, s)
    r = s.get(f"https://www.ebay.com/sch/i.html?_nkw={quote(q)}&_sop=10&_ipg=120", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return parse(r.text)
