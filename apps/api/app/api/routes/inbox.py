from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db
from app.models.entities import InboxConnection, User
from app.schemas.inbox import (
    InboxConnectionCreate,
    InboxConnectionOut,
    InboxOAuthProviderOut,
    InboxOtpEventOut,
    InboxOtpRequest,
)
from app.services.inbox import (
    build_oauth_authorization_url,
    complete_oauth_connection,
    create_inbox_connection,
    extract_otp,
    fetch_inbox_messages,
    get_oauth_provider_status,
    list_oauth_provider_statuses,
    record_otp_event,
    sanitize_connection_metadata,
)

router = APIRouter(prefix="/inbox", tags=["inbox"])


def _serialize_connection(connection: InboxConnection) -> InboxConnectionOut:
    payload = InboxConnectionOut.model_validate(connection).model_dump(mode="json")
    payload["metadata_json"] = sanitize_connection_metadata(connection.metadata_json)
    return InboxConnectionOut.model_validate(payload)


def _callback_redirect(return_to: str, provider: str, status: str, message: str = "") -> RedirectResponse:
    query = {"inbox_status": status, "provider": provider}
    if message:
        query["message"] = message
    location = f"{settings.web_origin.rstrip('/')}{return_to}?{urlencode(query)}"
    return RedirectResponse(url=location, status_code=302)


@router.get("/oauth/providers", response_model=list[InboxOAuthProviderOut])
def oauth_provider_statuses(user: User = Depends(get_current_user)) -> list[InboxOAuthProviderOut]:
    return [InboxOAuthProviderOut.model_validate(item) for item in list_oauth_provider_statuses()]


@router.get("/oauth/providers/{provider}", response_model=InboxOAuthProviderOut)
def oauth_provider_status(provider: str, user: User = Depends(get_current_user)) -> InboxOAuthProviderOut:
    try:
        return InboxOAuthProviderOut.model_validate(get_oauth_provider_status(provider))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{provider}/oauth/start")
def oauth_start(
    provider: str,
    return_to: str = "/settings",
    user: User = Depends(get_current_user),
    request: Request = None,
) -> dict:
    enforce_rate_limit(
        bucket=f"inbox.oauth_start.{provider}",
        request=request,
        limit=10,
        window_seconds=300,
        subject_suffix=str(user.id),
    )
    try:
        return build_oauth_authorization_url(provider, user.id, return_to)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/{provider}/oauth/callback")
def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if error:
        return _callback_redirect("/settings", provider, "error", error_description or error)
    if not code or not state:
        return _callback_redirect("/settings", provider, "error", "Missing OAuth callback parameters")
    try:
        _, return_to = complete_oauth_connection(db, provider, code, state)
    except ValueError as exc:
        return _callback_redirect("/settings", provider, "error", str(exc))
    except Exception as exc:
        return _callback_redirect("/settings", provider, "error", f"OAuth exchange failed: {exc}")
    return _callback_redirect(return_to, provider, "connected")


@router.get("/connections", response_model=list[InboxConnectionOut])
def list_connections(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[InboxConnectionOut]:
    connections = (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user.id)
        .order_by(InboxConnection.updated_at.desc())
        .all()
    )
    return [_serialize_connection(connection) for connection in connections]


@router.post("/gmail/connect", response_model=InboxConnectionOut)
def connect_gmail(
    payload: InboxConnectionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
) -> InboxConnectionOut:
    enforce_rate_limit(
        bucket="inbox.manual_connect.gmail",
        request=request,
        limit=5,
        window_seconds=300,
        subject_suffix=payload.email,
    )
    if payload.provider != "gmail":
        raise HTTPException(status_code=400, detail="Provider mismatch")
    return _serialize_connection(create_inbox_connection(db, user.id, payload.provider, payload.email, payload.token, payload.scopes))


@router.post("/outlook/connect", response_model=InboxConnectionOut)
def connect_outlook(
    payload: InboxConnectionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
) -> InboxConnectionOut:
    enforce_rate_limit(
        bucket="inbox.manual_connect.outlook",
        request=request,
        limit=5,
        window_seconds=300,
        subject_suffix=payload.email,
    )
    if payload.provider != "outlook":
        raise HTTPException(status_code=400, detail="Provider mismatch")
    return _serialize_connection(create_inbox_connection(db, user.id, payload.provider, payload.email, payload.token, payload.scopes))


@router.delete("/connections/{connection_id}")
def disconnect_connection(connection_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    connection = (
        db.query(InboxConnection)
        .filter(InboxConnection.id == connection_id, InboxConnection.user_id == user.id)
        .first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Inbox connection not found")
    connection.status = "disconnected"
    connection.metadata_json = {**sanitize_connection_metadata(connection.metadata_json), "oauth_connected": False, "token_present": False}
    db.commit()
    return {"message": "Inbox connection disconnected"}


@router.post("/request-otp")
def request_otp(
    payload: InboxOtpRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
) -> dict:
    enforce_rate_limit(
        bucket="inbox.request_otp",
        request=request,
        limit=12,
        window_seconds=300,
        subject_suffix=str(user.id),
    )
    connection = (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user.id, InboxConnection.status == "connected")
        .order_by(InboxConnection.updated_at.desc())
        .first()
    )
    if not connection:
        raise HTTPException(status_code=400, detail="Connect an inbox first")
    try:
        messages = payload.messages or fetch_inbox_messages(db, connection, payload.sender_hint, payload.subject_hint)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch inbox messages: {exc}") from exc
    result = extract_otp(messages, payload.sender_hint, payload.subject_hint)
    event = record_otp_event(
        db,
        connection_id=connection.id,
        run_id=payload.run_id,
        status=result["status"],
        sender=result["sender"],
        subject=result["subject"],
        code_last4=result["code_last4"],
        error_message="" if result["status"] == "resolved" else "OTP requires manual review",
    )
    return {
        "status": result["status"],
        "code": result["code"] if result["status"] == "resolved" else "",
        "masked_code": f"***{result['code_last4']}" if result["code_last4"] else "",
        "confidence": result["confidence"],
        "message_count": len(messages),
        "provider": connection.provider,
        "event": InboxOtpEventOut.model_validate(event).model_dump(mode="json"),
    }
