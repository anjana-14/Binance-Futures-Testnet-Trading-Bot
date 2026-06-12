"""Logging setup for the trading bot."""

import logging
from datetime import datetime
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_dir: str | Path = "logs", log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure file and console logging with timestamps.

    Returns the root logger for the bot package.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    log_file = log_path / f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger("trading_bot")
    logger.setLevel(log_level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug("Logging initialized; writing to %s", log_file)
    return logger
