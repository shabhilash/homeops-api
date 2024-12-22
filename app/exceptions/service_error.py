from fastapi import HTTPException


class ServiceError(HTTPException):
    """Base class for service-related HTTP exceptions."""
    def __init__(self, status_code: int, detail: any, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class ServiceNotFound(ServiceError):
    """Exception raised when the service is not found."""
    def __init__(self):
        super().__init__(status_code=404, detail="Service not found", code="SERVICE_NOT_FOUND_001")


class PermissionDenied(ServiceError):
    """Exception raised when permission is denied."""
    def __init__(self):
        super().__init__(status_code=403, detail="Permission denied", code="PERMISSION_DENIED_002")


class InvalidArgument(ServiceError):
    """Exception raised for invalid arguments."""
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid argument", code="INVALID_ARGUMENT_001")


class RequestTimeout(ServiceError):
    """Exception raised when a request times out."""
    def __init__(self):
        super().__init__(status_code=408, detail="Request timeout", code="REQUEST_TIMEOUT_001")


class FailedDependency(ServiceError):
    """Exception raised when a dependency fails."""
    def __init__(self):
        super().__init__(status_code=424, detail="Failed dependency", code="FAILED_DEPENDENCY_001")


class ConflictError(ServiceError):
    """Exception raised for conflicts."""
    def __init__(self, detail="Conflict error"):
        super().__init__(status_code=409, detail=detail, code="CONFLICT_ERROR_001")


class MethodNotAllowed(ServiceError):
    """Exception raised for disallowed methods."""
    def __init__(self):
        super().__init__(status_code=405, detail="Method not allowed", code="METHOD_NOT_ALLOWED_001")


class InternalServerError(ServiceError):
    """Exception raised for internal server errors."""
    def __init__(self):
        super().__init__(status_code=500, detail="Internal server error", code="INTERNAL_SERVER_ERROR_001")


class OSNotSupported(ServiceError):
    """Exception raised when the operating system is not supported."""
    def __init__(self):
        super().__init__(status_code=400, detail="Operating system not supported. Only Linux is supported.", code="OS_NOT_SUPPORTED_001")


class SudoDisabled(ServiceError):
    """Exception raised when sudo is disabled on the machine."""
    def __init__(self):
        super().__init__(status_code=403, detail="Sudo is disabled", code="SUDO_DISABLED_001")