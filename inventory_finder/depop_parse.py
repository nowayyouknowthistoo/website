"""Parse Depop search-page HTML (saved TinyFish fetch_content JSON) into item cards."""

import html
import json
import re
import sys


def cards(page_html):
    for li in re.split(r'<li class="[^"]*listItem', page_html)[1:]:
        m = re.search(r'href="(/products/([^"/]+)/)"', li)
        if not m:
            continue
        text = [html.unescape(t).strip() for t in re.findall(r'>([^<>]+)<', li)]
        text = [t for t in text if t and not t.startswith(("M21", "(min"))]
        prices = [float(p.replace(",", "")) for p in re.findall(r'\$([\d,]+\.\d\d)', " ".join(text))]
        alt = re.search(r'aria-label="([^"]*)"', li)
        yield {
            "url": "https://www.depop.com" + m.group(1),
            "slug": m.group(2),
            "alt": html.unescape(alt.group(1)) if alt else "",
            "price": min(prices) if prices else None,
            "orig": max(prices) if len(prices) > 1 else None,
            "text": [t for t in text if not t.startswith("$")],
        }


def load(paths):
    out = {}
    for p in paths:
        for r in json.load(open(p))["results"]:
            q = re.search(r"q=([^&]+)", r["url"]).group(1)
            for c in cards(r.get("text") or ""):
                c["query"] = q
                out.setdefault(c["url"], c)
    return out


if __name__ == "__main__":
    for c in load(sys.argv[1:]).values():
        print(c["price"], c["orig"], c["slug"], c["text"][:4], sep="\t")
