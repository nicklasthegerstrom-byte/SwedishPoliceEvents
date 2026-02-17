from __future__ import annotations
from polisprojekt.services.notify import send_to_slack, send_to_discord
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

def notify_slack(
    db: EventDB,
    events: list[Event],
    webhook_url: str,
    min_score: int = 7,
) -> int:
    """
    Skickar Slack-notiser för events som:
    - har seriousness >= min_score
    - inte redan är notifierade
    Markerar som notifierade först EFTER lyckad Slack-post.
    Returnerar antal skickade.
    """
    sent_count = 0

    for e in events:
        if e.event_id is None:
            continue

        if e.seriousness < min_score:
            continue

        if db.is_notified(e.event_id):
            continue

        ok = send_to_slack(webhook_url, e.to_slack())

        if ok:
            db.mark_notified(e.event_id)
            sent_count += 1

    return sent_count

def notify_discord(
    db: EventDB,
    events: list[Event],
    webhook_url: str,
    min_score: int = 7,
) -> int:
    """
    Samma logik som notify_slack, men skickar till Discord.
    """
    sent_count = 0

    for e in events:
        if e.event_id is None:
            continue

        if e.seriousness < min_score:
            continue

        if db.is_notified(e.event_id):
            continue

        ok = send_to_discord(webhook_url, e.to_slack())

        if ok:
            db.mark_notified(e.event_id)
            sent_count += 1

    return sent_count


def run_once_discord(db: EventDB, webhook: str, min_score: int = 7) -> dict[str, int]:
    """
    1) Hämtar events från API
    2) Sparar alla i DB (historik)
    3) Filtrerar ut "serious"
    4) Skickar till Discord endast om eventet INTE notifierats tidigare
    5) Markerar som notifierat först efter lyckad post

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
    
    serious = sorted(
    serious,
    key=lambda e: e.time or datetime.min
)

    sent = 0
    for e in serious:
        if e.event_id is None:
            continue

        if db.is_notified(e.event_id):
            continue

        ok = send_to_discord(webhook, e.to_slack())
        if ok:
            db.mark_notified(e.event_id)
            sent += 1

    return {
        "fetched": len(events),
        "inserted": inserted,
        "serious": len(serious),
        "sent": sent,
    }