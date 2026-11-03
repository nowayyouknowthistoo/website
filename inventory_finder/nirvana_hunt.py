"""Recently listed 90s Nirvana / Kurt Cobain shirts on eBay and Poshmark, tagged or no tag.

  python3 -m inventory_finder.nirvana_hunt --report   # output/nirvana_recent/nirvana_recent.html + .csv
"""
import csv, json, re, sys
from datetime import date, timedelta
from pathlib import Path

from . import weekly_hunt as wh

wh.DATA = Path("data/hunt_nov03")
wh.TODAY = date(2026, 11, 3)
wh.SINCE = wh.TODAY - timedelta(days=5)
OUT = Path("output/nirvana_recent")
NIRVANA = {"Nirvana": r"nirvana|kurt cobain|\bcobain\b"}
MODERN_BRANDS = (r"abercrombie|\bh&?m\b|^hm |rock off|spencers?|daydreamer|six fifty one|s-xl|cotton on|bravado|"
                 r"urban outfitters|\bjcpenney\b|polo shirt|cowboy shirt|lot of \d")
OTHER_BANDS = (r"alice in chains|rollins|codeine|soundgarden|pearl jam|korn|limp|hendrix|prince|bikini kill|lennon|"
               r"waaf|teen spirit tm|lollapalooza|big day out|famous guitars|sub pop no comment|loser shirt")
NOT_90S = r"\by2k\b|\b00s\b|2000s|\b200\d\b|\b201\d\b|\b202\d\b"


def rows():
    out = []
    for it in wh.load():
        r = wh.judge(it, NIRVANA, need_era=True)
        t = r["title"].lower() if r else ""
        at = re.search(r"nirvana|cobain", t)
        other = re.search(OTHER_BANDS, t)
        if r and not re.search(NOT_90S, t) and not re.search(MODERN_BRANDS, t) and not (other and other.start() < at.start()):
            out.append(r)
    return sorted(out, key=lambda r: (r["listed"], r["score"]), reverse=True)


if __name__ == "__main__":
    R = rows()
    from collections import Counter
    print(len(R), Counter(r["site"] for r in R), Counter(r["listed"] for r in R))
    if "--report" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        keys = ["listed", "band", "site", "price", "size", "brand", "cond", "bids", "where", "year", "tags", "score", "title", "url"]
        with open(OUT / "nirvana_recent.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for r in R:
                w.writerow({**r, "tags": ", ".join(r["tags"])})
        page = (Path(__file__).with_name("weekly_hunt.html").read_text()
                .replace("<title>Weekly Vintage Hunt</title>", "<title>Recent Nirvana Pulls</title>")
                .replace("This week's vintage pulls", "Nirvana · just listed")
                .replace("__DATA__", json.dumps({"nirvana": [{k: r.get(k) for k in keys} for r in R]}).replace("</", "<\\/"))
                .replace('const LABEL={', 'const LABEL={nirvana:"Nirvana",')
                .replace('const NOTES={', 'const NOTES={nirvana:"Nirvana and Kurt Cobain shirts that claim the 90s (a 1989–1999 date, 90s, single stitch, an old tag, or vintage with no later date), tagged or no tag. Anything dated 2000 or later, Y2K, reprints and print shops are left out. eBay searched: vintage nirvana, kurt cobain, 1991, 1993, single stitch, in utero, giant tag, 90s, 1992, nevermind (whatever eBay let through). Poshmark searched the same terms. Mercari blocked every search today.",')
                .replace("__SINCE__", f"{wh.SINCE:%b %-d}").replace("__TODAY__", f"{wh.TODAY:%b %-d, %Y}")
                .replace("The band tab only shows", "Only shows"))
        (OUT / "nirvana_recent.html").write_text(page)
        print("->", OUT)
