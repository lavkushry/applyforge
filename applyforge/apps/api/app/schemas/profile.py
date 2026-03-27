from pydantic import BaseModel, Field


class CandidateProfileIn(BaseModel):
    basics: dict = Field(default_factory=dict)
    summary: str = ''
    skills: list[str] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    education: list[dict] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)
    links: list[dict] = Field(default_factory=list)
    fact_locked: bool = True


class CandidateProfileOut(CandidateProfileIn):
    id: int
    user_id: int
