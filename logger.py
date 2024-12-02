import logging
from fastapi import HTTPException
from conf.log_config import logger
import configparser


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
    logger = logging.getLogger(logger_name)

    # Set the new log level in runtime
    logger.setLevel(level)
    logger.warning(f"Log level of logger '{logger_name}' set to {level}")

    # Update the log level in the configuration file
    await update_log_level_in_config(logger_name, level)

    return {"message": f"Log level of logger '{logger_name}' set to {level}"}


async def update_log_level_in_config(logger_name: str, level: str):
    """
    Update the log level of the logger in the config file.
    """
    config_file = 'autolab.ini'  # Path to your config file (update this if needed)

    # Load the existing config file
    config = configparser.ConfigParser()
    config.read(config_file)

    # Convert dots to underscores for the section name
    logger_section = f'logger_{logger_name.replace(".", "_")}'

    # Check if the logger section exists
    if logger_section not in config.sections():
        raise HTTPException(status_code=404, detail=f"Logger '{
                            logger_name}' not found in config file")

    # Update the level in the config file
    config.set(logger_section, 'level', level)

    # Save the updated config file
    with open(config_file, 'w') as configfile:
        config.write(configfile)

    # Log the update
    root_logger = logging.getLogger('autolab')
    root_logger.info(f"Updated log level of '{
                     logger_name}' to {level} in config file")
