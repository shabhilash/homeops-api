import logging
from fastapi import APIRouter, HTTPException
from server.database import create_database

router = APIRouter()

# Logger
logger = logging.getLogger("homeops.app")

@router.post("/dbcreate", tags=["database"], name="create database", summary="Create a new Database", status_code=201)
async def dbcreate():
    """
    This endpoint will create a database if not present and creates tables [users]
    """
    logger.debug("Endpoint Reached - /dbcreate")
    result = await create_database()
    if not result["status"]:
        raise HTTPException(status_code=500, detail=result["message"])
    db_logger = logging.getLogger("homeops.db")
    db_logger.info("Database Created")
    return {"message": result["message"]}