from __future__ import annotations
from polisprojekt.services.notify import notify_slack, notify_slack_updates
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
        return {
            "fetched": 0,
            "inserted": 0,
            "updated": 0,
            "serious": 0,
            "updated_serious": 0,
            "sent": 0,
            "update_sent": 0,
        }

    events = [Event.from_api(item) for item in api_data]

    inserted = 0
    updated = 0
    new_events = []
    updated_events = []

    for e in events:
        status = db.save_event(e)

        if status == "inserted":
            inserted += 1
            new_events.append(e)

        elif status == "updated":
            updated += 1
            updated_events.append(e)

    new_serious = get_serious_events(new_events, min_score=min_score)
    updated_serious = get_serious_events(updated_events, min_score=min_score)

    # --- Bootstrap-skydd (anti-spam vid första sync) ---
    BOOTSTRAP_INSERTED_THRESHOLD = 100  # justera vid behov

    if inserted >= BOOTSTRAP_INSERTED_THRESHOLD:
        logger.info(
            "Bootstrap-läge: %s nya events. Skickar inga notiser, markerar serious som notifierade.",
            inserted,
        )
        for e in new_serious:
            if e.event_id is not None:
                db.mark_notified(e.event_id)

        return {
            "fetched": len(events),
            "inserted": inserted,
            "updated": updated,
            "serious": len(new_serious),
            "updated_serious": len(updated_serious),
            "sent": 0,
            "update_sent": 0,
        }
    # -----------------------------------------------

    # Skicka nya events (din befintliga funktion)
    sent = notify_slack(
        db=db,
        events=new_serious,
        webhook_url=webhook,
        min_score=min_score,
    )

    update_sent = 0
    logger.warning(
        "Update-notiser AVSTÄNGDA temporärt. updated=%s updated_serious=%s",
        updated,
        len(updated_serious),
    )

    return {
        "fetched": len(events),
        "inserted": inserted,
        "updated": updated,
        "serious": len(new_serious),
        "updated_serious": len(updated_serious),
        "sent": sent,
        "update_sent": update_sent,
    }