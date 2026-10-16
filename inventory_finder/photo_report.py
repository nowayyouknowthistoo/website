"""Render output/photo_hunt/candidates.json as a filterable page."""

import html
import json
from collections import Counter
from pathlib import Path

from .photo_match import DESIGNS

GROUP_ORDER = [
    "Your designs: possible originals",
    "Same family: 90s bootleg / Euro long sleeves",
    "Reprint or modern: avoid",
    "Sold / reference (price comps)",
]
GROUP_NOTE = {
    GROUP_ORDER[0]: "Titles match one of your 12 photos. Check the tag, single-stitch hems and print wear before buying.",
    GROUP_ORDER[1]: "Not one of your exact graphics, but the same kind of piece: 90s bootleg, parking-lot or Euro Nirvana long sleeves, many with sleeve prints.",
    GROUP_ORDER[2]: "The seller says reprint, vintage-style or modern, or it is current licensed merch. These are here so you can recognise them.",
    GROUP_ORDER[3]: "Already sold, or posts and forum threads. Useful as proof a design exists and what it goes for.",
}
PILL = {GROUP_ORDER[0]: "match", GROUP_ORDER[1]: "family", GROUP_ORDER[2]: "avoid", GROUP_ORDER[3]: "comp"}

# Hand-picked highlights, shown above the table.
HIGHLIGHTS = [
    ("https://www.ebay.com/itm/287451400329", "Live eBay auction: 1992 Roskilde long sleeve, XL",
     "Your photo 9. At $709 with 30 bids and about 2.5 days left on Oct 16. Small armpit repair, fading."),
    ("https://www.grailed.com/listings/104006430-nirvana-ultra-rare-90s-nirvana-nevermind-one-dollar-tie-dye-cobain",
     "Grailed: 90s Nevermind One Dollar tie-dye long sleeve, XL, $2,000",
     "Screen Stars, made in Ireland, Euro bootleg, single stitch. Closest match to your tie-dye photo."),
    ("https://weber-auction.com/products/90s-kurt-cobain-memorial-nevermind-t-shirt-827f1",
     "Weber: 90s Kurt Cobain memorial 'Nevermind' long sleeve",
     "NIRVANA logos down both sleeves, French memorial back. Same Euro-boot family as your photos."),
    ("https://www.depop.com/products/thriftyteucker-rare-vintage-nirvana-kurt-cobain-6328/",
     "Depop / Poshmark: 1994 Kurt Cobain memorial long sleeve, XL",
     "Full NIRVANA prints on both sleeves, memorial quote on the back. Listed around $1,750."),
    ("https://shop.deadfamousvintage.com/products/nirvana-in-utero-rape-me-euro-bootleg-longsleeve-tee",
     "Dead Famous Vintage: In Utero 'Rape Me' Euro bootleg long sleeve",
     "90s, cut Euro tag, L/XL. Same era and maker type as your In Utero bootleg photo."),
    ("https://www.ebay.com/itm/365377477305", "eBay: 90s Smiley gradient long sleeve, Euro tag XL",
     "Euro-tag smiley long sleeve, the same piece Kid Cudi wore."),
]


def build(rows, path):
    counts = Counter(r["group"] for r in rows)
    dcounts = Counter(r["design"] for r in rows if r["design"])
    design_opts = "".join(
        f'<option value="{k}">{html.escape(v[0])} ({dcounts.get(k, 0)})</option>' for k, v in DESIGNS.items())
    sites = sorted({r["site"] for r in rows})
    site_opts = "".join(f"<option>{html.escape(s)}</option>" for s in sites)

    hl = "".join(
        f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(t)}</a><span>{html.escape(n)}</span></li>'
        for u, t, n in HIGHLIGHTS)

    sections = []
    for g in GROUP_ORDER:
        items = [r for r in rows if r["group"] == g]
        items.sort(key=lambda r: (r["design"] is None, r["design"] or "", -(r.get("price") or 0)))
        trs = []
        for r in items:
            price = f"${r['price']:,.0f}" if r.get("price") else "–"
            design = DESIGNS[r["design"]][0] if r["design"] else "–"
            ls = "Yes" if r["long_sleeve"] else "?"
            trs.append(
                f'<tr data-design="{r["design"] or ""}" data-site="{html.escape(r["site"])}">'
                f'<td><a href="{html.escape(r["url"])}" target="_blank" rel="noopener">{html.escape(r["title"])}</a>'
                f'<div class="note">{html.escape((r.get("note") or "")[:220])}</div></td>'
                f'<td>{html.escape(design)}</td><td class="n">{price}</td><td>{ls}</td>'
                f'<td><span class="site">{html.escape(r["site"])}</span></td></tr>')
        sections.append(f"""
<section class="grp" data-group="{PILL[g]}">
<h2><span class="pill {PILL[g]}">{counts.get(g, 0)}</span>{html.escape(g)}</h2>
<p class="gnote">{html.escape(GROUP_NOTE[g])}</p>
<div class="tablewrap"><table><thead><tr><th>Listing</th><th>Matches photo</th><th>Price</th><th>Long sleeve</th><th>Site</th></tr></thead>
<tbody>{''.join(trs)}</tbody></table></div>
</section>""")

    total = len(rows)
    actionable = total - counts.get(GROUP_ORDER[3], 0)
    page = f"""<title>Nirvana Long Sleeve Finds</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Layout: highlights strip, filter bar, then four grouped tables. Palette: faded black tee + bleach grey + screenprint accents. */
:root{{--bg:#f5f5f3;--surface:#ffffff;--fg:#1c1c1f;--muted:#5f6068;--line:#dedfe3;--accent:#3b4fb8;
--match:#1f7a4d;--match-bg:#e3f3ea;--family:#3b4fb8;--family-bg:#e6e9f8;--avoid:#b3261e;--avoid-bg:#fbe7e5;--comp:#6b5a12;--comp-bg:#f6efd6;
--display:"Oswald","Arial Narrow",sans-serif;--body:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#121214;--surface:#1a1a1e;--fg:#e8e8ec;--muted:#9a9ba5;--line:#2c2c33;--accent:#8fa0ff;
--match:#6fd3a0;--match-bg:#173226;--family:#9fb0ff;--family-bg:#1e2442;--avoid:#ff8a80;--avoid-bg:#3a1a18;--comp:#e3c86a;--comp-bg:#33290d;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#121214;--surface:#1a1a1e;--fg:#e8e8ec;--muted:#9a9ba5;--line:#2c2c33;--accent:#8fa0ff;
--match:#6fd3a0;--match-bg:#173226;--family:#9fb0ff;--family-bg:#1e2442;--avoid:#ff8a80;--avoid-bg:#3a1a18;--comp:#e3c86a;--comp-bg:#33290d;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 var(--body);padding:28px 16px}}
.wrap{{max-width:1180px;margin:0 auto;display:grid;gap:18px}}
h1{{font:600 30px/1.1 var(--display);text-transform:uppercase;letter-spacing:.02em;margin:0;text-wrap:balance}}
h2{{font:600 19px var(--display);text-transform:uppercase;letter-spacing:.03em;margin:0;display:flex;gap:10px;align-items:center}}
.sub,.gnote{{color:var(--muted);margin:4px 0 0;max-width:75ch}}
.hl{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px}}
.hl h3{{margin:0 0 8px;font:600 14px var(--display);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}
.hl ul{{margin:0;padding:0;list-style:none;display:grid;gap:8px}}
.hl li{{display:grid;gap:2px}} .hl li span{{color:var(--muted);font-size:13px}}
.filters{{display:flex;flex-wrap:wrap;gap:8px}}
.filters select,.filters input{{background:var(--surface);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 9px;font:inherit;max-width:100%}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.grp{{display:grid;gap:8px}}
.tablewrap{{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;width:100%;min-width:720px}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:last-child td{{border-bottom:0}}
th{{font:500 11px var(--body);color:var(--muted);text-transform:uppercase;letter-spacing:.08em;white-space:nowrap}}
td.n{{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}}
a{{color:var(--fg);font-weight:500;text-decoration:none}} a:hover{{color:var(--accent);text-decoration:underline}}
.note{{color:var(--muted);font-size:12px;margin-top:3px}}
.site{{font-size:12px;color:var(--muted)}}
.pill{{display:inline-block;min-width:28px;text-align:center;font:500 12px var(--mono);padding:2px 8px;border-radius:999px}}
.pill.match{{background:var(--match-bg);color:var(--match)}} .pill.family{{background:var(--family-bg);color:var(--family)}}
.pill.avoid{{background:var(--avoid-bg);color:var(--avoid)}} .pill.comp{{background:var(--comp-bg);color:var(--comp)}}
.empty{{color:var(--muted);padding:10px 0}}
</style>
<div class="wrap">
<header><h1>Nirvana long sleeve finds</h1>
<p class="sub">{total} results for your 12 photos, searched Oct 16, 2026 across eBay, Grailed, Depop, Etsy, Poshmark, Vinted, Mercari (US and Japan), vintage shops, Instagram and collector forums. {actionable} are listings, and {counts.get(GROUP_ORDER[3],0)} are sold or reference records for pricing. Matches come from listing titles and descriptions, so open the photos before buying. Some listings may have sold since.</p></header>
<div class="hl"><h3>Start here</h3><ul>{hl}</ul></div>
<div class="filters">
<select id="design" aria-label="Photo"><option value="">All designs</option>{design_opts}<option value="none">Not one of the 12 (same family)</option></select>
<select id="site" aria-label="Site"><option value="">All sites</option>{site_opts}</select>
<select id="grp" aria-label="Group"><option value="">All groups</option><option value="match">Possible originals</option><option value="family">Same family</option><option value="avoid">Reprints / modern</option><option value="comp">Sold / reference</option></select>
<input id="q" type="search" placeholder="Search titles (e.g. euro, single stitch)" aria-label="Search">
</div>
{''.join(sections)}
</div>
<script>
const $=id=>document.getElementById(id);
function apply(){{const d=$('design').value,s=$('site').value,g=$('grp').value,q=$('q').value.toLowerCase();
document.querySelectorAll('.grp').forEach(sec=>{{let n=0;const gok=!g||sec.dataset.group===g;
sec.querySelectorAll('tbody tr').forEach(tr=>{{const dd=tr.dataset.design;
const hide=!gok||(d==='none'?dd!=='':(d&&dd!==d))||(s&&tr.dataset.site!==s)||(q&&!tr.textContent.toLowerCase().includes(q));
tr.hidden=hide;if(!hide)n++;}});sec.hidden=n===0;}});}}
['design','site','grp','q'].forEach(i=>$(i).addEventListener('input',apply));
</script>"""
    Path(path).write_text(page)


if __name__ == "__main__":
    rows = json.loads(Path("output/photo_hunt/candidates.json").read_text())
    build(rows, "output/photo_hunt/nirvana_longsleeves.html")
    import csv
    with open("output/photo_hunt/nirvana_longsleeves.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "matches_photo", "title", "price", "long_sleeve", "site", "url", "note"])
        for g in GROUP_ORDER:
            for r in rows:
                if r["group"] == g:
                    w.writerow([g, DESIGNS[r["design"]][0] if r["design"] else "", r["title"], r.get("price") or "",
                                "yes" if r["long_sleeve"] else "?", r["site"], r["url"], r.get("note", "")])
    print("wrote output/photo_hunt/nirvana_longsleeves.html and .csv")
