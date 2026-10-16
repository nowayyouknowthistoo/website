"""Match listings from many sources against a set of reference photos.

Each reference design is described by keyword patterns taken from what is
visible in the photo (graphic, wording, sleeve prints). A listing is tagged
with the design it matches, plus flags for reprints and modern merch.
"""

import re

# The 12 photos the user sent (Oct 2026), all 90s-style Nirvana long sleeves
# with sleeve prints.
DESIGNS = {
    "pagan-cross": ("Pagan Cross (Celtic cross)", r"pagan|celtic cross|\bcross\b"),
    "1987-1994": ("1987-1994 band photos (Black Sheep)", r"1987.?1994|87.?94|black sheep"),
    "knot": ("Blue knot / Nevermind sleeves", r"\bknot|torus|trinity"),
    "wavy-nevermind": ("Nevermind wavy logo long sleeve (black / tie-dye)",
                       r"nevermind.*(euro|europe|wavy|boot|sleeve print|sleeve hit)|"
                       r"(euro|europe|wavy).*nevermind"),
    "why": ("'Why' collage, Kurt Cobain 1994", r"\bwhy\b|i hate myself|hate myself|1967.?1994"),
    "in-utero-boot": ("1993 bootleg In Utero circle", r"in utero.*(boot|parking|1993)|(boot|parking).*in utero"),
    "smiley-sleeves": ("Smiley with smiley sleeve prints", r"smiley.*(sleeve|long ?sleeve|ls)|kustom kit"),
    "roskilde": ("1992 Roskilde", r"roskilde"),
    "spiral": ("Nevermind spiral", r"spiral|vertigo|swirl|hypno"),
    "unplugged": ("MTV Unplugged in New York", r"unplugged"),
    "vestibule-euro": ("Vestibule x Nevermind European boot", r"vestibule|fudge pack|circles? of hell|dante"),
}

LONG_SLEEVE = r"long ?sleeve|longsleeve|long-sleeve|\bl/?s\b|\bls\b|longsleeved"
REPRINT = r"reprint|re-?print|repro|reproduction|vintage[- ]style|vtg style|retro reissue|reissue|modern"
MODERN_BRANDS = (r"old navy|zara|h&m|\bdivided\b|urban outfitters|hot topic|daydreamer|gildan|"
                 r"comfort colors|aeropostale|amplified|rowdy sprout|bravado|5mv")
SOLD = r"\bsold\b|sold price|no longer available"


def classify(title: str, snippet: str = "") -> dict:
    text = f"{title} {snippet}".lower()
    design = next((k for k, (_, p) in DESIGNS.items() if re.search(p, text)), None)
    return {
        "design": design,
        "design_name": DESIGNS[design][0] if design else "",
        "long_sleeve": bool(re.search(LONG_SLEEVE, text)),
        "reprint": bool(re.search(REPRINT, text)),
        "modern_brand": bool(re.search(MODERN_BRANDS, text)),
        "sold": bool(re.search(SOLD, text)),
    }
