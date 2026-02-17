from __future__ import annotations
from polisprojekt.services.notify import notify_discord
from polisprojekt.data.api_fetch import fetch_events
from polisprojekt.model.event_model import Event
from polisprojekt.services.database import EventDB

from polisprojekt.services.sorting import get_serious_events
from datetime import datetime

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


def run_once_discord(db: EventDB, webhook: str, min_score: int = 7) -> dict[str, int]:
    """
    1) Hämtar events från API
    2) Sparar alla i DB (historik)
    3) Filtrerar ut "serious"
    4) Skickar till Discord via notify_discord (dedupe + mark_notified ingår där)
    Returnerar enkel statistik.
    """
    api_data = fetch_events()
    if not api_data:
        return {"fetched": 0, "inserted": 0, "serious": 0, "sent": 0}

    events = [Event.from_api(item) for item in api_data]

    inserted = 0
    for e in events:
        if db.save_event(e):
            inserted += 1

    serious = get_serious_events(events, min_score=min_score)
    serious = sorted(serious, key=lambda e: e.time or datetime.min)

    sent = notify_discord(
        db=db,
        events=serious,
        webhook_url=webhook,
        min_score=min_score,
    )

    return {
        "fetched": len(events),
        "inserted": inserted,
        "serious": len(serious),
        "sent": sent,
    }