import requests


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