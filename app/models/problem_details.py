from pydantic import BaseModel
from typing import Optional

class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    code: str
