import requests
import json

API_URL = "https://polisen.se/api/events"

TARGET_ID = 628746  # ändra vid behov


def fetch_events():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def find_event(events, event_id):
    for e in events:
        if e.get("id") == event_id:
            return e
    return None


def main():
    events = fetch_events()
    event = find_event(events, TARGET_ID)

    if event:
        print("EVENT FOUND:\n")
        print(json.dumps(event, indent=2, ensure_ascii=False))
    else:
        print(f"Event {TARGET_ID} hittades inte")


if __name__ == "__main__":
    main()