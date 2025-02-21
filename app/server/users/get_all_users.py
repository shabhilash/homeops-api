from app.core.logger import logger
from app.exceptions.global_exception import GlobalHTTPException
from fastapi import status

from app.server.users.get_password_info import get_password_info


def parse_passwd_line(line):
    try:
        # Split the line by colon ":"
        fields = line.strip().split(":")

        if len(fields) < 7:
            logger.warning("Malformed line detected")
            return None

        user_dict = {
            "username": fields[0],
            "user_id": int(fields[2]),
            "group_id": int(fields[3]),
            "full_name": fields[4],
            "home_directory": fields[5],
            "shell": fields[6]
        }

        return user_dict
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None



def get_all_users(scope="all"):
    all_users = []
    logger.debug(f"Fetching {scope} users")

    try:
        with open("/etc/passwd", "r") as passwd_file:
            for line in passwd_file:
                if line.strip():
                    user_info = parse_passwd_line(line)
                    if user_info is None:
                        continue

                    try:
                        password_info = get_password_info(user_info["username"])
                        user_info.update(password_info)
                    except GlobalHTTPException:
                        logger.warning(f"Skipping {user_info['username']} due to password info error")

                    if scope == "active":
                        if user_info["home_directory"] and user_info["shell"] in ["/bin/bash"]:
                            all_users.append(user_info)
                    else:
                        all_users.append(user_info)

    except FileNotFoundError:
        logger.error("passwd file not found")
        raise GlobalHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            title="passwd file missing",
            detail="The /etc/passwd file is missing",
            code="PASSWD_FILE_NOT_FOUND"
        )
    except PermissionError:
        logger.error("Permission error reading passwd file")
        raise GlobalHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission Denied",
            detail="Permission issue reading /etc/passwd",
            code="PASSWD_FILE_PERMISSION_DENIED"
        )
    except Exception as e:
        logger.exception(f"Error reading passwd file: {e}")
        raise GlobalHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail="An error occurred while processing user data",
            code="UNEXPECTED_ERROR"
        )

    return all_users
