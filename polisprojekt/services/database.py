from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from polisprojekt.config import PROJECT_ROOT
from polisprojekt.model.event_model import Event


class EventDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _ensure_schema(self) -> None:
        """Ensure required tables exist."""
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

    def save_event(self, e: Event) -> bool:
        if e.event_id is None:
            return False

        fetched_at = datetime.now(timezone.utc).isoformat()

        gps = None
        loc = e.raw.get("location")
        if isinstance(loc, dict):
            gps = loc.get("gps")

        raw_json = json.dumps(e.raw, ensure_ascii=False)

        with self._connect() as con:
            cur = con.execute("""
                INSERT OR IGNORE INTO events
                (event_id, datetime, type, summary, name, city, county, gps, url, fetched_at, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                e.event_id,
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
        
    def is_notified(self, event_id: int) -> bool:
        """True om event_id redan finns i notified-tabellen."""
        if event_id is None:
            return False

        with self._connect() as con:
            row = con.execute(
                "SELECT 1 FROM notified WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            return row is not None    
        
    def mark_notified(self, event_id: int) -> None:
        """Sparar att eventet har notifierats (ska kallas EFTER lyckad Slack-post)."""
        if event_id is None:
            return

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO notified (event_id, notified_at) VALUES (?, ?)",
                (event_id, now),
            )
            con.commit()   

        #OBS JAG BEHÖVER INTE DENNA JUST NU TA BORT SEN
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
        
    
        