import glob
import json

from vintage_finder.sources import depop, ebay, poshmark
from vintage_finder.vintage import analyse


def test_depop_parses_saved_search_pages():
    files = sorted(glob.glob("data/depop/d*.json"))
    items = [it for f in files for r in json.load(open(f))["results"] for it in depop.parse(r["text"] or "")]
    assert len(items) > 300
    assert all(it["url"].startswith("https://www.depop.com/products/") for it in items)
    assert sum(it["price"] is not None for it in items) > 0.95 * len(items)
    assert sum(bool(it["image"]) for it in items) > 0.9 * len(items)


def test_ebay_parses_both_layouts():
    page = """
    <li class="s-item s-item__pl-on-bottom"><a class="s-item__link" href="https://www.ebay.com/itm/111?x=1">
      <div class="s-item__title"><span>Shop on eBay</span></div></a></li>
    <li class="s-item"><a class="s-item__link" href="https://www.ebay.com/itm/222?hash=1">
      <img src="https://i.ebayimg.com/a.jpg"><div class="s-item__title"><span>Vintage 90s Nirvana Sliver Tee</span></div></a>
      <span class="s-item__price">$45.00</span></li>
    <li class="s-card s-card--horizontal"><a href="https://www.ebay.com/itm/333"><img data-src="https://i.ebayimg.com/b.jpg"></a>
      <div class="s-card__title"><span>RHCP 1992 single stitch</span></div><span class="s-card__price">$1,200.00</span></li>
    """
    got = ebay.parse(page)
    assert [(g["id"], g["price"]) for g in got] == [("222", 45.0), ("333", 1200.0)]
    assert got[1]["image"] == "https://i.ebayimg.com/b.jpg"


def test_poshmark_parses_tile():
    page = """<div class="tile-grid-redesign"><a href="/listing/Vintage-Nirvana-Tee-abc123?x=1">
      <img src="https://di2ponv0v5otw.cloudfront.net/x.jpg"></a>
      <a class="tile-grid-redesign__title">Vintage Nirvana Tee</a>
      <span class="tile-grid-redesign__price-current">$40</span><span class="tile-grid-redesign__size">XL</span></div>"""
    (it,) = poshmark.parse(page)
    assert it["price"] == 40 and it["size"] == "XL" and it["id"] == "abc123"


def test_analyse_flags():
    v = analyse("1990s vintage Nirvana Sliver bootleg single stitch made in USA", "Giant", price=100)
    assert v["band"] == "Nirvana" and "underpriced" in v["flags"] and v["tag"] == "old tag"
    assert analyse("Nirvana tee REPRINT single stitch", price=20)["modern"]
    assert analyse("Nirvana In Utero Live 93 tee", price=7)["flags"] == ["80s/90s date"]  # no deal without a physical tell
    assert analyse("Vintage 1989 hot stuff chili pepper tee")["band"] is None
    assert analyse("Lollapalooza 1992", desc="sealed in a box until 2022")["modern"] is False
    assert "misspelled title" in analyse("vintage nirvanna shirt")["flags"]
