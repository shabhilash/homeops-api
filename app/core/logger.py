"""
https://docs.python.org/3/library/logging.html#logging-levels
Priority -
High -> Low
NOTSET-0, DEBUG-10, INFO-20, WARNING-30, ERROR-40, CRITICAL-50
"""
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_FILE = "homeops.log"
LOG_ROTATION_TIME = "midnight"
LOG_BACKUP_COUNT = 7

LOG_FORMATS = {
    logging.DEBUG: "%(created).0f DBG P%(process)d:%(module)s:%(lineno)d %(message)s",
    logging.INFO: "%(created).0f INF %(message)s",
    logging.WARNING: "%(created).0f WRN %(message)s",
    logging.ERROR: "%(created).0f ERR %(module)s:%(lineno)d %(message)s",
    logging.CRITICAL: "%(created).0f CRT %(message)s",
}


class LevelBasedFormatter(logging.Formatter):
    """Custom formatter with compressed formats and pre-initialized formatters"""
    def __init__(self):
        super().__init__()
        self.formatters = {level: logging.Formatter(fmt) for level, fmt in LOG_FORMATS.items()}

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.formatters[logging.INFO])
        return formatter.format(record)


# Initialize Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LevelBasedFormatter())
logger.addHandler(console_handler)

# File Handler with Daily Log Rotation
file_handler = TimedRotatingFileHandler(LOG_FILE, when=LOG_ROTATION_TIME, interval=1, backupCount=LOG_BACKUP_COUNT, utc=True)
file_handler.setFormatter(LevelBasedFormatter())
logger.addHandler(file_handler)


def set_log_level(level):
    """Dynamically update log level for all handlers"""
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


# Set initial log level
set_log_level(logging.DEBUG)
