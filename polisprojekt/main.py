import time
from dotenv import load_dotenv
load_dotenv()

from polisprojekt.config import DISCORD_WEBHOOK, active_events_db_path
from polisprojekt.services.database import EventDB
from polisprojekt.services.pipeline import run_once_discord

from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Stockholm")

if not DISCORD_WEBHOOK:
    raise ValueError("DISCORD_WEBHOOK saknas i .env")

db = EventDB(str(active_events_db_path()))

try:
    while True:
        stats = run_once_discord(db, DISCORD_WEBHOOK)
        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[{now}]")
        print(stats)
        
        time.sleep(30)

except KeyboardInterrupt:
    print("\nStänger ner polisprojekt...")