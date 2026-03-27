import re

from sqlalchemy.orm import Session

from app.models.entities import InboxConnection, InboxOtpEvent

OTP_PATTERN = re.compile(r"\b(\d{4,8})\b")


def mask_token(token: str) -> str:
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}{'*' * max(4, len(token) - 8)}{token[-4:]}"


def mask_subject(subject: str) -> str:
    if len(subject) <= 12:
        return subject[:2] + "*" * max(0, len(subject) - 2)
    return f"{subject[:4]}***{subject[-4:]}"


def extract_otp(messages: list[dict], sender_hint: str = "", subject_hint: str = "") -> dict:
    sender_hint = sender_hint.lower().strip()
    subject_hint = subject_hint.lower().strip()
    ranked_messages = sorted(
        messages,
        key=lambda message: (
            0 if sender_hint and sender_hint in str(message.get("sender", "")).lower() else 1,
            0 if subject_hint and subject_hint in str(message.get("subject", "")).lower() else 1,
        ),
    )
    for message in ranked_messages:
        body = str(message.get("body", ""))
        match = OTP_PATTERN.search(body)
        if match:
            code = match.group(1)
            return {
                "status": "resolved",
                "sender": str(message.get("sender", "")),
                "subject": str(message.get("subject", "")),
                "code": code,
                "code_last4": code[-4:],
                "confidence": "high",
            }
    return {
        "status": "manual_review_required",
        "sender": sender_hint,
        "subject": subject_hint,
        "code": "",
        "code_last4": "",
        "confidence": "low",
    }


def create_inbox_connection(db: Session, user_id: int, provider: str, email: str, token: str, scopes: list[str]) -> InboxConnection:
    existing = (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user_id, InboxConnection.provider == provider, InboxConnection.email == email)
        .first()
    )
    if existing:
        existing.status = "connected"
        existing.scopes = scopes
        existing.token_masked = mask_token(token)
        existing.metadata_json = {"oauth_connected": True}
        db.commit()
        db.refresh(existing)
        return existing
    row = InboxConnection(
        user_id=user_id,
        provider=provider,
        email=email,
        status="connected",
        scopes=scopes,
        token_masked=mask_token(token),
        metadata_json={"oauth_connected": True},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def record_otp_event(
    db: Session,
    connection_id: int,
    run_id: int | None,
    status: str,
    sender: str,
    subject: str,
    code_last4: str,
    error_message: str = "",
) -> InboxOtpEvent:
    row = InboxOtpEvent(
        connection_id=connection_id,
        run_id=run_id,
        status=status,
        sender=sender,
        subject_masked=mask_subject(subject),
        code_last4=code_last4,
        error_message=error_message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
