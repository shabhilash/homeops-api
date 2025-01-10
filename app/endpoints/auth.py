import logging
import os
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.problem_details import ProblemDetails
from app.utils.db_init import SessionLocal
from app.utils.db_schemas import User
from passlib.context import CryptContext
from authlib.jose import jwt

from app.exceptions.exceptions import InvalidPasswordError, UserNotFoundError

# Logger
logger = logging.getLogger("homeops.auth")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/auth")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "my-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set token expiry time

# Password Hashing Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create FastAPI router
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash the password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to create JWT token using Authlib
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode({"alg": ALGORITHM}, to_encode, SECRET_KEY)
    return encoded_jwt.decode("utf-8")  # Return as a string for easy use

# Function to get the user from the DB by username
def get_user(db: Session, username: str):
    return db.query(User).filter(username == User.username).first()

# Function to authenticate the user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        logger.error(f"Invalid credentials for username: {username}")
        raise UserNotFoundError(detail="The username is invalid",code="INVALID_USERNAME_002")
    if not verify_password(password, user.password):
        logger.error(f"Invalid password for username: {username}")
        raise InvalidPasswordError(detail="The password is incorrect",code="INVALID_CREDENTIALS_002")
    return user

# Define the response model for the login endpoint
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/auth", response_model=TokenResponse, responses={
    422: {"description": "Invalid Password", "model": ProblemDetails},
    404: {"description": "User Not Found", "model": ProblemDetails},
})
async def login_for_access_token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    logger.debug(f"Received request for username: {username}")

    # Authenticate user
    user = authenticate_user(db, username, password)


    # Define token expiration time (in seconds)
    expires_in = int(os.getenv("SESSION_TIMEOUT_SECONDS", 360))  # 360 seconds or 6 minutes default

    # Create the access token with an expiration time
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(seconds=expires_in))

    # Log the generated token (don't log the token in production for security reasons)
    logger.debug(f"Generated access token for username: {user.username}")

    # Return token and expiration info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }
