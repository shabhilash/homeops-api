from pydantic import BaseModel

# Define a model for the request body
class LogLevel(BaseModel):
    logger_name: str
    level: str
