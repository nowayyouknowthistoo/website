"""Load the Depop listings already collected in data/depop/ so the page isn't empty on first run."""

import glob
import json
import re
from pathlib import Path

from .sources import depop


def import_saved(store):
    pages = {}
    if Path("data/depop/pages.json").exists():
        pages = json.load(open("data/depop/pages.json"))
    # Verdicts written by hand while checking listings: reprint / not the band / gone.
    skip = set()
    if Path("data/depop/notes.tsv").exists():
        for line in open("data/depop/notes.tsv").read().splitlines()[1:]:
            slug, verdict, note = (line.split("\t") + ["", ""])[:3]
            if verdict in ("reprint", "notband", "gone"):
                skip.add(slug)
    items = []
    for f in sorted(glob.glob("data/depop/d*.json")):
        for r in json.load(open(f))["results"]:
            for it in depop.parse(r.get("text") or ""):
                if it["id"] in skip:
                    continue
                detail = pages.get(it["url"], {})
                it["desc"] = detail.get("desc", "")
                if detail.get("price"):
                    it["price"] = float(re.sub(r"[^\d.]", "", detail["price"]) or 0) or it["price"]
                items.append(it)
    if items:
        store.save(items)
