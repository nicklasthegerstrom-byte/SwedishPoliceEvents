from __future__ import annotations
from typing import Iterable
from polisprojekt.model.event_model import Event
from datetime import datetime





#För fjällräddning

BORING_MOUNTAIN_KEYWORDS = [
    "skidåkare",
    "skidåkning",
    "i skidbacke",
    "ramlat",
    "fallolycka",
    "benbrott",
    "armbrott",
    "axelskada",
    "vrickat",
    "stukat",
    "skadad",
    "förd till sjukhus",
    "förd till sjukvård",
]

SERIOUS_MOUNTAIN_KEYWORDS = [
    "lavin",
    "allvarligt skadad"
    "svårt skadad"
    "försvunnen",
    "saknad",
    "nedkyld",
    "hypotermi",
    "svårt väder",
    "hårt väder",
    "storm",
    "snöstorm",
    "mörker",
    "barn",
    "helikopter",
    "svårtillgänglig",
    "otillgänglig terräng",
    "fjällstation",
    "ingen kontakt",
    "kan inte ta sig",
    "fast"
    "död",
]

def is_serious_mountain(event) -> bool:
    if "fjällräddning" not in event.type.lower():
        return True

    text_parts = [
        event.name or "",
        event.summary or "",
    ]
    text = " ".join(text_parts).lower()

    serious_hits = [kw for kw in SERIOUS_MOUNTAIN_KEYWORDS if kw in text]
    boring_hits = [kw for kw in BORING_MOUNTAIN_KEYWORDS if kw in text]

    # Positiva signaler ska vinna
    if serious_hits:
        return True

    # Om det bara ser ut som vanlig skid-skada -> bort
    if boring_hits:
        return False

    # Oklar fjällräddning får hellre passera än försvinna
    return True

def get_serious_events(
    events: Iterable[Event],
    min_score: int = 7,
) -> list[Event]:
    """
    Filtrerar fram events med seriousness >= min_score och sorterar dem
    (senaste först).
    """
    serious = [
        e for e in events
        if e.seriousness >= min_score
        and is_serious_mountain(e)
    ]
    serious.sort(key=lambda e: e.time or datetime.min, reverse=True)
    return serious