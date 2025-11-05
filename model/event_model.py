from datetime import datetime
from data.scoring import SERIOUSNESS
import re
from data.scoring import user_seriousness  # live user adjustments

class Event:
    def __init__(self, data):
        self.id = data.get("id")
        self.datetime_str = data.get("datetime")
        self.type = data.get("type", "Okänd typ")
        self.summary = data.get("summary", "Ingen beskrivning")
        self.location = data.get("location", {})
        self.url = data.get("url")

       
    @property
    def time(self):
        """Return a parsed datetime object, fixing single-digit hours and ignoring timezone."""
        if not self.datetime_str:
            return None

        try:
            # Remove timezone if present (e.g., '+02:00')
            dt_str = self.datetime_str.split(" ")[0] + " " + self.datetime_str.split(" ")[1]

            # Fix single-digit hours: add leading zero if needed
            # Matches patterns like "9:08:15" and turns into "09:08:15"
            dt_str = re.sub(r"^(\d{4}-\d{2}-\d{2}) (\d):", r"\1 0\2:", dt_str)

            return datetime.fromisoformat(dt_str)
        except Exception:
            print(f"⚠️ Could not parse datetime: {self.datetime_str}")
            return None




    @property
    def location_name(self):
        return self.location.get("name", "Okänd plats")

    @property
    def seriousness(self):
        return SERIOUSNESS.get(self.type.strip(), 0) if self.type else 0
    
    @property
    def effective_seriousness(self):
        
        return user_seriousness.get(self.type.strip(), self.seriousness)

    def __str__(self):
        """
        Nicely formatted string for printing.
        Always prints datetime without timezone.
        """
        time_str = self.time.strftime("%Y-%m-%d %H:%M") if self.time else "Okänd tid"
        return (
            f"🕒 Tid: {time_str}\n"
            f"📍 Plats: {self.location_name}\n"
            f"🚨 Händelse: {self.type}\n"
            f"📝 Sammanfattning: {self.summary}\n"
            f"🔗 URL: {self.url or 'Ingen länk'}"
        )
