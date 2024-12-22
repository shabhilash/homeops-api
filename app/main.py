import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.conf import app_config
from app.endpoints import log, reload, service, auth, disk_usage, cpu_usage, memory_usage
from app.exceptions.exceptions import UserNotFoundError, InvalidPasswordError
from app.exceptions.handlers import invalid_username_exception_handler, invalid_password_exception_handler, \
    general_exception_handler
from app.utils.db_init import engine, create_admin_user, test_db_connection

# FastAPI app initialization
app = FastAPI(title=app_config.config["app"]["name"], version="0.2", root_path="/api",
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


# #### EXCEPTION HANLDERS ####
app.add_exception_handler(UserNotFoundError, invalid_username_exception_handler)
app.add_exception_handler(InvalidPasswordError, invalid_password_exception_handler)
app.add_exception_handler(HTTPException, general_exception_handler)

# #### USER MANAGEMENT ####
app.include_router(reload.router, tags=["user"])
app.include_router(auth.router, tags=["user"])

# #### SERVER ACTIONS ####
app.include_router(service.router, prefix="/server", tags=["server"])
app.include_router(disk_usage.router, prefix="/server", tags=["server"])
app.include_router(cpu_usage.router, prefix="/server", tags=["server"])
app.include_router(memory_usage.router, prefix="/server", tags=["server"])

# #### LOGGER ACTIONS ####
app.include_router(log.router, tags=["logger"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
