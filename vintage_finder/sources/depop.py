"""Depop search results (newest first), parsed from the search page."""

import html
import re
from urllib.parse import quote

from ..net import HEADERS


def search_url(q):
    return f"https://www.depop.com/search/?q={quote(q)}&sort=newlyListed"


def parse(page: str) -> list[dict]:
    out = []
    for li in re.split(r'<li class="[^"]*listItem', page)[1:]:
        m = re.search(r'href="(/products/([^"/]+)/)"', li)
        if not m:
            continue
        slug = m.group(2)
        texts = [html.unescape(t).strip() for t in re.findall(r">([^<>]+)<", li)]
        texts = [t for t in texts if t and not t.startswith("(min")]
        prices = [float(p.replace(",", "")) for p in re.findall(r"\$([\d,]+\.\d\d)", " ".join(texts))]
        words = [t for t in texts if not t.startswith("$")]
        img = re.search(r'<img[^>]+src="(https://media-photos\.depop\.com/[^"]+)"', li)
        # The slug is "<seller>-<first words of the description>-<hash>": the best title Depop gives us.
        title = " ".join(slug.split("-")[1:-1]) if re.search(r"-[0-9a-f]{4}$", slug) else " ".join(slug.split("-")[1:])
        out.append({
            "site": "depop", "id": slug, "url": "https://www.depop.com" + m.group(1),
            "title": title, "price": min(prices) if prices else None,
            "was": max(prices) if len(prices) > 1 else None,
            "brand": words[0] if words else "", "size": words[1] if len(words) > 1 else "",
            "image": img.group(1) if img else "",
        })
    return out


def search(q, s):
    r = s.get(search_url(q), headers=HEADERS, timeout=30)
    r.raise_for_status()
    return parse(r.text)
