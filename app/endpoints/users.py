from enum import Enum

from fastapi import APIRouter, Depends
from fastapi import status

from app.core.logger import logger
from app.exceptions.global_exception import GlobalHTTPException
from app.server.users.get_all_users import get_all_users
from app.server.users.get_user_details import get_user_details
from app.utils.db.config import get_config_value
from app.core.rate_limiter import RateLimiter

users_router = APIRouter(prefix="/users",
                         dependencies=[Depends(RateLimiter(requests_limit=int(get_config_value("REQUEST_LIMIT")),
                                                           time_window=int(get_config_value("TIME_WINDOW"))))])


class UserScope(str, Enum):
    all = "all"
    active = "active"


@users_router.get("")
async def get_users(scope: UserScope = UserScope.all):
    """
    Get all users List
    \n
    :param scope: all (Default) \n
    :param scope: active (Optional) \n
    :return: List of users
    """
    try:
        users = get_all_users(scope)
        if not users:
            raise GlobalHTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    title="No Users Found",
                    detail="No users found matching the criteria.",
                    code="NO_USERS_FOUND"
            )
        return users
    except GlobalHTTPException as e:
        # Log the error and raise the exception
        logger.error(f"GlobalHTTPException: {e.detail}")
        raise e
    except Exception as e:
        # Log any unexpected codes
        logger.exception("Unexpected error while fetching users.")
        raise GlobalHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Internal Server Error",
                detail="An unexpected error occurred while processing your request.",
                code="INTERNAL_SERVER_ERROR"
        )


@users_router.get("/{username}")
def get_users_username(username):
    """
    Get specific user details
    \n
    :param username: str \n
    :return: Dict of user details \n
    """
    return get_user_details(username)