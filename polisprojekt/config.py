from __future__ import annotations
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TZ = ZoneInfo("Europe/Stockholm")

DB_DIR = PROJECT_ROOT / "db"
DB_DIR.mkdir(exist_ok=True)

STATE_DB_PATH = DB_DIR / "state.db"

ARCHIVE_DIR = DB_DIR / "archive"
ARCHIVE_DIR.mkdir(exist_ok=True)

def events_db_path_for(dt: datetime | None = None) -> Path:
    """Returnerar rätt events-db för året (events_YYYY.db)."""
    if dt is None:
        dt = datetime.now(TZ)
    year = dt.year
    return ARCHIVE_DIR / f"events_{year}.db"