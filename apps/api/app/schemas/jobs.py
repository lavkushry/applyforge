from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    company: str = Field(min_length=2, max_length=255)
    company_id: int | None = None
    role_id: int | None = None
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
    source_metadata: dict
    enrichment_status: str
    enrichment_error: str
    enrichment_metadata: dict
    enrichment_revision: int
    source_document_file_id: int | None
    latest_score: float
    latest_score_revision: int
    latest_recommendation: str
    last_scored_at: datetime | None
    first_seen_at: datetime
    last_seen_at: datetime
    expired_at: datetime | None
    active: bool
    dedupe_key: str
    created_at: datetime


class JobScoreRequest(BaseModel):
    role_id: int | None = None


class JobScoreResponse(OrmModel):
    id: int
    job_id: int
    role_id: int | None
    enrichment_revision: int
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
    theme_id: int | None
    title: str
    variant: str
    theme_variant: str
    ats_mode: bool
    content_json: dict
    diff_metadata: dict
    export_status: str
    pdf_file_id: int | None
    created_at: datetime


class ResumeTailorRequest(BaseModel):
    role_id: int | None = None
    theme_id: int | None = None
    ats_mode: bool = True


class ResumeThemeOut(OrmModel):
    id: int
    slug: str
    label: str
    description: str
    accent_color: str
    layout_mode: str
    is_ats_safe: bool
    metadata_json: dict
    active: bool
    created_at: datetime
    updated_at: datetime


class ResumePreviewResponse(BaseModel):
    theme: ResumeThemeOut
    blocks: list[dict]


class CoverLetterResponse(OrmModel):
    id: int
    job_id: int
    content: str
    tone: str
    created_at: datetime
