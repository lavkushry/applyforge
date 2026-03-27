from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import InboxConnection, User
from app.schemas.inbox import InboxConnectionCreate, InboxConnectionOut, InboxOtpEventOut, InboxOtpRequest
from app.services.inbox import create_inbox_connection, extract_otp, record_otp_event

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/connections", response_model=list[InboxConnectionOut])
def list_connections(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[InboxConnection]:
    return (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user.id)
        .order_by(InboxConnection.updated_at.desc())
        .all()
    )


@router.post("/gmail/connect", response_model=InboxConnectionOut)
def connect_gmail(payload: InboxConnectionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InboxConnection:
    if payload.provider != "gmail":
        raise HTTPException(status_code=400, detail="Provider mismatch")
    return create_inbox_connection(db, user.id, payload.provider, payload.email, payload.token, payload.scopes)


@router.post("/outlook/connect", response_model=InboxConnectionOut)
def connect_outlook(payload: InboxConnectionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InboxConnection:
    if payload.provider != "outlook":
        raise HTTPException(status_code=400, detail="Provider mismatch")
    return create_inbox_connection(db, user.id, payload.provider, payload.email, payload.token, payload.scopes)


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
    db.commit()
    return {"message": "Inbox connection disconnected"}


@router.post("/request-otp")
def request_otp(payload: InboxOtpRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    connection = (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user.id, InboxConnection.status == "connected")
        .order_by(InboxConnection.updated_at.desc())
        .first()
    )
    if not connection:
        raise HTTPException(status_code=400, detail="Connect an inbox first")
    result = extract_otp(payload.messages, payload.sender_hint, payload.subject_hint)
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
        "event": InboxOtpEventOut.model_validate(event).model_dump(mode="json"),
    }
