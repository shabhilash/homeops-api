from pydantic import BaseModel
from typing import Optional

# This is for request validation and responses
class UserBase(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: str

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models


# This model extends UserBase and adds more fields
class User(UserBase):
    is_superuser: bool
    enabled: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models


# Pydantic model for User Out (when returning user data to the API)
class UserOut(BaseModel):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email_address: str
    is_superuser: bool
    enabled: bool

    class Config:
        from_attributes = True  # This tells Pydantic to work with SQLAlchemy models

# Pydantic model for User In (when getting user data during login)
class UserInDB(UserOut):
    hashed_password: str  # We use hashed_password to store in DB