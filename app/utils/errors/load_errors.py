import json
import os

from app.core import logger

# Define the path to the error codes JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_CODES_FILE = os.path.join(BASE_DIR, "error_codes.json")

def load_error_codes():
    """Load error codes from the JSON file."""
    try:
        with open(ERROR_CODES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.info(f"Error loading error codes: {e}")
        return []

# Load error codes once at import time
error_codes = load_error_codes()
