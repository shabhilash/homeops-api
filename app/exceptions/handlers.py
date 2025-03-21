from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

from app.exceptions.global_exception import GlobalHTTPException
from app.models.problem_details import ProblemDetails


async def general_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc, GlobalHTTPException):
        title = exc.title
        code = exc.code
    else:
        title = "Unknown Error Occurred"
        code = "UNEXPECTED_ERROR"

    problem_details = ProblemDetails(
            type="/codes",
            title=title,
            status=exc.status_code,
            detail=str(exc.detail),
            instance=str(request.url),
            code=code
    )

    return JSONResponse(
            status_code=exc.status_code,
            content=problem_details.model_dump()
    )