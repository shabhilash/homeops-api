from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.initial_db_setup import load_default_configs
from app.core.auth import require_role
from app.utils.db.config import get_config_value
from app.utils.db.init import get_db
from app.core.rate_limiter import RateLimiter

config_router = APIRouter(prefix="/config",
                          dependencies=[Depends(RateLimiter(requests_limit=int(get_config_value("REQUEST_LIMIT")),
                                                            time_window=int(get_config_value("TIME_WINDOW")))),Depends(require_role("admin"))])


@config_router.post("/reset")
async def post_load_default_config(db: Session = Depends(get_db)):
    try:
        load_default_configs(db)
        return {"message": "Default configurations loaded successfully."}
    except Exception as e:
        return {"error": str(e)}