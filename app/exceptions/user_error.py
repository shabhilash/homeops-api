from fastapi import HTTPException


class UserError(HTTPException):
    """Base class for User-Action-related HTTP exceptions."""
    def __init__(self, status_code: int, detail: any, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class UsernameExistsError(UserError):
    """
    Exception raised when the Username exists.
    """
    def __init__(self):
        super().__init__(status_code=409, detail="Username Taken", code="USERNAME_EXISTS_001")