from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str
    company: str
    location: str = ''
    remote_type: str = 'unknown'
    salary: str = ''
    source: str = 'manual'
    application_url: str = ''
    description: str
    seniority: str = ''
    employment_type: str = ''
    tags: list[str] = Field(default_factory=list)


class JobScoreResponse(BaseModel):
    overall_score: float
    missing_skills: list[str]
    strengths: list[str]
    reasons: list[str]
    recommendation: str
