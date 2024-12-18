import logging
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException

from app.server.service_action import service_action
from app.utils.auth import get_current_user
from app.utils.schemas import User

router = APIRouter()

# Logger
logger = logging.getLogger("homeops.service")

class ServiceActions(Enum):
    start = "start"
    stop = "stop"
    restart = "restart"
    reload = "reload"
    enable = "enable"
    disable = "disable"


# noinspection PyUnusedLocal
@router.post(path="/service")
def service_actions(svc: str, action: ServiceActions, current_user: User = Depends(get_current_user)):
    """
    Systemctl actions for linux server \n
    **Supports** : *[start, stop, restart, reload, enable, disable]*
    """
    logger.debug("Endpoint reached - POST - /service")

    success = service_action(svc, action.value)
    if success:
        return {"status": "success", "action": action.value, "service": svc}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to {action.value} service {svc}")

@router.get(path="/service")
def service_status(svc: str):
    """
    Systemctl status for linux server \n
    **Supports** : *[status]*
    """
    logger.debug("Endpoint reached - GET - /service")

    success = service_action(svc, "status")
    if success:
        return {"status": "active", "service": svc}
    else:
        return {"status": "inactive", "service": svc}
