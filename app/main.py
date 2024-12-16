import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.conf import app_config
from app.endpoints import log, reload, service, auth, user
from app.utils.db_init import engine

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
    engine.dispose()


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

# #### SERVICE ACTIONS ####
app.include_router(service.router)

app.include_router(auth.router, tags=["auth"])
app.include_router(user.router, tags=["users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)