from __future__ import annotations
from typing import Iterable
from polisprojekt.model.event_model import Event
from datetime import datetime


def get_serious_events(
    events: Iterable[Event],
    min_score: int = 7,
) -> list[Event]:
    """
    Filtrerar fram events med seriousness >= min_score och sorterar dem
    (senaste först). Events utan parsebar tid ignoreras.
    """
    serious = [
    e for e in events
    if e.seriousness >= min_score
    ]
    serious.sort(key=lambda e: e.time or datetime.min, reverse=True)
    return serious