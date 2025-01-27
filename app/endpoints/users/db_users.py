import logging
from http import HTTPStatus

from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.models.user import DbStats
from app.server.users.user_stats import get_db_users_count

# Logger
logger = logging.getLogger("homeops.db")

# Create FastAPI router
router = APIRouter()

@router.get("/stats")
def get_user_stats():
    """
    Function to get user stats
    """
    logger.debug("Fetching DB User stats")

    db_stats = DbStats(
        user_count= get_db_users_count()
    )

    return JSONResponse(status_code=HTTPStatus.OK,content= db_stats.model_dump())


