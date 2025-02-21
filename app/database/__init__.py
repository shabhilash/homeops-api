from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.logger import logger
from app.database.base import Base
from app.database.config import Config
from app.exceptions.global_exception import GlobalHTTPException

engine = create_engine(f'sqlite:///homeops.sqlite', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Custom error handling for database connection issues
def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            logger.info("Database connection successful. Status: %s", result)
    except Exception as e:
        logger.info("Error testing database connection: %s", e)
        raise GlobalHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Unable to Connect to Database",
                detail="The connection to the database could not be established.",
                code="DATABASE_CONNECTION_ERROR"
        )