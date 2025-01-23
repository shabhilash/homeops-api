from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.endpoints.auth import router
from app.utils.auth import get_current_user
from app.utils.db_schemas import User
from app.utils.schemas import UserBase

# OAuth2PasswordBearer tells FastAPI to expect a token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/auth")


@router.get("/users/me", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user