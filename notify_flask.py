# notify_flask.py (or inside app.py)

from datetime import datetime
from main import load_events
from data.scoring import user_seriousness  # make sure it’s imported

seen_event_ids = set()
first_run = True



def get_new_serious_events():
    events = load_events()
    global seen_event_ids, first_run
    if first_run:
        seen_event_ids.update({e.id for e in events})
        first_run = False
        return []

    new_events = []
    for e in events:
        e_type_score = user_seriousness.get(e.type, getattr(e, "seriousness", 0))
        if e.id not in seen_event_ids and e_type_score >= 7:  # or your min threshold
            new_events.append(e)
            seen_event_ids.add(e.id)
    return new_events

