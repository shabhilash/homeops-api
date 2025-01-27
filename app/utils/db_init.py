import logging

from sqlalchemy import create_engine, text, insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from app.conf.app_config import db_folder
from app.exceptions.exceptions import CustomHTTPException

import os
from contextlib import contextmanager

# Logger
logger = logging.getLogger("homeops.db")

# Database Configuration
def get_db_path():
    # Use environment variable for the database path
    db_path = os.getenv("DB_PATH", f"{db_folder}/homeops.sqlite")
    return db_path

DB_PATH = get_db_path()

# SQLAlchemy engine and session setup
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database connection context manager
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Custom error handling for database connection issues
def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            logger.debug("Database connection successful. Status: %s", result)
            create_admin_user()
    except Exception as e:
        logger.error("Error testing database connection: %s", e)
        raise CustomHTTPException(
            status_code=500,
            detail="Database connection failed",
            code="DB_CONNECTION_FAILED_001"
        )

# Custom error handling for user creation
def create_admin_user():
    from app.utils.db_schemas import User
    admin_user_data = {
        "username": "homeops",
        "first_name": "Homeops",
        "last_name": "Admin",
        "email_address": "homeops@homeops.local",
        "password": "$2b$12$rvb5aM/GwludqnjH3MlM4edVK805TPzmA3pPt/iwp1WvmzXuwcSdq",  # Should be securely managed
        "enabled": 1,
        "is_superuser": 1,
    }

    # Insert user if not exists
    try:
        admin_user = insert(User).values(admin_user_data).prefix_with("OR IGNORE", dialect="sqlite")
        with engine.connect() as conn:
            conn.execute(admin_user)
            conn.commit()
            logger.debug("Admin user created or already exists.")
    except OperationalError as e:
        logger.error("Database operation failed: %s", e)
        if "database is locked" in str(e):
            raise CustomHTTPException(
                    status_code=503,
                    detail="Database is currently locked, please try again later.",
                    code="DATABASE_LOCKED_001"
            )
        else:
            raise CustomHTTPException(
                    status_code=500,
                    detail="Database operation failed.",
                    code="DATABASE_OPERATIONAL_ERROR_001"
            )
    except Exception as e:
        logger.error("Error creating admin user: %s", e)
        raise CustomHTTPException(
                status_code=500,
                detail="Failed to create admin user",
                code="USER_CREATION_FAILED_002"
        )

test_db_connection()