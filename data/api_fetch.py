import time
from typing import Any

import requests

DEFAULT_URL = "https://polisen.se/api/events"
DEFAULT_HEADERS = {"User-Agent": "PolisEventsBot/1.0"}


def fetch_events(
    url: str = DEFAULT_URL,
    *,
    timeout: float = 10.0,
    retries: int = 3,
    backoff_seconds: float = 2.0,
) -> list[dict[str, Any]] | None:
    """
    Fetch events from the Swedish Police API.

    Returns:
        Non-empty list of events on success.
        None on any kind of failure or unexpected data.
    """

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                headers=DEFAULT_HEADERS,
                timeout=timeout,
            )
            response.raise_for_status()

            data = response.json()

            # Strikt validering
            if not isinstance(data, list):
                return None

            if not data:  # tom lista = ogiltigt i din domän
                return None

            return data

        except (requests.exceptions.RequestException, ValueError):
            if attempt < retries:
                time.sleep(backoff_seconds * attempt)
            else:
                return None
            



def print_events():

    events = fetch_events()
    if events is None:
    # handle failure
        return
    print(events[0])

print_events()

