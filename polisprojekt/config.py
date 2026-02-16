from __future__ import annotations
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Europe/Stockholm")

DB_DIR = PROJECT_ROOT / "db"
DB_DIR.mkdir(exist_ok=True)

ARCHIVE_DIR = DB_DIR / "archive"
ARCHIVE_DIR.mkdir(exist_ok=True)

def active_events_db_path(dt: datetime | None = None) -> Path:
    if dt is None:
        dt = datetime.now(TZ)
    return DB_DIR / f"events_{dt.year}.db"