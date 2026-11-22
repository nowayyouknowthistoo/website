"""What to search for and how often. Edit freely, then restart."""

# Each band: the searches to run on every site. Misspellings and vague titles are where the
# underpriced listings hide, so they're included on purpose.
SEARCHES = {
    "Nirvana": [
        "vintage nirvana", "nirvana single stitch", "nirvana bootleg", "90s nirvana", "nirvana giant tag",
        "nirvana brockum", "nirvana 1992", "nirvana 1993", "nirvana in utero vintage", "nirvana nevermind vintage",
        "kurt cobain vintage", "kurt cobain memorial", "nirvanna", "kurt kobain",
    ],
    "Red Hot Chili Peppers": [
        "vintage red hot chili peppers", "rhcp vintage", "red hot chili peppers single stitch", "red hot chilli peppers vintage",
    ],
    "Sade": ["vintage sade shirt", "sade tour shirt", "sade 1993", "sade love deluxe shirt"],
    "Sub Pop": [
        "vintage sub pop shirt", "sub pop loser shirt", "vintage mudhoney", "vintage l7 shirt", "screaming trees shirt",
        "tad band shirt", "babes in toyland shirt", "hazel sub pop", "dickless shirt", "sister double happiness",
        "afghan whigs vintage", "sebadoh shirt", "supersuckers vintage",
    ],
    "Smashing Pumpkins": ["vintage smashing pumpkins", "smashing pumpkins single stitch", "smashing pumpkins 1996"],
    "Soundgarden": ["vintage soundgarden", "soundgarden single stitch", "soundgarden 1994"],
    "Oasis": ["vintage oasis shirt", "oasis 1997 shirt", "oasis band tee 90s"],
    "Green Day": ["vintage green day", "green day dookie shirt", "green day 1994"],
    "Radiohead": ["vintage radiohead", "radiohead 1997", "radiohead ok computer shirt"],
    "Dinosaur Jr": ["vintage dinosaur jr", "dinosaur jr shirt"],
    "Butthole Surfers": ["vintage butthole surfers", "butthole surfers shirt"],
    "Stone Temple Pilots": ["vintage stone temple pilots", "stone temple pilots 1994"],
    "Nine Inch Nails": ["vintage nine inch nails", "nine inch nails 1994", "nin single stitch"],
    "The Cranberries": ["vintage cranberries shirt", "cranberries 1995 shirt"],
    "Siouxsie": ["vintage siouxsie shirt", "siouxsie and the banshees shirt"],
    "Wu-Tang": ["vintage wu tang shirt", "wu wear vintage"],
    "Rap tees": [
        "vintage tupac shirt", "tupac memorial shirt", "vintage 2pac shirt", "vintage biggie shirt", "vintage dr dre shirt",
        "vintage rap tee", "vintage snoop dogg shirt",
    ],
}

# Broad searches that catch any band, re-run about once a minute on every site so new listings show up fast.
# Shirts from bands not listed above are kept too (shown as "Other band").
FRESH = [
    "vintage band tee", "vintage band shirt", "single stitch band tee", "90s band t shirt",
    "vintage concert shirt", "vintage tour shirt", "vintage rap tee",
]

SITES = ["depop", "ebay", "poshmark", "vinted"]

# Each site runs in its own loop, one request every REQUEST_GAP_SECONDS. Searches are re-run on these timers:
WATCH_SECONDS = 45        # searches you add in the page's Watch box (top priority)
FRESH_SECONDS = 60        # the broad FRESH searches
BAND_SECONDS = 600        # the per-band SEARCHES above
REQUEST_GAP_SECONDS = 3   # pause between requests to the same site so it doesn't block you
WATCHES_PATH = "data/watches.json"
PORT = 8765
DB_PATH = "data/vintage_finder.sqlite"
