import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from app.conf import app_config
from app.endpoints import log, reload

# FastAPI app initialization
app = FastAPI(title=app_config.config["app"]["name"], version="0.1.5Beta",
              description=f"{app_config.config["app"]["name"]} is a hobby project to automate my homelab maintenance")

# Logger
logger = logging.getLogger("homeops.app")

@asynccontextmanager
async def lifespan():
    logger.critical("Starting Application")
    # Initialize database connection

    yield
    logger.critical("Shutting down Application")
    # Close database connection



@app.get("/", tags=["default"], name="root", summary="Root endpoint to check if the service is running")
def read_root():
    """
    To test if the API is working \n
    Success Response \n
    """
    logger.debug("Root endpoint accessed")
    return {"status": True}

# #### DB ACTIONS ####
app.include_router(reload.router)

# #### LOGGER ACTIONS ####
app.include_router(log.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)