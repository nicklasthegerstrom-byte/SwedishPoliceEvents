from __future__ import annotations
from polisprojekt.services.notify import notify_discord, notify_slack
from polisprojekt.data.api_fetch import fetch_events
from polisprojekt.model.event_model import Event
from polisprojekt.services.database import EventDB

from polisprojekt.services.sorting import get_serious_events
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


def run_once_slack(db: EventDB, webhook: str, min_score: int = 6) -> dict[str, int]:
  
    api_data = fetch_events()
    if not api_data:
        logger.warning("API levererade ingen data.")
        return {"fetched": 0, "inserted": 0, "serious": 0, "sent": 0}

    events = [Event.from_api(item) for item in api_data]

    inserted = 0
    for e in events:
        if db.save_event(e):
            inserted += 1

    serious = get_serious_events(events, min_score=min_score)
    serious = sorted(serious, key=lambda e: e.time or datetime.min)

    # --- Bootstrap-skydd (anti-spam vid första sync) ---
    BOOTSTRAP_INSERTED_THRESHOLD = 100  # justera vid behov

    if inserted >= BOOTSTRAP_INSERTED_THRESHOLD:
        logger.info(
            "Bootstrap-läge: %s nya events. Skickar inga notiser, markerar serious som notifierade.",
            inserted,
        )
        for e in serious:
            if e.event_id is not None:
                db.mark_notified(e.event_id)

        return {
            "fetched": len(events),
            "inserted": inserted,
            "serious": len(serious),
            "sent": 0,
        }
    # -----------------------------------------------

    sent = notify_slack(
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