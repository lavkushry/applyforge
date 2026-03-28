from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import enforce_rate_limit
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.entities import User
from app.schemas.auth import LoginRequest, RegisterRequest, SessionUser, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_auth_response(response: Response, user: User) -> TokenResponse:
    token = create_access_token(str(user.id))
    response.set_cookie(
        key=settings.access_cookie_name,
        value=token,
        httponly=True,
        secure=settings.access_cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return TokenResponse(access_token=token, user=SessionUser.model_validate(user))


@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest,
    response: Response,
    request: Request | None = None,
    db: Session = Depends(get_db),
) -> TokenResponse:
    enforce_rate_limit(
        bucket="auth.register",
        request=request,
        limit=5,
        window_seconds=300,
        subject_suffix=payload.email,
    )
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _build_auth_response(response, user)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    request: Request | None = None,
    db: Session = Depends(get_db),
) -> TokenResponse:
    enforce_rate_limit(
        bucket="auth.login",
        request=request,
        limit=8,
        window_seconds=300,
        subject_suffix=payload.email,
    )
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _build_auth_response(response, user)


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(key=settings.access_cookie_name)
    return {"message": "Logged out"}


@router.get("/me", response_model=SessionUser)
def me(user: User = Depends(get_current_user)) -> SessionUser:
    return SessionUser.model_validate(user)
