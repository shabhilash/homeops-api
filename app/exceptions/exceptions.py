from fastapi import HTTPException, status

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: any, code: str, headers: dict = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code

class InvalidPasswordError(HTTPException):
    def __init__(self, detail: any = "Invalid password", code: str = "INVALID_CREDENTIALS_001"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        self.code = code

class UserNotFoundError(HTTPException):
    def __init__(self, detail: any = "User not found", code: str = "INVALID_USER_001"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        self.code = code

class PermissionDeniedError(HTTPException):
    def __init__(self, detail: any = "Forbidden Access",code: str = "PERMISSION_DENIED_001"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        self.code = code

class InvalidTokenError(HTTPException):
    def __init__(self, detail: str = "Invalid token", code: str = "INVALID_TOKEN_001"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        self.code = code
