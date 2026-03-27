from pydantic import BaseModel


class RunRequest(BaseModel):
    mode: str


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    notes: str
