from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import OrmModel

AutomationMode = Literal["draft", "assisted", "auto"]


class ApplicationOut(OrmModel):
    id: int
    user_id: int
    job_id: int
    status: str
    notes: str
    latest_run_id: int | None
    created_at: datetime


class ApplicationStepOut(OrmModel):
    id: int
    run_id: int
    name: str
    status: str
    step_kind: str
    requires_approval: bool
    screenshot_file_id: int | None
    output: dict
    masked_output: dict
    retry_count: int
    started_at: datetime
    completed_at: datetime | None


class ApplicationRunOut(OrmModel):
    id: int
    application_id: int
    role_id: int | None
    mode: str
    status: str
    current_step: str
    external_task_id: str
    error_message: str
    policy_snapshot: dict
    started_at: datetime
    finished_at: datetime | None


class ApplicationPacketSummary(BaseModel):
    ready: bool
    auto_submit_allowed: bool
    resume_file_id: int | None
    cover_letter_id: int | None
    upload_ready: bool
    missing_answers: list[str]
    risk_summary: list[str]
    blocking_issues: list[str]
    auto_policy_reasons: list[str]
    answer_provenance: dict[str, str]
    answer_keys: list[str]


class ApplicationPrepareResponse(BaseModel):
    application: ApplicationOut
    packet: ApplicationPacketSummary


class ApplicationRunDetail(BaseModel):
    run: ApplicationRunOut
    steps: list[ApplicationStepOut]


class ExportResumePdfRequest(BaseModel):
    resume_version_id: int


class RunModeRequest(BaseModel):
    mode: AutomationMode = "assisted"
    answers: dict = Field(default_factory=dict)
