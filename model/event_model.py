from datetime import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from typing import Any

@dataclass
class Event:
    id: int | None
    datetime_str: str | None
    type: str
    summary: str
    location: dict[str, Any]
    url: str | None
    raw_type: str | None = None  # <-- spårning

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Event":
        raw_type = data.get("type")
        type_norm = (raw_type or "").strip() or "Okänd typ"

        return cls(
            id=data.get("id"),
            datetime_str=data.get("datetime"),
            type=type_norm,
            summary=(data.get("summary") or "Ingen beskrivning"),
            location=(data.get("location") or {}),
            url=data.get("url"),
            raw_type=raw_type,
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
    def location_name(self) -> str:
        return self.location.get("name", "Okänd plats")


    @property
    def full_url(self) -> str | None:
        return f"https://polisen.se{self.url}" if self.url else None

    def __str__(self):
        t = self.time  # hämta en gång
        time_str = t.strftime("%Y-%m-%d %H:%M") if t else "Okänd tid"

        return (
            f"🕒 Tid: {time_str}\n"
            f"📍 Plats: {self.location_name}\n"
            f"🚨 Händelse: {self.type}\n"
            f"📝 Sammanfattning: {self.summary}\n"
            f"🔗 URL: {self.full_url or 'Ingen länk'}"
        )
