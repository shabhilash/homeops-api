from app.core.logger import logger


def get_user_details(username):
    logger.debug(f"Fetching {username} data")

    return {"username":username}