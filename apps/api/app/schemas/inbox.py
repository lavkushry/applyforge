from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import OrmModel


class InboxConnectionCreate(BaseModel):
    provider: str = Field(pattern="^(gmail|outlook)$")
    email: EmailStr
    token: str = Field(min_length=8)
    scopes: list[str] = Field(default_factory=list)


class InboxConnectionOut(OrmModel):
    id: int
    user_id: int
    provider: str
    email: str
    status: str
    scopes: list[str]
    token_masked: str
    metadata_json: dict
    created_at: datetime
    updated_at: datetime


class InboxOAuthProviderOut(BaseModel):
    provider: str
    configured: bool
    authorization_enabled: bool
    redirect_uri: str
    scopes: list[str]
    required_env: list[str]
    missing_env: list[str]


class InboxOtpRequest(BaseModel):
    run_id: int | None = None
    sender_hint: str = ""
    subject_hint: str = ""
    messages: list[dict] = Field(default_factory=list)


class InboxOtpEventOut(OrmModel):
    id: int
    connection_id: int
    run_id: int | None
    status: str
    sender: str
    subject_masked: str
    code_last4: str
    error_message: str
    created_at: datetime
