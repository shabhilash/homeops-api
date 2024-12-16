import logging
from enum import Enum

from fastapi import APIRouter, Depends

from app.utils.auth import is_superuser_required
from app.utils.schemas import User

router = APIRouter()

# Logger
logger = logging.getLogger("homeops.service")

class ServiceActions(Enum):
    start: str = "start"
    stop: str = "stop"
    restart: str = "restart"
    reload: str = "reload"
    enable: str = "enable"
    disable: str = "disable"

@router.post(path="/service",tags=["server"])
def service_actions(svc:str,action:ServiceActions,current_user: User = Depends(is_superuser_required())):
    """
    Systemctl actions for linux server \n
    **Supports** : *[start, stop, restart, reload, enable, disable]*
    """
    logger.debug("Endpoint reached - POST - /service")

    return {"status":"success"}

@router.get(path="/service",tags=["server"])
def service_status(svc:str):
    """
    Systemctl status for linux server \n
    **Supports** : *[status]*
    """
    logger.debug("Endpoint reached - GET - /service")

    return {"status":"success"}