from pydantic import BaseModel, Field

from app.schemas.roles import SearchTemplateOut


class WizardStepOut(BaseModel):
    key: str
    title: str
    description: str
    status: str
    href: str


class WizardSummaryOut(BaseModel):
    profile_ready: bool
    resume_ready: bool
    inbox_ready: bool
    role_count: int
    job_count: int
    tailored_resume_count: int
    steps: list[WizardStepOut] = Field(default_factory=list)
    recommended_templates: list[SearchTemplateOut] = Field(default_factory=list)
    blocked_domains: list[str] = Field(default_factory=list)


class WizardBootstrapRequest(BaseModel):
    template_key: str
