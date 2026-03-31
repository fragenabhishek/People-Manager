"""
Logging utility module
Provides human-readable logging in dev and JSON-structured logging in production.
"""
import json
import logging
import sys
from typing import Optional

from config import Config


class JSONFormatter(logging.Formatter):
    """Outputs one JSON object per log line for log aggregation services."""

    def format(self, record):
        entry = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
        }
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


_DEV_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logger(
    name: str = 'people_manager',
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    if Config.DEBUG:
        formatter = logging.Formatter(_DEV_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        formatter = JSONFormatter()

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def get_logger(name: str = 'people_manager') -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)
