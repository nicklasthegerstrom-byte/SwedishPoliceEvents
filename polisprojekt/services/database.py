from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from polisprojekt.config import PROJECT_ROOT
from polisprojekt.model.event_model import Event


class EventDB:
    """
    Minimal SQLite-store:
    - events: historik (en rad per event-id)
    - notified: vilka event vi redan postat till Slack
    """

    def __init__(self, db_path: Path | None = None) -> None:
        # Default: database ligger i projektroten
        self.db_path = db_path or (PROJECT_ROOT / "database.db")
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        # Skapar parent-dir om du skulle peka db_path mot en undermapp
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path, timeout=10)

    def _init_db(self) -> None:
        with self._connect() as con:
            # 1) events-tabell (historik)
            con.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY,
                    datetime TEXT,
                    type TEXT,
                    summary TEXT,
                    name TEXT,
                    city TEXT,
                    county TEXT,
                    gps TEXT,
                    url TEXT,
                    fetched_at TEXT NOT NULL,
                    raw_json TEXT NOT NULL
                )
            """)

            # 2) notified-tabell (dedupe för Slack)
            con.execute("""
                CREATE TABLE IF NOT EXISTS notified (
                    event_id INTEGER PRIMARY KEY,
                    notified_at TEXT NOT NULL
                )
            """)

            con.commit()

    def save_event(self, e: Event, raw: dict[str, Any]) -> bool:
        """
        Spara event i events-tabellen.
        Returnerar True om eventet var nytt (sparades), annars False.
        """
        if e.id is None:
            return False

        fetched_at = datetime.now(timezone.utc).isoformat()

        # plocka gps från raw (du ville spara den)
        gps = None
        loc = raw.get("location")
        if isinstance(loc, dict):
            gps_val = loc.get("gps")
            if isinstance(gps_val, str):
                gps = gps_val

        raw_json = json.dumps(raw, ensure_ascii=False)

        with self._connect() as con:
            cur = con.execute("""
                INSERT OR IGNORE INTO events
                (id, datetime, type, summary, name, city, county, gps, url, fetched_at, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                e.id,
                e.datetime_str,
                e.type,
                e.summary,
                e.name,
                e.city,
                e.county,
                gps,
                e.url,
                fetched_at,
                raw_json,
            ))
            con.commit()
            return cur.rowcount == 1

    def mark_notified_if_new(self, event_id: int) -> bool:
        """
        Markera att vi notifierat eventet.
        Returnerar True om det var första gången (dvs posta till Slack),
        annars False.
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as con:
            cur = con.execute(
                "INSERT OR IGNORE INTO notified (event_id, notified_at) VALUES (?, ?)",
                (event_id, now),
            )
            con.commit()
            return cur.rowcount == 1