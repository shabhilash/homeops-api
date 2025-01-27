import logging
from http import HTTPStatus

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse

from app.exceptions.user_error import UsernameExistsError
from app.models.user import UserCreateRequest
from app.server.users.create_user import create_user_if_not_exists
from app.utils.auth import hash_password, is_superuser_required
from app.utils.db_schemas import User

logger = logging.getLogger("homeops.db")


router = APIRouter()


@router.post("/create", response_model=dict)  # Use POST for creating resources
def post_create_user(user_data: UserCreateRequest,current_user: User = Depends(is_superuser_required())):
    """
    Function to create user
    """
    logger.debug(
        f"Endpoint reached - POST - /create by user {current_user.username}")
    logger.debug("Initialize user creation")

    user_data.password = hash_password(user_data.password)
    status = create_user_if_not_exists(user_data.model_dump())

    if status.get("error"):
        raise UsernameExistsError()

    return JSONResponse(status_code=HTTPStatus.OK, content=status)
