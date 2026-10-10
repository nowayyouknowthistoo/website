"""The sourcing "formula": what counts as a match for the shop.

Niche: vintage pop culture / music / bands / sports / cartoons.
Item types: t-shirts, crewneck sweatshirts, snapback hats only.

Every listing gets a score. A listing is a match only if it is one of the
three item types AND hits at least one niche theme AND clears no hard
dealbreaker. The score then ranks matches by how likely they are to be
true vintage worth flipping. Edit the keyword lists below to tune it.
"""

import re
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Item types (must hit one)
# --------------------------------------------------------------------------
ITEM_TYPES = {
    "snapback": [r"snap ?back", r"\bhat\b", r"\bcap\b", r"trucker"],
    "crewneck": [r"crew ?neck", r"sweat ?shirt", r"\bpullover\b", r"\bfleece\b"],
    "tee": [r"t-?shirt", r"\btee\b", r"\btees\b", r"\bshirt\b", r"\btshirt\b"],
}

# Things that are clothing but not what we buy.
WRONG_ITEM = [
    r"hoodie", r"hooded", r"jacket", r"windbreaker", r"\bjersey\b", r"\bpolo\b",
    r"button[- ]?(down|up)", r"\btank\b", r"muscle tee", r"\bdress\b", r"crop ?top",
    r"\bcropped\b", r"baby ?tee", r"\bbeanie\b", r"fitted hat", r"flex ?fit", r"bucket hat",
    r"\bshorts\b", r"\bpants\b", r"\bsocks?\b", r"poster", r"\bvinyl record\b", r"\bpatch\b",
    r"\bpin\b", r"\bmug\b", r"\bkeychain\b", r"\blanyard\b", r"golf club", r"fairway wood",
    r"\bonesie\b", r"\bbib\b",
]

# --------------------------------------------------------------------------
# Niche themes (must hit at least one)
# --------------------------------------------------------------------------
THEMES = {
    "music": [
        r"\bband\b", r"concert", r"\brock\b", r"metal", r"\bpunk\b", r"grunge",
        r"hip ?hop", r"\brap\b", r"\br&b\b", r"country music", r"reggae", r"\bemo\b", r"boy ?band",
        r"lollapalooza", r"woodstock", r"ozzfest", r"warped tour",
        # big-name artists that resell well
        r"metallica", r"nirvana", r"pink floyd", r"led zep", r"grateful dead", r"rolling stones",
        r"ac/?dc", r"iron maiden", r"guns ?n'? ?roses", r"pearl jam", r"slayer", r"megadeth",
        r"black sabbath", r"ozzy", r"misfits", r"ramones", r"the cure", r"depeche mode",
        r"smiths", r"tupac|2pac", r"biggie|notorious b\.?i\.?g", r"wu[- ]tang", r"eazy[- ]?e",
        r"\bn\.?w\.?a\b", r"snoop", r"dr\.? ?dre", r"ice cube", r"outkast", r"public enemy",
        r"run[- ]?dmc", r"beastie boys", r"cypress hill", r"bone thugs", r"aaliyah", r"\btlc\b",
        r"michael jackson", r"prince\b", r"madonna", r"elvis", r"beatles", r"bob marley",
        r"hendrix", r"the doors", r"the who\b", r"kiss\b", r"aerosmith", r"def leppard",
        r"bon jovi", r"motley crue", r"poison\b", r"van halen", r"queen\b", r"u2\b",
        r"springsteen", r"phish", r"dave matthews", r"radiohead", r"smashing pumpkins",
        r"soundgarden", r"alice in chains", r"stone temple", r"red hot chili", r"rhcp",
        r"green day", r"blink[- ]?182", r"sublime", r"korn", r"slipknot", r"tool\b",
        r"rage against", r"deftones", r"marilyn manson", r"nine inch nails", r"\bnin\b",
        r"white zombie", r"pantera", r"sepultura", r"type o negative", r"danzig", r"the cult",
        r"no doubt", r"spice girls", r"backstreet", r"nsync|\*nsync", r"britney", r"selena",
        r"garth brooks", r"johnny cash", r"willie nelson", r"dolly parton", r"reba",
        r"jimmy buffett", r"eagles\b", r"fleetwood", r"lynyrd", r"zz top", r"bob dylan",
        r"insane clown|\bicp\b", r"juggalo", r"my chemical romance", r"fall out boy",
        r"linkin park", r"limp bizkit", r"system of a down", r"weezer", r"oasis\b", r"blur\b",
        r"bjork", r"sonic youth", r"pixies", r"fugazi", r"black flag", r"bad religion",
        r"descendents", r"rancid", r"nofx", r"\bbrockum\b", r"winterland", r"giant tag",
        r"rock ?t'?s",
    ],
    "pop culture": [
        r"movie", r"\bfilm\b", r"promo", r"\btv\b", r"television", r"sitcom", r"star wars",
        r"star trek", r"jurassic", r"ghostbusters", r"back to the future", r"terminator",
        r"\bet\b|e\.t\.", r"jaws", r"rocky\b", r"pulp fiction", r"scarface", r"friends\b",
        r"seinfeld", r"x[- ]?files", r"twin peaks", r"harry potter", r"matrix", r"horror",
        r"freddy|nightmare on elm", r"friday the 13th", r"halloween", r"chucky", r"scream\b",
        r"marvel", r"\bdc comics?\b", r"batman", r"superman", r"spider[- ]?man", r"x[- ]?men",
        r"comic", r"video game", r"nintendo", r"sega", r"playstation", r"atari", r"pokemon",
        r"mario", r"zelda", r"street fighter", r"mortal kombat", r"wwf|wwe|wcw|nwo",
        r"wrestl", r"hulk hogan", r"stone cold", r"the rock\b", r"undertaker",
        r"hard rock cafe", r"harley", r"budweiser", r"camel\b", r"marlboro", r"\bnasa\b",
        r"anime", r"dragon ?ball", r"akira", r"sailor moon", r"evangelion", r"\bmtv\b",
        r"\bbeavis", r"south park", r"simpsons", r"family guy", r"futurama", r"king of the hill",
        r"parody", r"bootleg", r"rap tee",
    ],
    "cartoons": [
        r"cartoon", r"looney tunes", r"warner bros", r"bugs bunny", r"taz\b|tasmanian",
        r"tweety", r"daffy", r"road ?runner", r"wile e", r"marvin the martian", r"disney",
        r"mickey", r"minnie", r"goofy", r"donald duck", r"winnie|pooh", r"lion king",
        r"aladdin", r"little mermaid", r"snoopy", r"peanuts", r"charlie brown", r"garfield",
        r"hanna[- ]barbera", r"scooby", r"flintstones", r"jetsons", r"yogi", r"popeye",
        r"betty boop", r"tom (and|&) jerry", r"rugrats", r"nickelodeon", r"\bnick\b",
        r"cartoon network", r"powerpuff", r"dexter", r"ren (and|&) stimpy", r"hey arnold",
        r"spongebob", r"tmnt|ninja turtles", r"care bears", r"smurfs", r"casper",
        r"pink panther", r"felix the cat", r"muppets", r"sesame street", r"calvin (and|&) hobbes",
        r"space jam", r"tiny toons", r"animaniacs", r"pinky (and|&) the brain",
    ],
    "sports": [
        r"\bnfl\b", r"\bnba\b", r"\bmlb\b", r"\bnhl\b", r"ncaa", r"nascar", r"winston cup",
        r"starter\b", r"logo ?7", r"logo athletic", r"salem sportswear", r"nutmeg", r"chalk ?line",
        r"competitor", r"apex one", r"\bsignal sports", r"trench", r"pro player", r"sports specialties",
        r"\bajd\b", r"american needle", r"twins enterprise", r"drew pearson", r"\blee sport\b",
        r"world series", r"super ?bowl", r"champions\b|championship", r"final four", r"stanley cup",
        r"jordan\b", r"bulls\b", r"lakers", r"celtics", r"knicks", r"hornets", r"magic\b",
        r"raiders", r"49ers", r"cowboys", r"steelers", r"packers", r"bears\b", r"dolphins",
        r"chiefs", r"broncos", r"eagles\b", r"giants\b", r"patriots", r"bills\b", r"vikings",
        r"yankees", r"dodgers", r"braves", r"red sox", r"cubs\b", r"mariners", r"white sox",
        r"blue jays", r"marlins", r"rockies", r"devils\b", r"mighty ducks", r"sharks\b",
        r"penguins", r"red wings", r"bruins", r"maple leafs", r"blackhawks",
        r"earnhardt", r"jeff gordon", r"dale jr", r"tiger woods", r"michael jordan", r"shaq",
        r"olympic", r"dream team", r"basketball", r"football", r"baseball", r"hockey", r"racing",
        r"boxing", r"tyson", r"\bufc\b",
    ],
}

# --------------------------------------------------------------------------
# Vintage signals (raise the score)
# --------------------------------------------------------------------------
VINTAGE_SIGNALS = [
    (r"single[- ]?stitch", 3),
    (r"made in (the )?usa|usa made|\busa\b", 2),
    (r"\b(19)?[789]0'?s\b|\b[789]0s\b", 2),
    (r"\bvintage\b|\bvtg\b|\bvntg\b", 1),
    (r"\by2k\b", 1),
    (r"screen stars", 2), (r"hanes beefy|beefy[- ]t", 1), (r"\bstedman\b", 2),
    (r"\bbrockum\b", 3), (r"\bgiant\b", 2), (r"winterland", 2), (r"tultex", 2),
    (r"\bsignal\b", 1), (r"\bchanges\b", 1), (r"liquid blue", 1), (r"tennessee river", 1),
    (r"oneita", 2), (r"sportswear", 1), (r"\bdelta\b", 1), (r"\banvil\b", 1),
    (r"\bfotl\b|fruit of the loom", 1), (r"\bbelton\b", 1), (r"jerzees", 1),
    (r"\bstarter\b", 2), (r"logo ?7|logo athletic", 2), (r"salem", 2), (r"nutmeg", 2),
    (r"chalk ?line", 2), (r"\bajd\b|drew pearson|american needle|sports specialties", 2),
    (r"\bnos\b|deadstock|nwot|nwt\b", 1), (r"double[- ]sided|front (and|&) back", 1),
    (r"puff print", 1), (r"bootleg|rap tee", 1), (r"rare\b", 0),
]

# Words that hint at music but are too generic on their own ("bicycle tour",
# "science festival"). They add a point only alongside a real theme hit.
WEAK_MUSIC = r"\btour\b|festival|album|\bmusic\b"

# Score cut-offs: below MIN_SCORE is dropped; STRONG and up is a strong lead.
MIN_SCORE = 6
STRONG = 9

# A year in the title. Pre-2006 is good, a recent year is a modern-merch tell.
YEAR = re.compile(r"(?<!\d)(19[6-9]\d|20[0-2]\d)(?!\d)")
VINTAGE_YEAR_MAX = 2005

# --------------------------------------------------------------------------
# Red flags (lower the score) and dealbreakers (drop the listing)
# --------------------------------------------------------------------------
RED_FLAGS = [
    (r"vintage[- ]style|vintage[- ]inspired|retro[- ]style|vintage look|retro look", -4),
    (r"\breprint\b|\brepro\b|reproduction|re-?issue", -4),
    (r"bootleg[- ]style|rap tee style|y2k style|90s style", -3),
    (r"\bgildan\b|softstyle|bella ?\+? ?canvas|next level", -2),
    (r"hot topic|urban outfitters|\bh&m\b|forever 21|target|walmart|primark|spencer", -3),
    (r"\bamplified\b|rock ?off|merch traffic|junk food|\bfifth sun\b|ripple junction", -2),
    (r"\bwomens?\b|\bwomen'?s\b|\bladies\b|\bjuniors?\b|\bgirls?\b", -1),
    (r"long[- ]sleeve|\bls\b", -1),
    (r"stain|hole|thrashed|distressed|damaged|flaw", -1),
    (r"oversized", -1),
]

DEALBREAKERS = [
    r"\btoddler\b", r"\binfant\b", r"\byouth\b", r"\bkids?\b", r"\bbaby\b", r"\b\d+t\b",
    r"\b\d+-\d+m\b", r"\b\d+m\b", r"\bcustom\b", r"\bdiy\b",
]

# Kid sizes as reported by the site's size field.
KID_SIZE = re.compile(r"^\s*(\d{1,2}T(/\d+)?|\d+-\d+M|\d+M|NB|\d+|\d+/\d+)\s*$", re.I)


@dataclass
class Verdict:
    match: bool
    score: int
    item_type: str | None
    themes: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def _hit(patterns, text):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(0)
    return None


def evaluate(title: str, brand: str = "", size: str = "", price: float | None = None) -> Verdict:
    text = f"{title} {brand}".lower()
    reasons = []

    if size and KID_SIZE.match(size) and not re.match(r"^\s*(os|osfa)\s*$", size, re.I):
        return Verdict(False, 0, None, reasons=[f"kid/numeric size {size}"])
    bad = _hit(DEALBREAKERS, text)
    if bad:
        return Verdict(False, 0, None, reasons=[f"dealbreaker: {bad}"])
    wrong = _hit(WRONG_ITEM, text)
    if wrong:
        return Verdict(False, 0, None, reasons=[f"wrong item: {wrong}"])

    item_type = next((t for t, pats in ITEM_TYPES.items() if _hit(pats, text)), None)
    if item_type is None:
        return Verdict(False, 0, None, reasons=["not a tee/crewneck/snapback"])

    themes = []
    for name, pats in THEMES.items():
        h = _hit(pats, text)
        if h:
            themes.append(name)
            reasons.append(f"{name}: {h}")
    weak = re.search(WEAK_MUSIC, text)
    if not themes and weak and re.search(r"single[- ]?stitch|\b(19[6-9]\d|200[0-5])\b", text):
        # An old "tour" tee from an act not in our list is still usually a concert tee.
        themes.append("music")
        reasons.append(f"music?: old + {weak.group(0)}")
        weak = None
    if not themes:
        return Verdict(False, 0, item_type, reasons=["no niche theme"])

    score = 2 + len(themes)
    if weak:
        score += 1
        reasons.append(f"+1 {weak.group(0)}")
    for pat, pts in VINTAGE_SIGNALS:
        m = re.search(pat, text, re.I)
        if m and pts:
            score += pts
            reasons.append(f"+{pts} {m.group(0)}")
    for pat, pts in RED_FLAGS:
        m = re.search(pat, text, re.I)
        if m:
            score += pts
            reasons.append(f"{pts} {m.group(0)}")

    years = [int(y) for y in YEAR.findall(text)]
    if years:
        y = min(years)
        if y <= VINTAGE_YEAR_MAX:
            score += 3
            reasons.append(f"+3 dated {y}")
        else:
            score -= 3
            reasons.append(f"-3 modern year {y}")

    return Verdict(score >= MIN_SCORE, score, item_type, themes, reasons)


def tier(score: int) -> str:
    return "strong" if score >= STRONG else "possible"
