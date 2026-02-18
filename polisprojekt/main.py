import time
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from zoneinfo import ZoneInfo

from polisprojekt.config import DISCORD_WEBHOOK, active_events_db_path
from polisprojekt.services.database import EventDB
from polisprojekt.services.pipeline import run_once_discord
from polisprojekt.services.logger import setup_logger

logger = setup_logger()
logger.info("Startar polishändelser…")

TZ = ZoneInfo("Europe/Stockholm")


def main() -> None:
    if not DISCORD_WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK saknas i .env")

    db = EventDB(str(active_events_db_path()))
    logger.info(f"DB: {active_events_db_path()}")

    try:
        while True:
            now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Loop start {now}")

            try:
                stats = run_once_discord(db, DISCORD_WEBHOOK)

                # terminal (valfritt)
                print(f"\n[{now}] {stats}")

                # logg (viktigt)
                logger.info(f"Stats: {stats}")

            except Exception:
                # full traceback i loggen
                logger.exception("ERROR i loop")

                # terminal (valfritt)
                print(f"\n[{now}] ERROR i loop (se logg för traceback)")

            time.sleep(30)

    except KeyboardInterrupt:
        logger.info("Stänger ner polisprojekt (KeyboardInterrupt)")
        print("\nStänger ner polisprojekt...")


if __name__ == "__main__":
    main()