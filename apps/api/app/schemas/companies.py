from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Message, OrmModel


class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    website_url: str = Field(default="", max_length=500)
    careers_url: str = Field(default="", max_length=500)
    linkedin_url: str = Field(default="", max_length=500)
    hq_location: str = Field(default="", max_length=255)
    industry: str = Field(default="", max_length=120)
    notes: str = ""
    active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyPortalCreate(BaseModel):
    provider_kind: str = Field(default="direct_site", min_length=2, max_length=60)
    base_url: str = Field(default="", max_length=500)
    board_token: str = Field(default="", max_length=255)
    health_status: str = Field(default="unknown", max_length=40)
    supports_structured_fetch: bool = False
    last_checked_at: datetime | None = None
    notes: str = ""


class CompanyContactCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    title: str = Field(default="", max_length=255)
    email: str = Field(default="", max_length=255)
    linkedin_url: str = Field(default="", max_length=500)
    contact_type: str = Field(default="recruiter", max_length=40)
    source: str = Field(default="manual", max_length=120)
    source_url: str = Field(default="", max_length=500)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    last_verified_at: datetime | None = None
    notes: str = ""


class CompanyPortalOut(CompanyPortalCreate, OrmModel):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime


class CompanyContactOut(CompanyContactCreate, OrmModel):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime


class CompanyOut(CompanyBase, OrmModel):
    id: int
    user_id: int
    normalized_name: str
    created_at: datetime
    updated_at: datetime


class CompanyDetailOut(CompanyOut):
    portals: list[CompanyPortalOut] = Field(default_factory=list)
    contacts: list[CompanyContactOut] = Field(default_factory=list)


CompanyDeleteResponse = Message
