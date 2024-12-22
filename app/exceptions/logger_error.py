from fastapi import HTTPException

class LoggerError(HTTPException):
    """Base class for Logger-related HTTP exceptions."""
    def __init__(self, status_code: int, detail: any, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class InvalidLogLevel(LoggerError):
    """
    Exception raised when the log level provided is invalid.

    Attributes:
        status_code (int): HTTP status code for the error (400).
        detail (str): Error message.
        code (str): Unique error code ('INVALID_LOG_LEVEL_001').
    """
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid log level", code="INVALID_LOG_LEVEL_001")

class LoggerNotFound(LoggerError):
    """
    Exception raised when the logger name is not found in the logging manager.

    Attributes:
        status_code (int): HTTP status code for the error (404).
        detail (str): Error message.
        code (str): Unique error code ('LOGGER_NOT_FOUND_001').
    """
    def __init__(self):
        super().__init__(status_code=404, detail="Logger not found", code="LOGGER_NOT_FOUND_001")

class ConfigFileNotFound(LoggerError):
    """
    Exception raised when the configuration file is not found.

    Attributes:
        status_code (int): HTTP status code for the error (404).
        detail (str): Error message.
        code (str): Unique error code ('CONFIG_FILE_NOT_FOUND_001').
    """
    def __init__(self):
        super().__init__(status_code=404, detail="Configuration file not found", code="CONFIG_FILE_NOT_FOUND_001")

class LoggerNotInConfig(LoggerError):
    """
    Exception raised when the logger is not found in the YAML config file.

    Attributes:
        status_code (int): HTTP status code for the error (200, with warning).
        detail (dict): Warning message with additional action.
        code (str): Unique error code ('LOGGER_NOT_IN_CONFIG_001').
    """
    def __init__(self, logger_name: str):
        super().__init__(status_code=200, detail={"status": "warning","message": f"'{logger_name}' - Logger level updated, but the logger was not found in the config file","action": "Verify if the logger is available in the settings.yaml"}, code="LOGGER_NOT_IN_CONFIG_001")

class LoggerUpdateError(LoggerError):
    """
    Exception raised when there is a failure updating the logger configuration.

    Attributes:
        status_code (int): HTTP status code for the error (500).
        detail (str): Error message.
        code (str): Unique error code ('LOGGER_UPDATE_ERROR_001').
    """
    def __init__(self):
        super().__init__(status_code=500, detail="Error updating logger configuration", code="LOGGER_UPDATE_ERROR_001")