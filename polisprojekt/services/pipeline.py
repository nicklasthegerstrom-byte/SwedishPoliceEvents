from __future__ import annotations

from polisprojekt.data.api_fetch import fetch_events
from polisprojekt.model.event_model import Event
from polisprojekt.services.database import EventDB


def load_events() -> list[Event]:
    api_data = fetch_events()
    if not api_data:
        return []
    return [Event.from_api(item) for item in api_data]


def save_events(db: EventDB, events: list[Event]) -> int:
    inserted = 0
    for e in events:
        if db.save_event(e):
            inserted += 1
    return inserted