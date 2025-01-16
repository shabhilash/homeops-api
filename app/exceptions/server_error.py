from fastapi import HTTPException


class DiskUsageError(HTTPException):
    """Base class for Logger-related HTTP exceptions."""
    def __init__(self, status_code: int, detail: any, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class DiskCommandNotFoundError(DiskUsageError):
    """
    Exception raised when the 'df' command is not found on the system.

    Attributes:
        status_code (int): HTTP status code for the error (501).
        detail (str): Error message.
        code (str): Unique error code ('DISK_COMMAND_NOT_FOUND_001').
    """

    def __init__(self):
        super().__init__(status_code=501, detail="The 'df' command is not available on this system", code="DISK_COMMAND_NOT_FOUND_001")


class DiskUsageFetchError(DiskUsageError):
    """
    Exception raised when there is an error fetching disk usage information.

    Attributes:
        status_code (int): HTTP status code for the error (500).
        detail (str): Error message.
        code (str): Unique error code ('DISK_USAGE_FETCH_ERROR_001').
    """

    def __init__(self):
        super().__init__(status_code=500, detail="Failed to fetch disk usage using the 'df' command", code="DISK_USAGE_FETCH_ERROR_001")


class DiskUsageSubprocessError(DiskUsageError):
    """
    Exception raised when a subprocess error occurs while running the 'df' command.

    Attributes:
        status_code (int): HTTP status code for the error (500).
        detail (str): Error message.
        code (str): Unique error code ('DISK_USAGE_SUBPROCESS_ERROR_001').
    """

    def __init__(self, message: str):
        super().__init__(status_code=500, detail=f"Subprocess error: {message}", code="DISK_USAGE_SUBPROCESS_ERROR_001")


class DiskUsageFileNotFoundError(DiskUsageError):
    """
    Exception raised when a required file is not found.

    Attributes:
        status_code (int): HTTP status code for the error (404).
        detail (str): Error message.
        code (str): Unique error code ('DISK_USAGE_FILE_NOT_FOUND_001').
    """

    def __init__(self, message: str):
        super().__init__(status_code=404, detail=f"File not found: {message}", code="DISK_USAGE_FILE_NOT_FOUND_001")