"""Write the Brockum / Winterland under-$35 list as a filterable HTML page and a CSV.

  python3 -m inventory_finder.brockum_report
"""

import csv
import html
import json
import re
from datetime import date
from pathlib import Path

from .brockum import MAX_PRICE, collect

OUT = Path("output/brockum")


def enrich(it):
    text = f'{it["title"]} {it.get("text", "")}'.lower()
    label = "Brockum" if re.search(r"brock?um|brockam", text) else "Winterland"
    year = re.search(r"\b(19[6-9]\d|20[0-2]\d)\b", it["title"])
    decade = re.search(r"\b(70|80|90)'?s\b", it["title"].lower())
    era = year.group(1) if year else (decade.group(1) + "s" if decade else "")
    flags = [f for f, p in (("single stitch", r"single[- ]?stitch|single stich"), ("made in USA", r"made in usa|usa made"),
                            ("double sided", r"double[- ]sided|2[- ]sided"), ("long sleeve", r"long ?sleeve|\bl/s\b"),
                            ("deadstock", r"deadstock|\bnos\b")) if re.search(p, text)]
    if it.get("offer"):
        flags.append("best offer")
    if it.get("bids"):
        flags.append(it["bids"])
    return {**it, "label": label, "era": era, "flags": flags}


def main():
    rows = sorted((enrich(r) for r in collect()), key=lambda r: r["price"])
    OUT.mkdir(parents=True, exist_ok=True)
    keys = ["label", "site", "price", "was", "size", "cond", "ship", "era", "flags", "title", "url"]
    with open(OUT / "brockum_winterland_under35.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "flags": ", ".join(r["flags"])})
    data = [{k: r.get(k) for k in keys} for r in rows]
    counts = {s: sum(r["site"] == s for r in rows) for s in sorted({r["site"] for r in rows})}
    page = TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/")) \
        .replace("__TOTAL__", str(len(rows))) \
        .replace("__BROCKUM__", str(sum(r["label"] == "Brockum" for r in rows))) \
        .replace("__WINTER__", str(sum(r["label"] == "Winterland" for r in rows))) \
        .replace("__SITES__", " · ".join(f"{html.escape(k)} {v}" for k, v in counts.items())) \
        .replace("__DATE__", f"{date.today():%b %d, %Y}").replace("__MAX__", f"{MAX_PRICE:.0f}")
    (OUT / "brockum_winterland_under35.html").write_text(page)
    print(len(rows), "listings ->", OUT)


TEMPLATE = r"""<title>Brockum &amp; Winterland Under $35</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;700&family=Work+Sans:wght@400;500&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a buyer's sheet. Count strip, sticky filter bar, then one dense table sorted cheapest first.
   Palette: tour-shirt black on unbleached cotton, with a faded screenprint red for prices. */
:root{--bg:#f3f1ec;--surface:#fbfaf7;--fg:#1d1b18;--muted:#6d675e;--line:#dfdad0;--accent:#b23a2a;--chip:#ebe7de;--brk:#2f4f7a;--wtr:#6b4f8a;
--display:"Archivo Narrow","Arial Narrow",sans-serif;--body:"Work Sans",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141311;--surface:#1c1a17;--fg:#ece8df;--muted:#a39d92;--line:#2f2c27;--accent:#ff8a70;--chip:#26231f;--brk:#8fb2e6;--wtr:#c3a4e8;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141311;--surface:#1c1a17;--fg:#ece8df;--muted:#a39d92;--line:#2f2c27;--accent:#ff8a70;--chip:#26231f;--brk:#8fb2e6;--wtr:#c3a4e8;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:14px/1.45 var(--body)}
.wrap{max-width:1180px;margin:0 auto;padding-block:24px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:14px}
h1{font:700 32px/1.05 var(--display);text-transform:uppercase;letter-spacing:.02em;margin:0;text-wrap:balance}
.sub{color:var(--muted);margin:4px 0 0;max-width:72ch}
.counts{display:flex;flex-wrap:wrap;gap:16px;font:13px var(--mono);color:var(--muted)}
.counts b{font:600 20px var(--display);color:var(--fg);margin-right:4px}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:3;background:var(--bg);padding-block:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;border-bottom:1px solid var(--line)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
.bar select,.bar input{background:var(--surface);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 9px;font:inherit;min-width:0}
#q{flex:1 1 200px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
#shown{font:12px var(--mono);color:var(--muted);margin-left:auto}
.tablewrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;min-width:760px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font:500 11px var(--body);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);white-space:nowrap;cursor:pointer;user-select:none}
th[aria-sort] ::after{content:""}
tr:last-child td{border-bottom:0}
td.price{font:600 15px var(--mono);color:var(--accent);white-space:nowrap;font-variant-numeric:tabular-nums}
td.price s{font-weight:400;font-size:11px;color:var(--muted);display:block}
a{color:var(--fg);text-decoration:none;font-weight:500}a:hover{text-decoration:underline;color:var(--accent)}
.lab{font:700 11px var(--display);text-transform:uppercase;letter-spacing:.08em}
.lab.Brockum{color:var(--brk)}.lab.Winterland{color:var(--wtr)}
.f{display:inline-block;font-size:11px;background:var(--chip);color:var(--muted);border-radius:999px;padding:1px 7px;margin:3px 4px 0 0}
.m{color:var(--muted);font-size:12px}
.era{font:12px var(--mono)}
.empty{padding:28px;text-align:center;color:var(--muted)}
footer{color:var(--muted);font-size:12px;max-width:80ch}
</style>
<div class="wrap">
<header><h1>Brockum &amp; Winterland under $__MAX__</h1>
<p class="sub">Every listing on this sheet has Brockum or Winterland in the title or brand, costs $__MAX__ or less (before shipping) and doesn't say modern, reprint or brand new. Authenticity is for you to judge from the photos. Pulled __DATE__; cheap ones sell fast.</p></header>
<div class="counts"><span><b>__TOTAL__</b>listings</span><span><b>__BROCKUM__</b>Brockum</span><span><b>__WINTER__</b>Winterland</span><span>__SITES__</span></div>
<div class="bar">
<select id="label" aria-label="Label"><option value="">Both labels</option><option>Brockum</option><option>Winterland</option></select>
<select id="site" aria-label="Site"><option value="">All sites</option></select>
<select id="size" aria-label="Size"><option value="">Any size</option><option>S</option><option>M</option><option>L</option><option>XL</option><option>2XL+</option></select>
<select id="era" aria-label="Era"><option value="">Any era</option><option value="old">Dated 1999 or earlier</option><option value="new">Dated 2000 or later</option><option value="none">No date in title</option></select>
<input id="maxp" type="number" min="0" max="35" step="1" placeholder="Max $" aria-label="Max price" style="width:84px">
<input id="q" type="search" placeholder="Search: single stitch, metallica, 1991…" aria-label="Search titles">
<span id="shown"></span>
</div>
<div class="tablewrap"><table><thead><tr><th data-k="price">Price</th><th data-k="title">Listing</th><th data-k="size">Size</th><th data-k="era">Year</th><th data-k="cond">Condition · shipping</th><th data-k="site">Site</th></tr></thead>
<tbody id="rows"></tbody></table><div class="empty" id="empty" hidden>No listings match these filters.</div></div>
<footer>Prices are list prices before shipping; eBay auctions show the current bid. Poshmark and Mercari take offers on most listings. Some Winterland lines (Classic Rock, Y2K tour merch) date from the 2000s; the Year column shows what the seller wrote.</footer>
</div>
<script>
const DATA=__DATA__;
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
[...new Set(DATA.map(r=>r.site))].sort().forEach(s=>$("site").insertAdjacentHTML("beforeend",`<option>${esc(s)}</option>`));
function sizeKey(s){s=(s||"").toUpperCase();if(/2X|XXL|3X|4X/.test(s))return"2XL+";if(/\bXL\b|X-LARGE|EXTRA LARGE/.test(s))return"XL";if(/\bL\b|LARGE/.test(s))return"L";if(/\bM\b|MEDIUM/.test(s))return"M";if(/\bS\b|SMALL/.test(s))return"S";return"";}
let sortK="price",asc=true;
function render(){
  const lab=$("label").value,site=$("site").value,size=$("size").value,era=$("era").value,mx=parseFloat($("maxp").value),q=$("q").value.toLowerCase().trim();
  let rows=DATA.filter(r=>(!lab||r.label===lab)&&(!site||r.site===site)&&(!size||sizeKey(r.size)===size)
    &&(!era||(era==="none"?!r.era:era==="old"?(r.era&&(r.era.endsWith("s")||+r.era<2000)):(r.era&&!r.era.endsWith("s")&&+r.era>=2000)))
    &&!(mx>=0&&r.price>mx)&&(!q||(r.title+" "+r.flags.join(" ")).toLowerCase().includes(q)));
  rows.sort((a,b)=>{const x=a[sortK]??"",y=b[sortK]??"";return (x>y?1:x<y?-1:0)*(asc?1:-1);});
  $("rows").innerHTML=rows.map(r=>`<tr><td class="price">$${r.price.toFixed(2)}${r.was&&r.was>r.price?`<s>$${r.was.toFixed(2)}</s>`:""}</td>
    <td><span class="lab ${r.label}">${r.label}</span><br><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a><div>${r.flags.map(f=>`<span class="f">${esc(f)}</span>`).join("")}</div></td>
    <td>${esc(r.size)}</td><td class="era">${esc(r.era)}</td><td class="m">${esc([r.cond,r.ship].filter(Boolean).join(" · "))}</td><td class="m">${esc(r.site)}</td></tr>`).join("");
  $("empty").hidden=rows.length>0;$("shown").textContent=`${rows.length} shown`;
}
["label","site","size","era","maxp","q"].forEach(id=>$(id).addEventListener("input",render));
document.querySelectorAll("th[data-k]").forEach(th=>th.addEventListener("click",()=>{const k=th.dataset.k;asc=sortK===k?!asc:true;sortK=k;render();}));
render();
</script>"""

if __name__ == "__main__":
    main()
