"""Poshmark newest listings, parsed from the search page."""

from urllib.parse import quote

from bs4 import BeautifulSoup

from ..net import HEADERS


def _price(t):
    t = (t or "").replace("$", "").replace(",", "").strip().split()
    try:
        return float(t[0])
    except (IndexError, ValueError):
        return None


def parse(page: str) -> list[dict]:
    soup = BeautifulSoup(page, "html.parser")
    out = []
    for card in soup.select("div.tile-grid-redesign, div[data-et-name='listing']"):
        a = card.select_one("a[href*='/listing/']")
        title = card.select_one(".tile-grid-redesign__title, .tile__title")
        if not a or not title:
            continue
        price = card.select_one(".tile-grid-redesign__price-current, .fw--bold")
        was = card.select_one("[class*='price-original'], s, del")
        size = card.select_one(".tile-grid-redesign__size, .tile__details__pipe__size")
        brand = card.select_one(".tile-grid-redesign__brand, .tile__details__pipe__brand")
        img = card.select_one("img")
        href = a["href"].split("?")[0]
        out.append({
            "site": "poshmark", "id": href.rsplit("-", 1)[-1], "url": "https://poshmark.com" + href,
            "title": title.get_text(" ", strip=True), "price": _price(price.get_text() if price else ""),
            "was": _price(was.get_text() if was else ""), "size": size.get_text(" ", strip=True) if size else "",
            "brand": brand.get_text(" ", strip=True) if brand else "",
            "image": (img.get("src") or img.get("data-src") or "") if img else "",
        })
    return out


def search(q, s):
    r = s.get(f"https://poshmark.com/search?query={quote(q)}&type=listings&sort_by=added_desc",
              headers=HEADERS, timeout=30)
    r.raise_for_status()
    return parse(r.text)
