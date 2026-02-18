from datetime import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from typing import Any
from polisprojekt.data.scoring import SERIOUSNESS
import logging

logger = logging.getLogger(__name__)

@dataclass
class Event:
    event_id: int | None
    datetime_str: str | None
    type: str
    summary: str
    name: str | None
    location: dict[str, Any]
    url: str | None
    raw: dict[str, Any]                 # <-- inga default, ligger här
    raw_type: str | None = None         # <-- default sist

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Event":
        raw_type = data.get("type")
        type_norm = (raw_type or "").strip() or "Okänd typ"

        return cls(
            event_id=data.get("id"),
            datetime_str=data.get("datetime"),
            type=type_norm,
            summary=(data.get("summary") or "Ingen beskrivning"),
            name=data.get("name"),
            location=(data.get("location") or {}),
            url=data.get("url"),
            raw=data,
            raw_type=raw_type,
        )

    @property
    def type_key(self) -> str:
        return (self.type or "").strip()

    @property
    def time(self) -> datetime | None:
        if not self.datetime_str:
            return None

        try:
            dt = datetime.fromisoformat(self.datetime_str.strip())
            return dt.astimezone(ZoneInfo("Europe/Stockholm"))
        except ValueError:
            return None
        
    @property
    def city(self) -> str | None:
        if self.name:
            parts = [p.strip() for p in self.name.split(",") if p.strip()]
            if parts:
                return parts[-1]
        return None

    @property
    def county(self) -> str | None:
        return self.location.get("name")
    
    @property
    def seriousness(self) -> int:
        return SERIOUSNESS.get(self.type_key, 9)

    @property
    def full_url(self) -> str | None:
        return f"https://polisen.se{self.url}" if self.url else None

    def __str__(self):
        t = self.time
        time_str = t.strftime("%Y-%m-%d %H:%M") if t else "Okänd tid"

        city = self.city
        county = self.county

        if city and county and city != county:
            place = f"{city} ({county})"
        elif county:
            place = county
        elif city:
            place = city
        else:
            place = "Okänd plats"

        return (
            f"🕒 Tid: {time_str}\n"
            f"📍 {place}\n"
            f"🚨 Händelse: {self.type}\n"
            f"📝 Sammanfattning: {self.summary}\n"
            f"🔗 URL: {self.full_url or 'Ingen länk'}"
        )
    def to_slack(self) -> str:
        t = self.time
        time_str = t.strftime("%Y-%m-%d %H:%M") if t else "Okänd tid"

        city = self.city
        county = self.county

        if self.type_key not in SERIOUSNESS:
            logger.warning(f"Ograderad händelsetyp upptäckt: {self.type}")
            warning = "⚠️ OBS! OGRADERAD HÄNDELSETYP:\n"
        else:
            warning = ""

        if city and county and city != county:
            place = f"{city} ({county})"
        elif county:
            place = county
        elif city:
            place = city
        else:
            place = "Okänd plats"

        url = self.full_url
        link_part = f"🔗 <{url}|Läs mer>" if url else ""

        return (
            f"{warning}"
            f"🚨 *{self.type}*\n"
            f"🕒 {time_str}\n"
            f"📍 {place}\n"
            f"📝 {self.summary}\n"
            f"{link_part}"
        )
    
    def to_discord(self) -> str:
        t = self.time
        time_str = t.strftime("%Y-%m-%d %H:%M") if t else "Okänd tid"

        city = self.city
        county = self.county

        if self.type_key not in SERIOUSNESS:
            logger.warning(f"Ograderad händelsetyp upptäckt: {self.type}")
            warning = "⚠️ OBS! OGRADERAD HÄNDELSETYP:\n"
        else:
            warning = ""

        if city and county and city != county:
            place = f"{city} ({county})"
        elif county:
            place = county
        elif city:
            place = city
        else:
            place = "Okänd plats"

        url = self.full_url
        link_part = f"\n🔗 {url}" if url else ""

        return (
            f"{warning}"
            f"🚨 **{self.type}**\n"
            f"🕒 {time_str}\n"
            f"📍 {place}\n"
            f"📝 {self.summary}"
            f"{link_part}"
        )