from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import OrmModel


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SessionUser(OrmModel):
    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    user: SessionUser
