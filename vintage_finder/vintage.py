"""Decide whether a listing looks like a real 80s/90s shirt, and whether it's underpriced.

Works on whatever text a site gives us (title, brand, description). Every flag is shown on
the page, so you can see why something ranked high.
"""

import re

BANDS = {
    "Nirvana": r"nirvan+a|nervana|kurt|cobain|kobain|nevermind|in utero|incesticide|insecticide|sliver|"
               r"bleach|vestibule|unplugged",
    "Red Hot Chili Peppers": r"chil+i\s*pepper|rhcp|red hot|blood sugar|magik|one hot minute|mother'?s milk|"
                             r"lollapalooza",
}
NOT_THE_BAND = r"manic nirvana|robert plant|hot stuff|kurt adler|kurt s\.? adler|philly peppers|radiohead"
NOT_A_SHIRT = (r"\b(cd|vinyl|lp|cassette|poster|keychain|patch|magazine|sticker|pin|mug|signed|"
               r"framed|cardigan|sweater|knit|corset|skirt|ornament|lighter|flag|tapestry|book)\b")

# Clearly modern: say so, or come from current mall / licensed lines.
MODERN = (r"\breprint|re-print|reproduction|repro\b|modern|vintage[- ]style|vintage inspired|"
          r"retro style|brand new|nwt|new with tags|y2k|2000s|2010s|"
          r"bravado|hot topic|h&m|\bdivided\b|urban outfitters|pacsun|forever 21|american eagle|"
          r"abercrombie|spencer'?s|cotton on|old navy|zara|shein|gildan|comfort colors|"
          r"rock off|amplified|cropped|baby tee|upcycled|reworked|custom")

OLD_TAGS = r"\bgiant\b|brockum|screen stars|oneita|tultex|winterland|tee jays|\bm&o\b|signal sport|stanley desantis"
PERIOD_BLANKS = r"fruit of the loom|\bfotl\b|\bhanes\b|\banvil\b|jerzees"
TELLS = [
    ("single stitch", r"single[- ]?stitch|single stich", 3),
    ("80s/90s date", r"\b19[89]\d\b|\b'?9[0-9]\b|\b(80|90)'?s\b|early 90", 3),
    ("old tag", OLD_TAGS, 3),
    ("period blank", PERIOD_BLANKS, 1),
    ("made in USA", r"made in (the )?usa|\busa made", 2),
    ("bootleg", r"bootleg|\bboot\b|parking lot|lot tee", 2),
    ("no tag", r"no tag|tagless|cut tag|tag (cut|ripped|removed|missing)|missing tag", 1),
    ("original owner", r"original owner|og owner|bought at|purchased at", 2),
    ("faded / thrashed", r"faded|thrashed|distressed|sun fade", 1),
    ("says vintage", r"vintage|\bvtg\b|true vintage", 1),
]
MISSPELL = r"nirvanna|nervana|kobain|curt cobain|cobian|insecticide|chilli|chilly pepper|red hot chilly"


def band_of(text: str) -> str | None:
    if re.search(NOT_THE_BAND, text):
        return None
    for band, pat in BANDS.items():
        if re.search(pat, text):
            return band
    return None


def analyse(title: str, brand: str = "", desc: str = "", price: float | None = None) -> dict:
    text = f"{title} {brand} {desc}".lower()
    flags, score = [], 0
    for label, pat, pts in TELLS:
        if re.search(pat, text):
            flags.append(label)
            score += pts
    # A 2000s+ year in the title means a modern shirt; in a description it's often just a story.
    modern = bool(re.search(MODERN, text) or re.search(r"\b20[0-2]\d\b", title.lower()))
    if modern:
        flags.append("modern / reprint")
    if re.search(MISSPELL, text):
        flags.append("misspelled title")
    # Dates like "Live 93" or "In Utero 1993" are printed on modern merch too, so a deal also needs
    # something physical about the shirt itself.
    physical = {"single stitch", "old tag", "made in USA", "bootleg", "no tag", "original owner"} & set(flags)
    deal = (not modern and price is not None and bool(physical) and
            ((score >= 7 and price <= 120) or (score >= 5 and price <= 60) or (score >= 3 and price <= 25)))
    if deal:
        flags.append("underpriced")
    return {
        "band": band_of(text),
        "shirt": not re.search(NOT_A_SHIRT, text),
        "score": score,
        "modern": modern,
        "flags": flags,
        "tag": "old tag" if "old tag" in flags else ("no tag" if "no tag" in flags else ""),
    }
