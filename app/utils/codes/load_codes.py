import os
import json
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_and_merge_json_files():
    """Load and merge all JSON files in the directory into a single JSON object."""
    merged_data = {}

    for filename in os.listdir(BASE_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(BASE_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                    if isinstance(data, dict):  # Merge dictionaries
                        merged_data.update(data)
                    elif isinstance(data, list):  # Append lists under filename key
                        merged_data[filename] = data
                    else:
                        logger.warning(f"Skipping {filename}: Unsupported JSON format")

            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Error loading {filename}: {e}", exc_info=True)

    return merged_data

# Load merged JSON at import time
codes = load_and_merge_json_files()
