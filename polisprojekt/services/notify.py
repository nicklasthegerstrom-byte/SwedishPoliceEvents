
import requests
from polisprojekt.model.event_model import Event
from polisprojekt.services.database import EventDB

#Notify används inte just nu pga görs direkt i pipeline
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

def send_to_slack(webhook_url: str, text: str, timeout: int = 10) -> bool:
    """
    Skickar text till Slack via incoming webhook.
    Returnerar True om Slack svarar OK, annars False.
    """
    try:
        response = requests.post(
            webhook_url,
            json={"text": text},
            timeout=timeout,
        )

        response.raise_for_status()

        # Slack brukar returnera "ok"
        return response.text.strip().lower() == "ok"

    except requests.RequestException as e:
        print(f"Slack error: {e}")
        return False

def send_to_discord(webhook_url: str, text: str, timeout: int = 10) -> bool:
    """
    Skickar text till Discord via webhook.
    Returnerar True om Discord svarar OK (2xx), annars False.
    """
    try:
        resp = requests.post(
            webhook_url,
            json={"content": text},
            timeout=timeout,
        )
        resp.raise_for_status()
        return True
    except requests.RequestException:
        return False