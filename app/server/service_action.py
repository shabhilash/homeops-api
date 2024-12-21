import logging
import subprocess
from fastapi import HTTPException

# Logger
logger = logging.getLogger("homeops.service")


# Custom HTTP Exceptions
class ServiceError(HTTPException):
    pass


class ServiceNotFound(ServiceError):
    def __init__(self):
        super().__init__(status_code=404, detail="Service not found")


class PermissionDenied(ServiceError):
    def __init__(self):
        super().__init__(status_code=403, detail="Permission denied")


class InvalidArgument(ServiceError):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid argument")


class RequestTimeout(ServiceError):
    def __init__(self):
        super().__init__(status_code=408, detail="Request timeout")


class FailedDependency(ServiceError):
    def __init__(self):
        super().__init__(status_code=424, detail="Failed dependency")


class ConflictError(ServiceError):
    def __init__(self, detail="Conflict error"):
        super().__init__(status_code=409, detail=detail)


class MethodNotAllowed(ServiceError):
    def __init__(self):
        super().__init__(status_code=405, detail="Method not allowed")


class InternalServerError(ServiceError):
    def __init__(self):
        super().__init__(status_code=500, detail="Internal server error")


def service_action(name: str, action: str) -> bool:
    """
    Function to perform requested actions on service

    :param name: Service name
    :param action: Action to perform
    :return: True if successful, raises HTTPException otherwise
    """
    try:
        result = subprocess.run(
            ["sudo", "systemctl", action, name],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Command Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command '{e.cmd}' failed with return code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")

        if "not found" in e.stderr:
            raise ServiceNotFound()
        elif "permission denied" in e.stderr:
            raise PermissionDenied()
        elif "invalid argument" in e.stderr:
            raise InvalidArgument()
        elif "timeout" in e.stderr:
            raise RequestTimeout()
        elif "failed" in e.stderr and "dependency" in e.stderr:
            raise FailedDependency()
        elif "conflict" in e.stderr:
            raise ConflictError()
        elif "already running" in e.stderr:
            raise ConflictError(detail="Service already running")
        elif "not allowed" in e.stderr:
            raise MethodNotAllowed()
        else:
            raise InternalServerError()