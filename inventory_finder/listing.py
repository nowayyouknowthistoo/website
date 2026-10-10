from dataclasses import dataclass, asdict


@dataclass
class Listing:
    site: str
    title: str
    price: float | None
    size: str
    url: str
    brand: str = ""
    condition: str = ""
    original_price: float | None = None
    query: str = ""

    def __post_init__(self):
        # Poshmark titles contain invisible left-to-right marks.
        self.title = " ".join(self.title.replace("\u200e", "").split())

    def as_dict(self):
        return asdict(self)


def parse_price(s: str) -> float | None:
    s = s.replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None
