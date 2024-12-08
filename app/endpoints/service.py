import logging
from enum import Enum


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