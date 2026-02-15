from datetime import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from typing import Any

@dataclass
class Event:
    event_id: int | None
    datetime_str: str | None
    type: str
    summary: str
    name: str | None
    location: dict[str, Any]
    url: str | None
    raw_type: str | None = None  # <-- spårning
    raw: dict[str, Any]

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
            raw_type=raw_type,
            raw=data
        )

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
    def full_url(self) -> str | None:
        return f"https://polisen.se{self.url}" if self.url else None

    def __str__(self):
        t = self.time
        time_str = t.strftime("%Y-%m-%d %H:%M") if t else "Okänd tid"

        city = self.city
        county = self.county

        if city and county:
            place_line = f"📍 {city} ({county})"
        elif county:
            place_line = f"📍 {county}"
        else:
            place_line = "📍 Okänd plats"

        return (
            f"🕒 Tid: {time_str}\n"
            f"{place_line}\n"
            f"🚨 Händelse: {self.type}\n"
            f"📝 Sammanfattning: {self.summary}\n"
            f"🔗 URL: {self.full_url or 'Ingen länk'}"
        )
    def to_slack(self) -> str:
        t = self.time
        time_str = t.strftime("%Y-%m-%d %H:%M") if t else "Okänd tid"

        city = self.city
        county = self.county

        if city and county:
            place_line = f"📍 {city} ({county})"
        elif city:
            place_line = f"📍 {city}"
        elif county:
            place_line = f"📍 {county}"
        else:
            place_line = "📍 Okänd plats"

        url = self.full_url
        link_part = f"🔗 <{url}|Läs mer>" if url else ""

        return (
            f"🚨 *{self.type}*\n"
            f"🕒 {time_str}\n"
            f"{place_line}\n"
            f"📝 {self.summary}\n"
            f"{link_part}"
        )