from pydantic import BaseModel, EmailStr


class DbStats(BaseModel):
    user_count:int


class UserCreateRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email_address: EmailStr
    enabled: bool
    is_superuser: bool = False
    password: str