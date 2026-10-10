import csv
import html
from datetime import date

from .formula import tier

FIELDS = ["tier", "score", "site", "item_type", "themes", "title", "price", "original_price",
          "size", "condition", "brand", "url", "why", "query"]


def rows(scored):
    for l, v in scored:
        yield {
            "tier": tier(v.score), "score": v.score, "site": l.site, "item_type": v.item_type,
            "themes": ", ".join(v.themes), "title": l.title, "price": l.price,
            "original_price": l.original_price or "", "size": l.size,
            "condition": l.condition, "brand": l.brand, "url": l.url,
            "why": "; ".join(v.reasons), "query": l.query,
        }


def write_csv(scored, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows(scored))


def write_html(scored, path, stats):
    """Self-contained, filterable lead sheet (also publishable as an Artifact)."""
    data = list(rows(scored))
    counts = {k: sum(1 for r in data if r["tier"] == k) for k in ("strong", "possible")}
    trs = []
    for r in data:
        price = f"${r['price']:.0f}" if r["price"] is not None else "?"
        if r["original_price"]:
            price += f" <s>${r['original_price']:.0f}</s>"
        trs.append(
            f'<tr data-site="{r["site"]}" data-type="{r["item_type"]}" data-tier="{r["tier"]}" data-price="{r["price"] or 0}">'
            f'<td><span class="pill {r["tier"]}">{r["tier"]}</span><span class="sc">{r["score"]}</span></td>'
            f'<td><a href="{html.escape(r["url"])}" target="_blank" rel="noopener">{html.escape(r["title"])}</a>'
            f'<div class="why">{html.escape(r["why"])}</div></td>'
            f'<td class="n">{price}</td><td>{html.escape(r["size"])}</td>'
            f'<td>{r["item_type"]}</td><td>{html.escape(r["themes"])}</td>'
            f'<td><span class="site {r["site"]}">{r["site"]}</span></td></tr>'
        )
    page = f"""<title>Vintage Inventory Leads</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Layout: one lead sheet - summary strip, filter bar, then a scannable table. Palette: washed denim + screenprint red. */
:root{{--bg:#f6f7f9;--surface:#ffffff;--fg:#1b1f27;--muted:#5d6676;--line:#dde1e8;--accent:#2f5d8a;--hot:#c2362b;--hot-bg:#fbe9e7;--chip:#eef1f5;
--display:"Oswald","Arial Narrow",sans-serif;--body:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#12151b;--surface:#191d25;--fg:#e6e9ef;--muted:#98a1b1;--line:#2a303b;--accent:#7fb0e0;--hot:#ff7a6b;--hot-bg:#3a1f1d;--chip:#222833;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#12151b;--surface:#191d25;--fg:#e6e9ef;--muted:#98a1b1;--line:#2a303b;--accent:#7fb0e0;--hot:#ff7a6b;--hot-bg:#3a1f1d;--chip:#222833;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 var(--body);padding:28px 16px}}
.wrapall{{max-width:1180px;margin:0 auto;display:grid;gap:16px}}
h1{{font:600 30px/1.1 var(--display);letter-spacing:.02em;text-transform:uppercase;margin:0;text-wrap:balance}}
.sub{{color:var(--muted);margin:4px 0 0}}
.stats{{display:flex;flex-wrap:wrap;gap:8px}}
.stat{{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:8px 12px;display:flex;gap:8px;align-items:baseline}}
.stat b{{font:600 20px var(--display)}} .stat span{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.06em}}
.filters{{display:flex;flex-wrap:wrap;gap:8px}}
.filters select,.filters input{{background:var(--surface);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 9px;font:inherit}}
.filters :focus-visible,a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.tablewrap{{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;width:100%;min-width:720px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:last-child td{{border-bottom:0}}
th{{font:500 11px var(--body);color:var(--muted);text-transform:uppercase;letter-spacing:.08em;cursor:pointer;user-select:none;white-space:nowrap}}
td.n{{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}}
a{{color:var(--fg);text-decoration:none;font-weight:500}} a:hover{{color:var(--accent);text-decoration:underline}}
.why{{color:var(--muted);font:11px/1.4 var(--mono);margin-top:3px}} s{{color:var(--muted)}}
.pill{{display:inline-block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;padding:2px 7px;border-radius:999px;background:var(--chip);color:var(--muted)}}
.pill.strong{{background:var(--hot-bg);color:var(--hot);font-weight:500}}
.sc{{font:12px var(--mono);color:var(--muted);margin-left:6px}}
.site{{font-size:12px;color:var(--muted)}}
.empty{{padding:24px;color:var(--muted);text-align:center}}
</style>
<div class="wrapall">
<header><h1>Vintage inventory leads</h1>
<p class="sub">Tees, crewnecks and snapbacks from Poshmark and Vinted that fit the music / pop culture / sports / cartoons formula. {stats}. Pulled {date.today():%b %d, %Y}; listings may have sold since.</p></header>
<div class="stats"><div class="stat"><b>{counts['strong']}</b><span>strong</span></div><div class="stat"><b>{counts['possible']}</b><span>possible</span></div><div class="stat"><b id="shown">{len(data)}</b><span>showing</span></div></div>
<div class="filters">
<select id="tier" aria-label="Tier"><option value="">All tiers</option><option value="strong">Strong only</option><option value="possible">Possible only</option></select>
<select id="site" aria-label="Site"><option value="">Both sites</option><option value="poshmark">Poshmark</option><option value="vinted">Vinted</option></select>
<select id="type" aria-label="Item type"><option value="">All items</option><option value="tee">Tees</option><option value="crewneck">Crewnecks</option><option value="snapback">Snapbacks</option></select>
<input id="maxp" type="number" min="0" placeholder="Max price $" aria-label="Max price">
<input id="q" type="search" placeholder="Search titles (e.g. nirvana, starter)" aria-label="Search titles">
</div>
<div class="tablewrap"><table><thead><tr><th data-k="score">Lead</th><th>Listing · why it matched</th><th data-k="price">Price</th><th>Size</th><th>Type</th><th>Theme</th><th>Site</th></tr></thead>
<tbody id="rows">{''.join(trs)}</tbody></table><div class="empty" id="empty" hidden>No listings match these filters.</div></div>
</div>
<script>
const $=id=>document.getElementById(id);
function apply(){{const t=$('tier').value,s=$('site').value,ty=$('type').value,m=parseFloat($('maxp').value),q=$('q').value.toLowerCase();let n=0;
for(const tr of $('rows').rows){{const p=parseFloat(tr.dataset.price);
const hide=(t&&tr.dataset.tier!==t)||(s&&tr.dataset.site!==s)||(ty&&tr.dataset.type!==ty)||(m>=0&&p>m)||(q&&!tr.cells[1].textContent.toLowerCase().includes(q));
tr.hidden=hide;if(!hide)n++;}}$('shown').textContent=n;$('empty').hidden=n>0;}}
['tier','site','type','maxp','q'].forEach(i=>$(i).addEventListener('input',apply));
document.querySelectorAll('th').forEach((th,i)=>th.addEventListener('click',()=>{{const b=$('rows'),r=[...b.rows];
const key=x=>i===0?parseFloat(x.cells[0].querySelector('.sc').textContent):i===2?parseFloat(x.dataset.price):x.cells[i].textContent.toLowerCase();
const asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
r.sort((a,c)=>(key(a)>key(c)?1:key(a)<key(c)?-1:0)*(asc?1:-1)).forEach(x=>b.appendChild(x));}}));
</script>"""
    with open(path, "w") as fh:
        fh.write(page)
