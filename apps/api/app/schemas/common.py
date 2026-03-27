from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(OrmModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    timestamp: datetime
