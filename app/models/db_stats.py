from pydantic import BaseModel


class DbStats(BaseModel):
    user_count:int