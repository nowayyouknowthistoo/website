"""What to search for and how often. Edit freely, then restart."""

# Each band: the searches to run on every site. Misspellings and vague titles are where the
# underpriced listings hide, so they're included on purpose.
SEARCHES = {
    "Nirvana": [
        "vintage nirvana", "nirvana single stitch", "nirvana bootleg", "90s nirvana", "nirvana giant tag",
        "nirvana brockum", "nirvana 1992", "nirvana 1993", "nirvana sliver", "nirvana incesticide",
        "nirvana in utero vintage", "nirvana nevermind vintage", "nirvana long sleeve vintage",
        "kurt cobain vintage", "kurt cobain 1994", "kurt cobain memorial",
        "nirvanna", "nervana shirt", "kurt kobain", "curt cobain", "nirvana insecticide",
    ],
    "Red Hot Chili Peppers": [
        "vintage red hot chili peppers", "red hot chili peppers single stitch", "90s red hot chili peppers",
        "rhcp vintage", "rhcp single stitch", "red hot chili peppers 1991", "red hot chili peppers 1992",
        "blood sugar sex magik shirt", "red hot chili peppers giant", "red hot chili peppers bootleg",
        "red hot chilli peppers", "red hot chilli peppers vintage", "chili peppers vintage shirt",
        "lollapalooza 1992 shirt",
    ],
}

SITES = ["depop", "ebay", "poshmark", "vinted"]

POLL_MINUTES = 5          # how often each search is re-run
REQUEST_GAP_SECONDS = 2   # pause between requests so sites don't block you
PORT = 8765
DB_PATH = "data/vintage_finder.sqlite"
