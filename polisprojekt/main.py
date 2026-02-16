
# Hämta events och sortera
# ----------------------------

# ----------------------------
# Funktioner
# ----------------------------

# Hämta alla Polisens Events, via Event klassen:

def load_events():
    api_data = fetch_events()
    events = [Event(item) for item in api_data]
    return(events)
    
# printa ALLA senaste 500 events (används inte):

def show_all_events():
    events = load_events()
    for e in events:
        print(e)
        print("-" * 40)
            
 #printa bara de inom en vald seriousness

from datetime import datetime, timedelta

def get_serious_events(hours=None, min_score=7):
    """Return a filtered list of serious events that respects user settings."""
    events = load_events()

    def effective_score(e):
        return user_seriousness.get(e.type, e.seriousness)

    # Filter by seriousness level
    serious_events = [e for e in events if effective_score(e) >= min_score]

    # Filter by time window, if specified
    if hours is not None:
        cutoff = datetime.now() - timedelta(hours=hours)
        serious_events = [e for e in serious_events if e.time and e.time >= cutoff]

    return serious_events


def show_serious_events(hours=None, min_score=7):
    """Print events nicely in terminal (for manual checks)."""
    events = get_serious_events(hours, min_score)
    if not events:
        print("⚠️ Inga händelser hittades.")
        return

    for e in events:
        print(e)
        print("-" * 40)



def search_events_by_word(search_term, min_score=7):
    """Return serious events matching a word in summary or type."""
    events = load_events()
    search_term = search_term.lower()

    matched = [
        e for e in events
        if e.seriousness >= min_score
        and (
            search_term in e.summary.lower()
            or search_term in e.type.lower()
        )
    ]
    return matched


def search_events_by_location(location_name, min_score=7):
    """Return serious events matching location."""
    events = load_events()
    location_name = location_name.lower()

    matched = [
        e for e in events
        if e.seriousness >= min_score
        and location_name in e.location_name.lower()
    ]
    return matched

def show_search_by_word(search_term, min_score=7):
    matched = search_events_by_word(search_term, min_score)
    if not matched:
        print(f"🚫 Inga händelser hittades för sökningen '{search_term}'.")
        return
    for e in matched:
        print(e)
        print("-" * 40)


def show_search_by_location(location_name, min_score=7):
    matched = search_events_by_location(location_name, min_score)
    if not matched:
        print(f"🚫 Inga händelser hittades för platsen '{location_name}'.")
        return
    for e in matched:
        print(e)
        print("-" * 40)





        


# ----------------------------
# Input. Att göra :Gör en funktion i en loop så jag slipper köra filen om och om.
#                  Rullista för att söka efter de städer (location) som finns i events.
# ----------------------------

def meny():
    while True:
        print("\nVälj en tidsperiod att visa viktiga händelser från:")
        print("1 - Senaste 3 timmar")
        print("2 - Senaste 6 timmar")
        print("3 - Senaste 12 timmar")
        print("4 - Senaste 24 timmar")
        print("5 - Alla")
        print("6 - Sök efter händelse (ex mord, explosion)")
        print("7 - Sök efter plats")
        print("8 - Avsluta")
        val = input("Ange nummer: ")

        if val == "1":
            show_serious_events(3)
        elif val == "2":
            show_serious_events(6)
        elif val == "3":
            show_serious_events(12)
        elif val == "4":
            show_serious_events(24)
        elif val == "5":
            show_serious_events()
        elif val == "6":
            search_word = input("Skriv en händelse att söka efter: ")
            search_events(search_word)
        elif val == "7":
            search_events_by_location()
        elif val == "8":
            print("Programmet avslutas.")
            break
        else:
            print("Felaktig input.")
            continue  # back to menu

        # ----------------------------
        # Pause before showing menu again
        # ----------------------------
        while True:
            again = input("\nVisa fler händelser / Ny fråga? (J/N): ").strip().lower()
            if again == "j":
                break  # goes back to menu
            elif again == "n":
                print("Programmet avslutas.")
                return
            else:
                print("Skriv J för Ja eller N för Nej.")

#NY VERSION AV MAIN HÄR:

from polisprojekt.data.api_fetch import fetch_events
from polisprojekt.model.event_model import Event
from polisprojekt.services.database import EventDB


def run_once():
    db = EventDB()

    api_data = fetch_events()
    if not api_data:
        print("No data from API.")
        return

    events: list[Event] = []
    inserted = 0

    for item in api_data:
        e = Event.from_api(item)
        events.append(e)

        if db.save_event(e):
            inserted += 1

    # plocka bara de som har en tid
    timed_events = [e for e in events if e.time is not None]

    latest_event = max(timed_events, key=lambda e: e.time) if timed_events else None

    total = len(events)

    print(f"Fetched: {total}")
    print(f"Inserted new: {inserted}")
    print(f"Already existed: {total - inserted}")

    if latest_event:
        print("\nLatest event (from API):")
        print(latest_event)
    else:
        print("\nLatest event: kunde inte parsea någon tid.")


if __name__ == "__main__":
    run_once()