"""Narrow hunts for one specific item, stricter than the general formula.

A target listing must match every pattern in `require`, none in `exclude`,
and is ranked by `tells` (signs it is genuinely early-90s). Run with
`--target <name>`.
"""

import re
from dataclasses import dataclass, field

from .formula import Verdict


@dataclass
class Target:
    name: str
    require: list[str]
    exclude: list[str]
    tells: list[tuple[str, int]]
    queries: dict[str, list[str]] = field(default_factory=dict)
    notes: str = ""
    min_score: int = 3  # needs at least one real vintage tell to count as a lead


TARGETS = {
    "nirvana-tiedye-ls": Target(
        name="Nirvana tie-dye long sleeve (Nevermind era)",
        require=[
            r"nirvana|kurt cobain|nevermind",
            r"tie[- ]?d[iy]e|tye[- ]?dye|dip[- ]?dye",
            r"long[- ]?sleeve|longsleeve|\bl/?s\b",
        ],
        exclude=[
            # Modern licensed or mall versions seen in search results (Oct 2026).
            r"old navy", r"\bzara\b", r"rowdy sprout", r"\bh&m\b", r"urban outfitters",
            r"hot topic", r"american eagle", r"forever 21", r"target\b", r"walmart",
            r"pull ?& ?bear", r"bershka", r"shein", r"\bprimark\b", r"boxlunch",
            r"smiley|smile face|happy face",          # licensed smiley reissues
            r"reprint|repro\b|reproduction|vintage[- ]style|retro",
            r"custom|reworked|upcycl|diy|hand[- ]?dyed by me",
            r"hoodie|sweatshirt|crewneck|crew neck|pullover|cropped|crop top|tank",
            r"toddler|youth|kids?\b|\d+t\b|months?\b",
            r"colortone|colourtone",                  # modern tie-dye blank
            r"sleeve graphic|sleeve print",           # current official merch layout
            r"purple (and|&) pink|pink (and|&) purple|yellow logo",  # the Old Navy colourway, often unbranded
            r"acid[- ]?wash",
        ],
        tells=[
            (r"\b(19)?9[0-4]\b|early 90s|90'?s|1990s", 3),
            (r"single[- ]?stitch", 3),
            (r"made in (the )?usa|\busa\b", 2),
            (r"fruit of the loom|\bfotl\b|\bhanes\b|screen stars|oneita|jerzees|"
             r"sportswear|\bdelta\b|\banvil\b|\bgiant\b|brockum|tee jays|signal", 2),
            (r"parking lot|bootleg|boot\b|lot tee|tour", 2),
            (r"nevermind", 2),
            (r"vintage|\bvtg\b", 1),
            (r"faded|thrashed|worn", 1),
        ],
        queries={
            "poshmark": [
                "nirvana tie dye long sleeve", "vintage nirvana nevermind tie dye",
                "nirvana tie dye longsleeve 90s",
            ],
            "vinted": [
                "nirvana tie dye long sleeve", "nirvana nevermind tie dye",
                "vintage nirvana tie dye",
            ],
        },
        notes=(
            "Real early-90s Nirvana tie-dye long sleeves are mostly unofficial 'parking lot' "
            "bootlegs on period blanks (Fruit of the Loom, Hanes, Screen Stars). Official 1992 "
            "Nevermind prints carry a copyright line on the front; the 2002 reprint has it on "
            "the back under the tracklist. Always check the tag, cuff/hem stitching and print "
            "in photos before buying."
        ),
    ),
}


def evaluate_target(t: Target, title: str, brand: str = "", size: str = "",
                    description: str = "") -> Verdict:
    text = f"{title} {brand} {description}".lower()
    for p in t.require:
        if not re.search(p, text):
            return Verdict(False, 0, None, reasons=[f"missing: {p}"])
    for p in t.exclude:
        m = re.search(p, text)
        if m:
            return Verdict(False, 0, None, reasons=[f"excluded: {m.group(0)}"])
    score, reasons = 0, []
    for p, pts in t.tells:
        m = re.search(p, text)
        if m:
            score += pts
            reasons.append(f"+{pts} {m.group(0)}")
    # Every listing that passes the filters is shown; tells only rank them.
    return Verdict(True, score, "long sleeve", ["music"], reasons, band="Nirvana")
