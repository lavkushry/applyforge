from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.schemas.common import OrmModel


class LinkItem(BaseModel):
    label: str
    url: str


class ExperienceItem(BaseModel):
    title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str = ""
    highlights: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: str = ""
    degree: str = ""


class CertificationItem(BaseModel):
    name: str = ""
    issuer: str = ""


class CandidateBasics(BaseModel):
    full_name: str = ""
    headline: str = ""
    email: EmailStr | None = None
    phone: str = ""
    location: str = ""
    target_role: str = ""
    preferred_locations: list[str] = Field(default_factory=list)


class CandidateProfileIn(BaseModel):
    basics: CandidateBasics = Field(default_factory=CandidateBasics)
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certifications: list[CertificationItem] = Field(default_factory=list)
    links: list[LinkItem] = Field(default_factory=list)
    preferences: dict = Field(default_factory=dict)
    saved_answers: dict = Field(default_factory=dict)
    fact_locked: bool = True


class CandidateProfileOut(CandidateProfileIn, OrmModel):
    id: int
    user_id: int


class ResumeUploadResponse(BaseModel):
    file_id: int
    path: str
    checksum: str


class ResumeParseResponse(BaseModel):
    parsed: CandidateProfileIn


class ProfileSettingsUpdate(BaseModel):
    values: dict = Field(default_factory=dict)
