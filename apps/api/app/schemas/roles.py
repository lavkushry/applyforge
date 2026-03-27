from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class TargetRoleSourceIn(BaseModel):
    kind: str = Field(default="manual", min_length=2, max_length=60)
    label: str = Field(default="", max_length=120)
    base_url: str = Field(default="", max_length=500)
    config: dict = Field(default_factory=dict)
    enabled: bool = True


class TargetRoleIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    aliases: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: str = "remote"
    salary_target: str = ""
    visa_preference: str = "unknown"
    seniority: str = "mid"
    companies_include: list[str] = Field(default_factory=list)
    companies_exclude: list[str] = Field(default_factory=list)
    scrape_cadence_minutes: int = Field(default=30, ge=5, le=1440)
    automation_enabled: bool = False
    min_auto_apply_score: float = Field(default=85.0, ge=0.0, le=100.0)
    active: bool = True
    sources: list[TargetRoleSourceIn] = Field(default_factory=list)


class TargetRoleSourceOut(TargetRoleSourceIn, OrmModel):
    id: int
    role_id: int
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TargetRoleOut(OrmModel):
    id: int
    user_id: int
    name: str
    aliases: list[str]
    keywords: list[str]
    preferred_locations: list[str]
    remote_preference: str
    salary_target: str
    visa_preference: str
    seniority: str
    companies_include: list[str]
    companies_exclude: list[str]
    scrape_cadence_minutes: int
    automation_enabled: bool
    min_auto_apply_score: float
    active: bool
    created_at: datetime
    updated_at: datetime
    sources: list[TargetRoleSourceOut] = Field(default_factory=list)


class JobIngestionRunOut(OrmModel):
    id: int
    role_id: int
    status: str
    source_count: int
    discovered_count: int
    inserted_count: int
    updated_count: int
    error_message: str
    started_at: datetime
    finished_at: datetime | None
