import logging
import os

import yaml
from fastapi import HTTPException

from app.conf.log_config import LOGGERFILE

# Logger
logger = logging.getLogger("homeops.logger")

async def change_logger(logger_name, level):
    """
    Endpoint to change the log level of a logger dynamically and update the config file.
    """
    # Validate log level
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise HTTPException(status_code=400, detail="Invalid log level")

    # Check if the logger exists in the logger manager's dictionary
    if logger_name not in logging.root.manager.loggerDict:
        raise HTTPException(status_code=404, detail=f"Logger '{
                            logger_name}' not found")

    # Get the logger
    modify_logger = logging.getLogger(logger_name)

    # Set the new log level in runtime
    modify_logger.setLevel(level)
    modify_logger.warning(f"Log level of logger {logger_name} set to {level}")

    # Update the log level in the configuration file
    await update_log_level_in_config(logger_name, level)

    return f"Log level of logger '{logger_name}' set to {level}"


# Function to update the log level in the YAML config file
async def update_log_level_in_config(logger_name: str, level: str):
    """
    Update the log level of the logger in the YAML config file.
    """
    # Load the existing YAML config file
    if not os.path.exists(LOGGERFILE):
        raise FileNotFoundError(f"Configuration file '{LOGGERFILE}' not found.")

    with open(LOGGERFILE, 'r') as file:
        config = yaml.safe_load(file)


    # Check if the logger section exists
    if logger_name not in config['loggers']:
        # This can be disabled since the response should be success even if it was not updated on the config file,
        # as not all config is expected to be in the logger file
        raise HTTPException(status_code=200, detail={
            "status": "warning",
            "message": f"'{logger_name}' - Logger level Updated. but the logger was not found in the config file",
            "action": "Verify if the logger is available in the settings.yaml"
        })

    # Update the level in the config dictionary
    config['loggers'][logger_name]['level'] = level

    logger.debug(f"config = {config}")
    # Save the updated config back to the YAML file
    with open(LOGGERFILE, 'w') as file:
        yaml.safe_dump(config, file)

    # Log the update
    main_logger = logging.getLogger('homeops')
    main_logger.info(f"Updated log level of '{logger_name}' to {level} in config file")

