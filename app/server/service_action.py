import logging
import subprocess

# Logger
logger = logging.getLogger("homeops.service")

def service_action(name: str, action: str) -> bool:
    """
    Function to perform requested actions on service \n
    @param name: svc \n
    @param action: action \n
    @return: bool \n
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
        logger.exception(f"Command Error: {e.stderr}")
        return False