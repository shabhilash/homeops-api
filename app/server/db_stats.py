import logging

from sqlalchemy import select, func

from app.exceptions.exceptions import CustomHTTPException
from app.utils.db_init import engine
from app.utils.db_schemas import User


# Logger
logger = logging.getLogger("homeops.db")

def get_db_users_count():
    # Fetch user count
    try:
        with engine.connect() as conn:
            user_count_query = select(func.count()).select_from(User)
            result = conn.execute(user_count_query)
            user_count = result.scalar()  # Fetch the scalar value (count)
            logger.info(f"Total users in database: {user_count}")
            return user_count
    except Exception as e:
        logger.exception("Error fetching user count: %s", e)
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to fetch user count",
            code="USER_COUNT_FETCH_FAILED_001"
        )