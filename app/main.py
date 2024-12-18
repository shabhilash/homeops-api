import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.conf import app_config
from app.endpoints import log, reload, service, auth, user
from app.utils.db_init import engine

# FastAPI app initialization
app = FastAPI(title=app_config.config["app"]["name"], version="0.2",root_path="/api",
              description=f'{app_config.config["app"]["name"]} is a hobby project to automate my homelab maintenance')

# Logger
logger = logging.getLogger("homeops.app")

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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

# #### USER MANAGEMENT ####
app.include_router(reload.router,tags=["user"])
app.include_router(auth.router, tags=["user"])

# #### SERVER ACTIONS ####
app.include_router(service.router, tags=["server"])

# #### LOGGER ACTIONS ####
app.include_router(log.router, tags=["logger"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)