from datetime import datetime, timedelta
from data.api_fetch import fetch_events
from model.event_model import Event
from functions.search import search_events, search_input


def load_events():
    api_data = fetch_events()
    events = [Event(item) for item in api_data]

    # 👇 Debug: show the raw datetime string from the API
    for e in events:
        print(e.datetime_str)
    return events

if __name__ == "__main__":
    load_events()

load_events()