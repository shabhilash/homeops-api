import logging
from enum import Enum
from fastapi import APIRouter, Depends

from app.exceptions.exceptions import CustomHTTPException
from app.server.service_action import service_action
from app.utils.auth import get_current_user
from app.utils.schemas import User

router = APIRouter()

# Logger setup
logger = logging.getLogger("homeops.service")


class ServiceActions(Enum):
    """
    Enum for supported service actions.
    """
    start = "start"
    stop = "stop"
    restart = "restart"
    reload = "reload"
    enable = "enable"
    disable = "disable"


def validate_service_action(action: str):
    """
    Validate the provided service action.

    Args:
        action (str): The action to validate.

    Returns:
        ServiceActions: The validated service action.

    Raises:
        CustomHTTPException: If the action is not valid.
    """
    try:
        return ServiceActions[action]
    except KeyError:
        raise CustomHTTPException(status_code=400, detail=f"Invalid service action: {action}",
                                  code="INVALID_ACTION_001")


@router.post(path="/service")
def service_actions(svc: str, action: str, current_user: User = Depends(get_current_user)):
    """
    Perform a systemctl action on a Linux server service.

    Args:
        svc (str): The name of the service to perform the action on.
        action (str): The action to perform. Supported actions are: start, stop, restart, reload, enable, disable.
        current_user (User): The current authenticated user (injected by Depends).

    Returns:
        dict: A dictionary with the status of the action, the action performed, and the service name.

    Raises:
        CustomHTTPException: If the service action fails.
    """
    logger.debug(f"Endpoint reached - POST - /service with action: {action} for service: {svc} by user {current_user.username}")

    try:
        action_enum = validate_service_action(action)
        success = service_action(svc, action_enum.value)
        if success:
            return {"status": "success", "action": action_enum.value, "service": svc}
        else:
            raise CustomHTTPException(status_code=500, detail=f"Failed to {action_enum.value} service {svc}",
                                      code="SERVICE_ACTION_FAILED_001")
    except CustomHTTPException as exc:
        logger.error(f"Error performing service action: {exc.detail} - Code: {exc.code}")
        raise exc


@router.get(path="/service")
def service_status(svc: str):
    """
    Get the status of a Linux server service.

    Args:
        svc (str): The name of the service to get the status for.

    Returns:
        dict: A dictionary with the status of the service and the service name.

    Raises:
        CustomHTTPException: If fetching the service status fails.
    """
    logger.debug(f"Endpoint reached - GET - /service for service: {svc}")

    try:
        success = service_action(svc, "status")
        if success:
            return {"status": "active", "service": svc}
        else:
            return {"status": "inactive", "service": svc}
    except CustomHTTPException as exc:
        logger.error(f"Error fetching service status for {svc}: {exc.detail} - Code: {exc.code}")
        raise exc
    except Exception as err:
        logger.error(f"Unexpected error fetching service status for {svc}: {err}")
        raise CustomHTTPException(status_code=500, detail=str(err), code="UNKNOWN_ERROR_003")
