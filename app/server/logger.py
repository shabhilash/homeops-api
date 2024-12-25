import logging
import os
import yaml

from app.conf.log_config import LOGGERFILE
from app.exceptions.logger_error import *

# Logger
logger = logging.getLogger("homeops.logger")


async def change_logger(logger_name, level):
    """
    Endpoint to dynamically change the log level of a logger and update the configuration file.

    **Parameters:**
    - `logger_name` (str): The name of the logger whose level is to be changed.
    - `level` (str): The log level to set. Valid values are "DEBUG", "INFO", "WARNING", "ERROR", and "CRITICAL".

    **Returns:**
    - str: Confirmation message indicating the log level was successfully updated.

    **Raises:**
    - `InvalidLogLevel`: If the provided log level is not valid.
    - `LoggerNotFound`: If the specified logger name does not exist in the logging manager.
    - `ConfigFileNotFound`: If the configuration file is missing or not found.
    - `LoggerUpdateError`: If there is a failure while updating the logger configuration.

    **Error Codes:**
    - `INVALID_LOG_LEVEL_001`: Raised when an invalid log level is provided.
    - `LOGGER_NOT_FOUND_001`: Raised when the specified logger is not found.
    - `CONFIG_FILE_NOT_FOUND_001`: Raised when the configuration file cannot be found.
    - `LOGGER_UPDATE_ERROR_001`: Raised when an error occurs during the update of the logger configuration.
    """
    # Validate log level
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise InvalidLogLevel()

    # Check if the logger exists in the logger manager's dictionary
    if logger_name not in logging.root.manager.loggerDict:
        raise LoggerNotFound()

    # Get the logger
    modify_logger = logging.getLogger(logger_name)

    # Set the new log level in runtime
    modify_logger.setLevel(level)
    modify_logger.warning(f"Log level of logger {logger_name} set to {level}")

    # Update the log level in the configuration file
    try:
        await update_log_level_in_config(logger_name, level)
    except FileNotFoundError:
        raise ConfigFileNotFound()
    except Exception as e:
        logger.error(f"Error updating logger config: {e}")
        raise LoggerUpdateError()

    return f"Log level of logger '{logger_name}' set to {level}"


# Function to update the log level in the YAML config file
async def update_log_level_in_config(logger_name: str, level: str):
    """
    Update the log level of the logger in the YAML configuration file.
    If the logger does not exist, a new entry is created with the given settings.

    **Parameters:**
    - `logger_name` (str): The name of the logger to update.
    - `level` (str): The new log level to set for the logger.

    **Raises:**
    - `FileNotFoundError`: If the configuration file cannot be found.
    - `LoggerNotInConfig`: If the logger is not found and creation fails.

    **Error Codes:**
    - `CONFIG_FILE_NOT_FOUND_001`: Raised when the configuration file cannot be found.
    - `LOGGER_NOT_IN_CONFIG_001`: Raised when the logger is not found in the config file.
    """
    # Load the existing YAML config file
    if not os.path.exists(LOGGERFILE):
        raise FileNotFoundError(f"Configuration file '{LOGGERFILE}' not found.")

    with open(LOGGERFILE, 'r') as file:
        config = yaml.safe_load(file)

    # Check if the logger section exists
    if logger_name not in config['loggers']:
        # Create a new logger entry if it does not exist
        config['loggers'][logger_name] = {
            'level': level,
            # 'handlers': [],  # Add handlers as per your default configuration
            # 'propagate': False  # Default propagate value
        }
        logger.info(f"Logger '{logger_name}' not found. Created new entry with level '{level}'.")

    else:
        # Update the level in the config dictionary
        config['loggers'][logger_name]['level'] = level
        logger.debug(f"Updated log level of logger '{logger_name}' to '{level}'.")

    # Save the updated config back to the YAML file
    with open(LOGGERFILE, 'w') as file:
        yaml.safe_dump(config, file)

    # Log the update
    main_logger = logging.getLogger('homeops')
    main_logger.info(f"Updated log level of '{logger_name}' to {level} in config file.")
