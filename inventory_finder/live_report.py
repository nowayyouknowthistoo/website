"""Render the hand-verified live listings (data/verify/live_under_800.json).

  python -m inventory_finder.live_report
"""

import csv
import html
import json
from pathlib import Path

SRC = Path("data/verify/live_under_800.json")
OUT = Path("output/photo_hunt")

SECTIONS = [
    ("deal", "Make an offer", "Listed over budget, but the seller has already accepted less in public."),
    ("ls", "Long sleeves, $800 or under", "Your priority. Starred listings are the closest to your 12 photos."),
    ("tee", "Same designs as tees, $800 or under", "The graphics from your photos, printed on short sleeves."),
]


def esc(s):
    return html.escape(str(s))


def card(it):
    price = f"${it['price']:,.2f}".replace(".00", "")
    if it.get("list_price"):
        price = f"{price} offer <s>${it['list_price']:,}</s>"
    if it.get("price_note"):
        price += f' <span class="pn">({esc(it["price_note"])})</span>'
    flags = ('<span class="flag star">closest match</span>' if it.get("star") else "") + \
            ('<span class="flag check">ask for tag photos</span>' if it.get("check") else "")
    return f"""<article class="card" data-price="{it['price']}" data-site="{esc(it['site'])}">
<div class="top"><span class="site">{esc(it['site'])}</span>{flags}<span class="price">{price}</span></div>
<h3><a href="{esc(it['url'])}" target="_blank" rel="noopener">{esc(it['title'])}</a></h3>
<dl><dt>Size</dt><dd>{esc(it['size'])}</dd><dt>Sleeve</dt><dd>{esc(it['sleeve'])}</dd>
<dt>Matches</dt><dd>{esc(it['photo'])}</dd><dt>Tag / era</dt><dd>{esc(it['tag'])}</dd>
<dt>Condition</dt><dd>{esc(it['cond'])}</dd></dl>
<p class="note">{esc(it['notes'])}</p></article>"""


def build(data, path):
    items = data["items"]
    secs = []
    for key, title, sub in SECTIONS:
        rows = sorted((i for i in items if i["sec"] == key), key=lambda i: (not i.get("star"), -i["price"]))
        secs.append(f'<section><h2>{title} <span class="n">{len(rows)}</span></h2><p class="sub">{sub}</p>'
                    f'<div class="grid">{"".join(card(i) for i in rows)}</div></section>')

    def lst(rows, fmt):
        return "<ul class='mini'>" + "".join(fmt(r) for r in rows) + "</ul>"

    over = lst(data["over"], lambda r: f'<li><a href="{esc(r[0])}" target="_blank" rel="noopener">{esc(r[1])}</a> <span class="mono">${r[2]:,.0f}</span></li>')
    gone = lst(data["gone"], lambda r: f'<li><a href="{esc(r[0])}" target="_blank" rel="noopener">{esc(r[0].split("//")[1][:48])}…</a> {esc(r[1])}</li>')
    skip = lst(data["skipped"], lambda r: f'<li><a href="{esc(r[0])}" target="_blank" rel="noopener">{esc(r[0].split("//")[1][:48])}…</a> {esc(r[1])}</li>')
    n_ls = sum(1 for i in items if i["sleeve"] != "Short")
    page = f"""<title>Live Nirvana Finds</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Layout: summary + filter bar, then card grids per section (deal, long sleeves, tees), then compact excluded lists. Palette: washed denim + screenprint red. */
:root{{--bg:#f6f7f9;--surface:#fff;--fg:#1b1f27;--muted:#5d6676;--line:#dde1e8;--accent:#2f5d8a;--hot:#c2362b;--hot-bg:#fbe9e7;--warn:#8a5a00;--warn-bg:#fdf3dc;--chip:#eef1f5;
--display:"Oswald","Arial Narrow",sans-serif;--body:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#12151b;--surface:#191d25;--fg:#e6e9ef;--muted:#98a1b1;--line:#2a303b;--accent:#7fb0e0;--hot:#ff7a6b;--hot-bg:#3a1f1d;--warn:#f0c060;--warn-bg:#3a2f15;--chip:#222833;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#12151b;--surface:#191d25;--fg:#e6e9ef;--muted:#98a1b1;--line:#2a303b;--accent:#7fb0e0;--hot:#ff7a6b;--hot-bg:#3a1f1d;--warn:#f0c060;--warn-bg:#3a2f15;--chip:#222833;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 var(--body);padding:28px 16px;margin:0}}
.wrap{{max-width:1180px;margin:0 auto;display:grid;gap:22px}}
h1{{font:600 30px/1.1 var(--display);letter-spacing:.02em;text-transform:uppercase;margin:0;text-wrap:balance}}
h2{{font:600 20px/1.2 var(--display);text-transform:uppercase;letter-spacing:.03em;margin:0}}
h2 .n{{font:13px var(--mono);color:var(--muted);margin-left:6px}}
.sub{{color:var(--muted);margin:4px 0 10px}}
.filters{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
.filters select,.filters input{{background:var(--surface);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 9px;font:inherit}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:8px}}
.top{{display:flex;flex-wrap:wrap;gap:6px;align-items:center}}
.site{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
.price{{margin-left:auto;font:500 16px var(--mono);font-variant-numeric:tabular-nums}} .price s{{color:var(--muted);font-size:12px}} .pn{{font-size:11px;color:var(--muted)}}
.flag{{font-size:11px;padding:2px 7px;border-radius:999px}} .star{{background:var(--hot-bg);color:var(--hot)}} .check{{background:var(--warn-bg);color:var(--warn)}}
h3{{font:500 15px/1.3 var(--body);margin:0}} a{{color:var(--fg);text-decoration:none}} a:hover{{color:var(--accent);text-decoration:underline}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:3px 10px;margin:0;font-size:13px}} dt{{color:var(--muted)}} dd{{margin:0}}
.note{{margin:0;font-size:13px;color:var(--fg);border-top:1px solid var(--line);padding-top:8px}}
details{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}
summary{{cursor:pointer;font:600 15px var(--display);text-transform:uppercase;letter-spacing:.03em}}
.mini{{margin:10px 0 0;padding-left:18px;display:grid;gap:4px;font-size:13px;color:var(--muted)}} .mini a{{color:var(--fg)}}
.mono{{font-family:var(--mono)}}
.empty{{color:var(--muted)}}
</style>
<div class="wrap">
<header><h1>Live Nirvana finds under $800</h1>
<p class="sub">Every listing below was opened and checked on {data['checked']}: page live, Buy It Now or available, price $800 or under. {len(items)} listings ({n_ls} long sleeves). Listings sell fast, so recheck before you pay.</p></header>
<div class="filters"><select id="site" aria-label="Site"><option value="">All sites</option>{"".join(f"<option>{esc(s)}</option>" for s in sorted({i['site'] for i in items}))}</select>
<input id="maxp" type="number" min="0" placeholder="Max price $" aria-label="Max price"></div>
{"".join(secs)}
<details><summary>Live but over $800 ({len(data['over'])})</summary>{over}</details>
<details><summary>Gone since the last list: sold, ended, removed ({len(data['gone'])})</summary>{gone}</details>
<details><summary>Skipped as modern or reprint ({len(data['skipped'])})</summary>{skip}</details>
<p class="sub">Couldn't verify: Grailed, Etsy and Facebook block automated checks, so none of their listings are included here.</p>
</div>
<script>
const s=document.getElementById('site'),m=document.getElementById('maxp');
function f(){{const mx=parseFloat(m.value);document.querySelectorAll('.card').forEach(c=>{{c.hidden=(s.value&&c.dataset.site!==s.value)||(mx>=0&&parseFloat(c.dataset.price)>mx);}});}}
s.addEventListener('input',f);m.addEventListener('input',f);
</script>"""
    path.write_text(page)


def main():
    data = json.loads(SRC.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    build(data, OUT / "live_under_800.html")
    keys = ["sec", "site", "title", "price", "list_price", "size", "sleeve", "photo", "tag", "cond", "notes", "url"]
    with open(OUT / "live_under_800.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(data["items"])
    print(f"wrote {OUT/'live_under_800.html'} and .csv ({len(data['items'])} listings)")


if __name__ == "__main__":
    main()
