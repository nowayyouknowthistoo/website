"""Search terms run on each site. Add or remove freely."""

QUERIES = {
    "poshmark": [
        "vintage band tee single stitch",
        "vintage concert tour tee 80s",
        "vintage rap tee",
        "vintage cartoon tee 90s",
        "vintage movie promo tee",
        "vintage looney tunes crewneck",
        "vintage band crewneck sweatshirt",
        "vintage nfl crewneck",
        "vintage nba tee 90s",
        "vintage nascar tee",
        "vintage snapback starter",
    ],
    "vinted": [
        "vintage band tee",
        "vintage single stitch tour tee",
        "vintage rap tee",
        "vintage cartoon tee",
        "vintage movie promo tee",
        "vintage band crewneck",
        "vintage nfl crewneck",
        "vintage nba tee",
        "vintage nascar tee",
        "vintage starter snapback",
    ],
}


# Searches for the focus bands (see FOCUS_BANDS in formula.py). Run with --focus.
FOCUS_QUERIES = {
    "poshmark": [
        "vintage nirvana shirt", "vintage nirvana sweatshirt", "nirvana single stitch",
        "vintage kurt cobain shirt",
        "vintage smashing pumpkins shirt", "smashing pumpkins sweatshirt",
        "vintage soundgarden shirt", "soundgarden sweatshirt",
        "vintage morrissey shirt", "morrissey sweatshirt",
        "butthole surfers shirt",
        "vintage cranberries shirt", "cranberries band tee",
        "vintage red hot chili peppers shirt", "red hot chili peppers sweatshirt",
    ],
    "vinted": [
        "vintage nirvana", "nirvana single stitch", "kurt cobain",
        "smashing pumpkins", "soundgarden", "morrissey", "butthole surfers",
        "cranberries band", "vintage red hot chili peppers", "red hot chili peppers crewneck",
    ],
}
