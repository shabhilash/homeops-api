import logging
from fastapi import HTTPException
import configparser
from conf.log_config import CONFIGFILE

# Logger
logger = logging.getLogger("homeops.db")

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


async def update_log_level_in_config(logger_name: str, level: str):
    """
    Update the log level of the logger in the config file.
    """

    # Load the existing config file
    config = configparser.ConfigParser()
    config.read(CONFIGFILE)
    logger.debug(f"Config Sections: {config.sections()}")
    # Convert dots to underscores for the section name
    logger_section = f'logger_{logger_name.replace(".", "_")}'

    logger.debug(f"Logger Section: {logger_section}")



    # Check if the logger section exists
    if logger_section not in config.sections():
        # This can be disabled since the response should be success even it was not updated on config file, as Not all config is expected to be on the logger file
        raise HTTPException(status_code=200, detail={"status": "warning",
                                                     "message":f"'{logger_name}' - Logger level Updated. but the logger was not found in the config file",
                                                     "action":"Verify if the logger is available in settings.ini"})

    # Update the level in the config file
    config.set(logger_section, 'level', level)

    # Save the updated config file
    with open(CONFIGFILE, 'w') as configfile:
        # noinspection PyTypeChecker
        config.write(configfile)

    # Log the update
    main_logger = logging.getLogger('homeops')
    main_logger.debug(f"Updated log level of '{
                     logger_name}' to {level} in config file")
