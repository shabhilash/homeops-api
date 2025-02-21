"""
https://docs.python.org/3/library/logging.html#logging-levels

NOTSET-0, DEBUG-10, INFO-20, WARNING-30, ERROR-40, CRITICAL-50
"""
import logging

# Constants for log format and date format
LOG_FORMAT = "%(asctime)s %(levelno)s %(message)s"
DATE_FORMAT = "%m:%d-%H:%M:%S"

# Initialize Logger
logger = logging.getLogger("homeops")
logger.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(console_handler)

def set_log_level(level):
    """Dynamically updates the log level of all handlers."""
    level = level if isinstance(level, int) else logging.INFO  # Default to INFO if invalid level
    for handler in logger.handlers:
        handler.setLevel(level)

# Example usage to change log level dynamically
set_log_level(logging.DEBUG)  # Now logs DEBUG and above
