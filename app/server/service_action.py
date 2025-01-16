import logging
import subprocess
import platform

from app.exceptions.service_error import *

# Logger
logger = logging.getLogger("homeops.service")


def service_action(name: str, action: str) -> bool:
    """
    Function to perform requested actions on a service.

    This function attempts to execute a systemctl action on a given service.
    If the action fails, it raises an appropriate HTTP exception based on the
    error message from the system.

    Args:
        name (str): The name of the service to act upon.
        action (str): The action to perform (e.g., start, stop, restart).

    Returns:
        bool: True if the action is successful.

    Raises:
        ServiceError: If the action fails due to various possible issues.
    """
    if platform.system() != "Linux":
        raise OSNotSupported()

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
        elif "Sudo is disabled" in e.stderr:
            raise SudoDisabled()
        else:
            raise InternalServerError()
