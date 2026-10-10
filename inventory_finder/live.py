"""Fetch search results straight from Poshmark and Vinted.

Run this from your own computer (a normal home connection). Both sites
change their pages without notice and may rate-limit or block scrapers, so
keep requests slow and few. Requires: pip install requests beautifulsoup4
"""

import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .listing import Listing, parse_price

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def poshmark(query: str, session: requests.Session) -> list[Listing]:
    url = (f"https://poshmark.com/search?query={quote(query)}"
           "&type=listings&sort_by=added_desc")
    r = session.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    # Class names as of Oct 2026 ("tile-grid-redesign").
    for card in soup.select("div.tile-grid-redesign"):
        a = card.select_one("a.tile-grid-redesign__meta-link, a[href*='/listing/']")
        title_el = card.select_one(".tile-grid-redesign__title")
        if not a or not title_el:
            continue
        price_el = card.select_one(".tile-grid-redesign__price-current")
        orig_el = card.select_one("[class*='price-original'], s, del")
        size_el = card.select_one(".tile-grid-redesign__size")
        out.append(Listing(
            "poshmark", title_el.get_text(" ", strip=True),
            parse_price(price_el.get_text()) if price_el else None,
            size_el.get_text(" ", strip=True) if size_el else "",
            "https://poshmark.com" + a["href"].split("?")[0],
            original_price=parse_price(orig_el.get_text()) if orig_el else None,
            query=query,
        ))
    return out


def vinted(query: str, session: requests.Session, per_page: int = 96) -> list[Listing]:
    # Visiting the homepage sets the anonymous session cookie the API needs.
    if not session.cookies.get("access_token_web", domain=".vinted.com"):
        session.get("https://www.vinted.com/", headers={"User-Agent": UA}, timeout=30)
    r = session.get(
        "https://www.vinted.com/api/v2/catalog/items",
        params={"search_text": query, "order": "newest_first", "per_page": per_page, "page": 1},
        headers={"User-Agent": UA, "Accept": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for it in r.json().get("items", []):
        price = it.get("price")
        if isinstance(price, dict):
            price = price.get("amount")
        out.append(Listing(
            "vinted", it.get("title", ""), parse_price(str(price or "")),
            it.get("size_title") or "", it.get("url") or f"https://www.vinted.com/items/{it['id']}",
            brand=it.get("brand_title") or "", condition=it.get("status") or "", query=query,
        ))
    return out


def fetch_all(queries: dict[str, list[str]], delay: float = 3.0) -> list[Listing]:
    session = requests.Session()
    listings = []
    for site, qs in queries.items():
        fn = {"poshmark": poshmark, "vinted": vinted}[site]
        for q in qs:
            try:
                got = fn(q, session)
                print(f"  {site:8} {len(got):3} listings  '{q}'")
                listings += got
            except requests.RequestException as e:
                print(f"  {site:8} FAILED '{q}': {e}")
            time.sleep(delay)
    return listings
