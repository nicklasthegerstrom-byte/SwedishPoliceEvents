# notify.py
import threading
import time
from datetime import datetime
from main import load_events  # Make sure this path is correct

# Keep track of events we've already seen
seen_event_ids = set()

def check_new_events():
    """
    Runs in a separate thread and checks for new serious events every 60 seconds.
    """
    global seen_event_ids
    events = load_events()
    seen_event_ids = {e.id for e in events if e.seriousness >= 7}

    def loop():
        global seen_event_ids
        while True:
              # Load all events from your main logic
            events = load_events()
            new_events = []
            for e in events:
                # Only consider seriousness >= 7
                if getattr(e, "id", None) not in seen_event_ids and getattr(e, "seriousness", 0) >= 7:
                    new_events.append(e)
                    seen_event_ids.add(e.id)

            # Notify about new events
            for e in new_events:
                print(f"🚨 New serious event detected! {e.type} at {e.location_name} ({e.seriousness})")

            print(f"{datetime.now()}: Checked events. {len(new_events)} new serious events.")
            time.sleep(60)  # Wait 60 seconds before checking again

    # Start the loop in a daemon thread
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    print("Notifier started...")
    check_new_events()

    # Keep the main thread alive so the daemon keeps running
    while True:
        time.sleep(1)

