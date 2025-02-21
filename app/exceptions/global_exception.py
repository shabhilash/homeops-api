from fastapi import HTTPException


class GlobalHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: any, code: str, title: any = "Error Occurred", headers: dict = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code
        self.title = title