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

SITES = ["depop", "ebay", "poshmark", "vinted"]

POLL_MINUTES = 15         # how often each search is re-run (about 70 searches across 4 sites)
REQUEST_GAP_SECONDS = 2   # pause between requests so sites don't block you
PORT = 8765
DB_PATH = "data/vintage_finder.sqlite"
