from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.endpoints.auth import get_db
from app.utils.db_schemas import User
import os

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Make sure to set a real secret key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # You can adjust this to the desired expiration time

# OAuth2PasswordBearer is used to extract the token from the "Authorization" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify if a password matches the hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Create JWT token using Authlib
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode({"alg": ALGORITHM}, to_encode, SECRET_KEY)
    return encoded_jwt.decode("utf-8")  # Return as a string for easy use


# Verify JWT token using Authlib
def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY)
        return payload
    except JoseError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token using Authlib
        payload = jwt.decode(token, SECRET_KEY)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # You can add a database query here to fetch the user from the DB if needed
        user = db.query(User).filter(username == User.username).first()
        if user is None:
            raise credentials_exception
    except JoseError:
        raise credentials_exception
    return user


def role_required(role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency


def is_superuser_required():
    def superuser_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,  # FORBIDDEN
                detail="User does not have superuser permissions",
            )
        return current_user
    return superuser_dependency
