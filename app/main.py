from app.database import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.endpoints.config import config_router
from app.endpoints.users import users_router
from app.exceptions.handlers import general_exception_handler
from app.models.root_response import ResponseRootModel
from app.utils.db.config import get_config_value
from app.utils.errors.load_errors import error_codes

error_code_count = len(error_codes)

API_DESCRIPTION = f"""

## 🎯 Features
- ⚙️ **Configuration Management**: Modify system, network, and automation settings.
- 📊 **System Monitoring**: View system logs, diagnostics, and health reports.
- ⚡ **Automation**: Create and schedule automated tasks.
- 🔐 **Security & Access Control**: Manage users, authentication, and permissions.
- 🌐 **Network Management**: Configure and monitor network settings.
- 💾 **Storage & Logs**: Manage disk usage and retrieve system logs.

## 📘 Documentation
Refer to the [API schema](/openapi.json) for endpoint details.  
For error handling, visit the [Error Codes ({error_code_count})](/errors) page.
"""

OPENAPI_TAGS = [
    {"name": "system", "description": "Check system status, uptime, and API health."},
    {"name": "config", "description": "Manage system and network configurations."},
    {"name": "monitoring", "description": "Monitor system performance, logs, and diagnostics."},
    {"name": "automation", "description": "Schedule and manage automated tasks."},
    {"name": "security", "description": "Manage authentication, authorization, and security policies."},
    {"name": "services", "description": "Manage systemctl services."},
    {"name": "network", "description": "View and configure network settings and status."},
    {"name": "storage", "description": "Manage storage, disk usage, and related resources."},
    {"name": "users", "description": "Handle user authentication and access control."},
    {"name": "logs", "description": "Retrieve and analyze system logs."},
    {"name": "web", "description": "Endpoints serving the web-based UI."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Context manager for application lifespan.
    Ensures proper cleanup of resources such as database connections.
    """
    yield  # Yield control to the application startup
    engine.dispose()

app = FastAPI(
    title="HomeOps API",
    summary="HomeOpsAPI provides a powerful and efficient interface for managing homelab environments.",
    version="0.1.6-beta",
    description=API_DESCRIPTION,
    contact={"name": "HomeOps Team", "email": "homeops-api@googlegroups.com"},
    license_info={"name": "Apache 2.0", "identifier": "Apache-2.0"},
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan
)


@app.exception_handler(HTTPException)
async def general_error_handler(request: Request, exc: HTTPException):
    """
    Handles HTTP exceptions raised in the application.
    """
    return await general_exception_handler(request, exc)

@app.get(
    "/",
    response_description="API Status OK",
    status_code=status.HTTP_200_OK,
    response_model=ResponseRootModel,
    tags=["system"],
    summary="Get API Status",
    description="Returns the current API status, version, and metadata."
)
def get_root():
    return ResponseRootModel(
        status="ok",
        version=app.version,
        metadata={
            "environment": get_config_value("ENVIRONMENT"),
            "rate_limit": f"{get_config_value('REQUEST_LIMIT')} Req / {get_config_value('TIME_WINDOW')} Sec"
        }
    )


app.include_router(config_router, tags=["config"])
app.include_router(users_router, tags=["users"])

# WEB UI
templates = Jinja2Templates(directory="pages")


@app.get(
        "/errors",
        response_class=HTMLResponse,
        tags=["web"],
        include_in_schema=False,
        summary="Error Codes Page",
        description="Displays an HTML page with error codes."
)
async def error_codes_page(request: Request):
    if not error_codes:
        return HTMLResponse(content="<h2>No error codes available.</h2>", status_code=404)

    return templates.TemplateResponse(
            "errors.html", {"request": request, "error_codes": error_codes}
    )

