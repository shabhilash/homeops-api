import logging
from fastapi import APIRouter, Depends
from app.exceptions.logger_error import LoggerNotFound
from app.models.loglevel import LogLevel
from app.server.logger import change_logger
from app.utils.auth import get_current_user
from app.utils.schemas import User

# Logger
logger = logging.getLogger("homeops.app")


router = APIRouter()


@router.put("/log-level", name="logger", summary="Modify Loggers on the go")
async def log_level(logger_level: LogLevel, current_user: User = Depends(get_current_user)):
    """
    Endpoint to change the log level of a logger dynamically and update the config file.

    **Parameters:**
    - `logger_level` (LogLevel): The logger name and level to be changed.

    **Returns:**
    - `message` (str): A message indicating the result of the operation.

    **Raises:**
    - `InvalidLogLevel`: Raised when the log level provided is invalid.
    - `LoggerNotFound`: Raised when the specified logger is not found in the logging manager.
    - `LoggerUpdateError`: Raised when the logger update fails.

    **Error Codes:**
    - `INVALID_LOG_LEVEL_001`: Raised when an invalid log level is provided.
    - `LOGGER_NOT_FOUND_002`: Raised when the logger is not found in the logging manager.
    - `LOGGER_UPDATE_ERROR_002`: Raised when an error occurs during the update of the logger configuration.
    """
    logger.debug("Endpoint Reached - PUT - /log-level")

    # Call to change the logger's log level
    result = await change_logger(logger_level.logger_name, logger_level.level.upper())

    return {"message": result}


@router.get("/log-list")
async def log_list():
    """
    Endpoint to list all loggers and their current levels.

    **Returns:**
    - `loggers` (list): A list of dictionaries containing logger names and their respective levels.

    **Error Codes:**
    - `LOGGER_NOT_FOUND_001`: Raised if a logger is not found in the logging manager.
    """
    logger.debug("Endpoint Reached - GET - /log-list")
    loggers = []
    # Iterate over all defined loggers in the logging module
    try:
        for logger_name in logging.root.manager.loggerDict:
            get_logger = logging.getLogger(logger_name)
            loggers.append({
                "logger_name": logger_name,
                "level": logging.getLevelName(get_logger.level)
            })
    except Exception as e:
        logger.error(f"Error fetching loggers: {e}")
        raise LoggerNotFound()

    return {"loggers": loggers}
