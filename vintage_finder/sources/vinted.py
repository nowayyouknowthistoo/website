"""Vinted newest listings via the JSON endpoint its own site uses."""

from ..net import HEADERS


def search(q, s):
    if not any(c.name == "access_token_web" for c in getattr(s.cookies, "jar", [])):
        s.get("https://www.vinted.com/", headers=HEADERS, timeout=30)  # sets the anonymous session cookie
    r = s.get("https://www.vinted.com/api/v2/catalog/items",
              params={"search_text": q, "order": "newest_first", "per_page": 96, "page": 1},
              headers={**HEADERS, "Accept": "application/json"}, timeout=30)
    r.raise_for_status()
    out = []
    for it in r.json().get("items", []):
        price = it.get("price")
        if isinstance(price, dict):
            price = price.get("amount")
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = None
        out.append({
            "site": "vinted", "id": str(it["id"]), "url": it.get("url") or f"https://www.vinted.com/items/{it['id']}",
            "title": it.get("title", ""), "price": price, "was": None,
            "brand": it.get("brand_title") or "", "size": it.get("size_title") or "",
            "image": (it.get("photo") or {}).get("url", ""), "desc": it.get("status") or "",
        })
    return out
