import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.conf import app_config
from app.endpoints import log, reload, service, auth, disk_usage, cpu_usage, memory_usage
from app.exceptions.handlers import *
from app.utils.db_init import engine

# FastAPI app initialization
app = FastAPI(title=app_config.config["app"]["name"], version="0.2", root_path="/api",
              description=f'{app_config.config["app"]["name"]} is a hobby project to automate my homelab maintenance')

# Logger
logger = logging.getLogger("homeops.app")

# noinspection PyTypeChecker
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
@app.exception_handler(UserNotFoundError)
async def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
    return await user_not_found_exception_handler(request, exc)

@app.exception_handler(InvalidPasswordError)
async def invalid_password_exception_handler(request: Request, exc: InvalidPasswordError):
    return await invalid_password_exception_handler(request, exc)

@app.exception_handler(InvalidTokenError)
async def invalid_token_exception_handler(request: Request, exc: InvalidTokenError):
    return await invalid_token_exception_handler(request, exc)

@app.exception_handler(PermissionDeniedError)
async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
    return await permission_denied_exception_handler(request, exc)

@app.exception_handler(HTTPException)
async def general_exception_handler(request: Request, exc: HTTPException):
    return await general_exception_handler(request, exc)


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
