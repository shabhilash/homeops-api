from pydantic import BaseModel


class ResponseRootModel(BaseModel):
    status: str
    version: str
    metadata: dict