from fastapi.responses import JSONResponse
from fastapi import Request

from app.exceptions.exceptions import *
from app.models.problem_details import ProblemDetails


# Custom exception handler for Invalid Username Error
async def invalid_username_exception_handler(request: Request, exc: UserNotFoundError):
    problem_details = ProblemDetails(
        type="https://example.com/errors",
        title="Invalid Username",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),
        code=exc.code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details.model_dump()
    )

# Custom exception handler for Invalid Password Error
async def invalid_password_exception_handler(request: Request, exc: InvalidPasswordError) -> JSONResponse:
    problem_details = ProblemDetails(
        type="https://example.com/errors",
        title="Invalid Password",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),
        code=exc.code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details.model_dump()
    )

# Custom exception handler for Invalid Password Error
async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError)-> JSONResponse:
    problem_details = ProblemDetails(
        type="https://example.com/errors",
        title="Permission Denied",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),code=exc.code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details.model_dump()
    )

async def invalid_token_exception_handler(request: Request, exc: InvalidTokenError)-> JSONResponse:
    problem_details = ProblemDetails(
        type="https://example.com/errors",
        title="Invalid Token",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),code=exc.code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details.model_dump()
    )

async def general_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if hasattr(exc, 'code'):
        code = exc.code
    else:
        code = "UNKNOWN_ERROR"  # Default value if code doesn't exist

    problem_details = ProblemDetails(
        type="https://example.com/errors",
        title=exc.detail,
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),
        code=code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem_details.dict()  # Convert to dictionary
    )
