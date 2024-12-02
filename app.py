import logging
from fastapi import FastAPI, HTTPException
from conf import app_config
from database import *
from pydantic import BaseModel
from logger import change_logger
from logging.handlers import RotatingFileHandler

from sync_adusers import add_ad_users

# FastAPI app initialization
app = FastAPI(title=app_config.config["app"]["name"], version=app_config.config["app"]["version"],
              description=f"{app_config.config["app"]["name"]} is a hobby project to automate my homelab maintanence")

# logger
root_logger = app_config.logger
logger = root_logger.getChild('app')


@app.on_event("startup")
async def startup():
    logger.info("Starting Application")
    # Initialize your database connection
    await db_connect()


@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down Application")
    await db_disconnect()


@app.get("/", tags=["default"], name="root", summary="Root endpoint to check if the service is running")
def read_root():
    '''
    To test if the API is working \n
    Success Response \n
    '''
    logger.debug("Root endpoint accessed")
    return {"status": True}


# #### DB ACTIONS ####

@app.post("/dbcreate", tags=["database"], name="create database", summary="Create a new Database", status_code=201)
async def dbcreate():
    '''
    This endpoint will create a database if not present and creates tables [users]
    '''
    logger.debug("Endpoint Reached - /dbcreate")
    result = await create_database()
    if not result["status"]:
        raise HTTPException(status_code=500, detail=result["message"])
    db_logger = root_logger.getChild('db')
    db_logger.info("Database Created")
    return {"message": result["message"]}


@app.put("/refresh/users", tags=["database"], status_code=204)
async def refresh_users():
    '''
    This endpoint will sync all the AD users to the local database
    '''
    await add_ad_users()
    # return {"message": "Users Refreshed"}

# #### LOGGER ACTIONS ####

# Define a model for the request body


class LogLevel(BaseModel):
    logger_name: str
    level: str


@app.post("/log-level", tags=["logger"], name="logger", summary="Modify Loggers on the go")
async def log_level(log_level: LogLevel):
    """
    Endpoint to change the log level of a logger dynamically and update the config file.
    """
    logger.debug("Endpoint Reached - /log-level")
    result = await change_logger(log_level.logger_name, log_level.level.upper())
    return {"message": result}


@app.get("/log-list", tags=["logger"])
async def log_list():
    """
    Endpoint to list all loggers and their current levels.
    """
    # logger.debug("Endpoint Reached - /log-list")
    loggers = []
    # Iterate over all defined loggers in the logging module
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        loggers.append({
            "logger_name": logger_name,
            "level": logging.getLevelName(logger.level)
        })
    return {"loggers": loggers}

# #### EOF ####
