from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import OrmModel


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    company: str = Field(min_length=2, max_length=255)
    location: str = ""
    remote_type: str = "unknown"
    salary: str = ""
    source: str = "manual"
    application_url: str = ""
    description: str = Field(min_length=20)
    seniority: str = ""
    employment_type: str = ""
    visa_support: str = "unknown"
    tags: list[str] = Field(default_factory=list)


class JobOut(JobCreate, OrmModel):
    id: int
    user_id: int
    normalized_description: dict
    stack_tags: list[str]
    domain_tags: list[str]
    dedupe_key: str
    created_at: datetime


class JobScoreResponse(OrmModel):
    id: int
    job_id: int
    overall_score: float
    score_breakdown: dict
    missing_skills: list[str]
    strengths: list[str]
    reasons: list[str]
    recommendation: str
    created_at: datetime


class ResumeVersionResponse(OrmModel):
    id: int
    resume_id: int
    job_id: int | None
    title: str
    variant: str
    content_json: dict
    pdf_file_id: int | None
    created_at: datetime


class CoverLetterResponse(OrmModel):
    id: int
    job_id: int
    content: str
    tone: str
    created_at: datetime
