from fastapi import Depends, Security, status
from fastapi.security import APIKeyHeader

from app.core.logger import logger
from app.exceptions.global_exception import GlobalHTTPException
from app.utils.db.config import get_config_value

api_key_header = APIKeyHeader(name="X-API-Key")


async def validate_api_key(key: str = Security(api_key_header)):
    api_key = get_config_value("API_KEY")
    admin_api_key = get_config_value("ADMIN_API_KEY")

    if key not in {api_key, admin_api_key}:
        raise GlobalHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized - Invalid API key",
                detail="API key is invalid or expired. Please check your API key or obtain a new one.",
                code="AUTH03_INVKEY"
        )
    return "admin" if key == admin_api_key else "user"


def require_role(required_role: str):
    def role_checker(role: str = Depends(validate_api_key)):
        if role == "admin":
            logger.info("AUTH02_OK")
            return role
        if role != required_role:
            raise GlobalHTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                      title="Insufficient Permissions",
                                      detail=f"Access Denied - {required_role.capitalize()} Role Required",
                                      code="AUTH02_DENY")
        logger.info("AUTH02_OK")
        return role

    return role_checker