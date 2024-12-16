import logging

from fastapi import APIRouter
from app.models.loglevel import LogLevel
from app.server.logger import change_logger

router = APIRouter()

# Logger
logger = logging.getLogger("homeops.app")

@router.put("/log-level", tags=["logger"], name="logger", summary="Modify Loggers on the go")
async def log_level(logger_level: LogLevel):
    """
    Endpoint to change the log level of a logger dynamically and update the config file. \n
    @type logger_level: object
    """
    logger.debug("Endpoint Reached - PUT - /log-level")
    result = await change_logger(logger_level.logger_name, logger_level.level.upper())
    return {"message": result}


@router.get("/log-list", tags=["logger"])
async def log_list():
    """
    Endpoint to list all loggers and their current levels.
    """
    logger.debug("Endpoint Reached - GET - /log-list")
    loggers = []
    # Iterate over all defined loggers in the logging module
    for logger_name in logging.root.manager.loggerDict:
        get_logger = logging.getLogger(logger_name)
        loggers.append({
            "logger_name": logger_name,
            "level": logging.getLevelName(get_logger.level)
        })
    return {"loggers": loggers}