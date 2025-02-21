import subprocess

from starlette import status

from app.core.logger import logger
from app.exceptions.global_exception import GlobalHTTPException


def get_password_info(username):
    try:
        # Run the chage command to get password info
        result = subprocess.run(['chage', '-l', username], capture_output=True, text=True)

        if result.returncode == 0:
            details = {}
            for line in result.stdout.splitlines():
                if line.strip():
                    try:
                        key, value = line.split(":", 1)
                        # Mapping to one word keys for easier parsing
                        key_mapping = {
                            "Last password change": "last_password_change",
                            "Password expires": "password_expires",
                            "Password inactive": "password_inactive",
                            "Account expires": "account_expires",
                            "Minimum number of days between password change": "min_days_between_change",
                            "Maximum number of days between password change": "max_days_between_change",
                            "Number of days of warning before password expires": "warning_days_before_expiry"
                        }
                        # Use mapped key if exists, otherwise keep original key
                        mapped_key = key_mapping.get(key.strip(), key.strip().lower().replace(" ", "_"))
                        details[mapped_key] = value.strip()
                    except ValueError:
                        logger.warning("Malformed chage line")
            return details
        else:
            logger.error(f"Chage command error: {result.stderr.strip()}")
            raise GlobalHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Chage Command Error",
                detail="Error while fetching password info",
                code="CHAGE_COMMAND_FAILED"
            )
    except FileNotFoundError:
        logger.error("chage command not found")
        raise GlobalHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            title="chage not found",
            detail="Ensure chage is installed",
            code="CHAGE_COMMAND_NOT_FOUND"
        )
    except PermissionError:
        logger.error(f"Permission error for user {username}")
        raise GlobalHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission Denied",
            detail="Permission issue with chage",
            code="CHAGE_PERMISSION_DENIED"
        )
    except Exception as e:
        logger.exception(f"Error running chage for {username}: {e}")
        raise GlobalHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail="An error occurred while fetching password data",
            code="UNEXPECTED_ERROR"
        )