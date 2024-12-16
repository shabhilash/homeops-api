import logging

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.utils.db_init import SessionLocal
from app.utils.db_schemas import User
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from datetime import timedelta, datetime

# Logger
logger = logging.getLogger("homeops.auth")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
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

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get the user from the DB by username
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Function to authenticate the user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user

# Route for generating the token (login)
# Define the response model for the login endpoint
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/token", response_model=TokenResponse)  # Use TokenResponse here
async def login_for_access_token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    logger.debug(f"Received username: {username}, password: {password}")

    # Authenticate user
    user = authenticate_user(db, username, password)

    if not user:
        logger.error(f"Invalid credentials for username: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Define token expiration time (in seconds)
    expires_in = 360  # This is 6 minutes

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
