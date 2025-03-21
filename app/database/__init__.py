from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.logger import logger
from app.database.base import Base
from app.database.config import Config
from app.exceptions.global_exception import GlobalHTTPException

# FOR PROD
engine = create_engine(f'sqlite:///homeops.sqlite', echo=False)

# FOR DEV
# engine = create_engine("sqlite:///:memory:", echo=False,connect_args={'check_same_thread': False})

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Custom error handling for database connection issues
def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            logger.info("DB04_OK")
            logger.debug("Status: %s", result)
    except Exception as e:
        logger.exception("Error testing database connection: %s", e)
        raise GlobalHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Unable to Connect to Database",
                detail="The connection to the database could not be established.",
                code="DB06_CONNFAIL"
        )