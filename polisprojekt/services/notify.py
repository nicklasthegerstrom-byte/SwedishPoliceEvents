
import requests
from polisprojekt.model.event_model import Event
from polisprojekt.services.database import EventDB

import logging
logger = logging.getLogger(__name__)

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
            logger.info(f"Notifierade event {e.event_id} ({e.type})")
            db.mark_notified(e.event_id)
            sent_count += 1
        else:
            logger.error(f"Misslyckades notifiera event {e.event_id} ({e.type})")

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

        ok = send_to_discord(webhook_url, e.to_discord())

        if ok:
            logger.info(f"Notifierade event {e.event_id} ({e.type})")
            db.mark_notified(e.event_id)
            sent_count += 1
        else:
            logger.error(f"Misslyckades notifiera event {e.event_id} ({e.type})")

    return sent_count

def send_to_slack(webhook_url: str, text: str, timeout: int = 10) -> bool:
    try:
        logger.info("Försöker skicka meddelande till Slack")

        response = requests.post(
            webhook_url,
            json={"text": text},
            timeout=timeout,
        )

        response.raise_for_status()

        ok = response.text.strip().lower() == "ok"

        if ok:
            logger.info("Slack-notis skickad OK")
        else:
            logger.error(f"Slack svarade oväntat: {response.text}")

        return ok

    except requests.RequestException as e:
        logger.error(f"Slack error: {e}")
        return False

def send_to_discord(webhook_url: str, text: str, timeout: int = 10) -> bool:
    try:
        logger.info("Försöker skicka meddelande till Discord")

        resp = requests.post(
            webhook_url,
            json={"content": text},
            timeout=timeout,
        )

        resp.raise_for_status()

        logger.info("Discord-notis skickad OK")
        return True

    except requests.RequestException as e:
        logger.error(f"Discord error: {e}")
        return False