import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import time as dtime
from polisprojekt.config import LOG_FILE_PATH

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("polisprojekt")
    logger.setLevel(logging.INFO)

    # Undvik dubbla handlers om du råkar kalla setup två gånger
    if logger.handlers:
        return logger

    handler = TimedRotatingFileHandler(
        filename=str(LOG_FILE_PATH),
        when="midnight",
        interval=1,
        backupCount=14,      # sparar 14 dagar, raderar äldre automatiskt
        encoding="utf-8",
        utc=False,
        atTime=dtime(3, 0)   # rotera 03:00
    )

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    return logger