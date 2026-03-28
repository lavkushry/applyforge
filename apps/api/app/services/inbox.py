import base64
import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import InboxConnection, InboxOtpEvent

OTP_PATTERN = re.compile(r"\b(\d{4,8})\b")
MAX_PROVIDER_MESSAGES = 10
OAUTH_STATE_ALGORITHM = "HS256"
GOOGLE_OAUTH_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]
OUTLOOK_OAUTH_SCOPES = [
    "openid",
    "profile",
    "email",
    "offline_access",
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Mail.Read",
]
GOOGLE_REQUIRED_ENV = ["GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REDIRECT_URI"]
OUTLOOK_REQUIRED_ENV = [
    "MICROSOFT_OAUTH_CLIENT_ID",
    "MICROSOFT_OAUTH_CLIENT_SECRET",
    "MICROSOFT_OAUTH_REDIRECT_URI",
]


def _token_cipher() -> Fernet:
    secret_digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(secret_digest))


def encrypt_token(token: str) -> str:
    return _token_cipher().encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(token_encrypted: str) -> str:
    try:
        return _token_cipher().decrypt(token_encrypted.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Stored inbox token could not be decrypted") from exc


def mask_token(token: str) -> str:
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}{'*' * max(4, len(token) - 8)}{token[-4:]}"


def mask_subject(subject: str) -> str:
    if len(subject) <= 12:
        return subject[:2] + "*" * max(0, len(subject) - 2)
    return f"{subject[:4]}***{subject[-4:]}"


def sanitize_connection_metadata(metadata_json: dict[str, Any] | None) -> dict[str, Any]:
    metadata = dict(metadata_json or {})
    metadata.pop("access_token_encrypted", None)
    metadata.pop("refresh_token_encrypted", None)
    return metadata


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_return_to(return_to: str | None) -> str:
    candidate = (return_to or "/settings").strip()
    if not candidate.startswith("/") or candidate.startswith("//"):
        return "/settings"
    return candidate


def _google_oauth_config() -> dict[str, str]:
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        raise ValueError("Google OAuth is not configured")
    return {
        "client_id": settings.google_oauth_client_id,
        "client_secret": settings.google_oauth_client_secret,
        "redirect_uri": settings.google_oauth_redirect_uri,
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
    }


def _outlook_oauth_config() -> dict[str, str]:
    if not settings.microsoft_oauth_client_id or not settings.microsoft_oauth_client_secret:
        raise ValueError("Microsoft OAuth is not configured")
    tenant = settings.microsoft_oauth_tenant or "common"
    base = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0"
    return {
        "client_id": settings.microsoft_oauth_client_id,
        "client_secret": settings.microsoft_oauth_client_secret,
        "redirect_uri": settings.microsoft_oauth_redirect_uri,
        "authorize_url": f"{base}/authorize",
        "token_url": f"{base}/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me?$select=mail,userPrincipalName,displayName",
    }


def _oauth_config(provider: str) -> dict[str, str]:
    if provider == "gmail":
        return _google_oauth_config()
    if provider == "outlook":
        return _outlook_oauth_config()
    raise ValueError("Unsupported inbox provider")


def _oauth_scopes(provider: str) -> list[str]:
    if provider == "gmail":
        return GOOGLE_OAUTH_SCOPES
    if provider == "outlook":
        return OUTLOOK_OAUTH_SCOPES
    raise ValueError("Unsupported inbox provider")


def get_oauth_provider_status(provider: str) -> dict[str, Any]:
    if provider == "gmail":
        values = {
            "GOOGLE_OAUTH_CLIENT_ID": settings.google_oauth_client_id,
            "GOOGLE_OAUTH_CLIENT_SECRET": settings.google_oauth_client_secret,
            "GOOGLE_OAUTH_REDIRECT_URI": settings.google_oauth_redirect_uri,
        }
        missing = [key for key in GOOGLE_REQUIRED_ENV if not values[key]]
        return {
            "provider": provider,
            "configured": not missing,
            "authorization_enabled": not missing,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "scopes": GOOGLE_OAUTH_SCOPES,
            "required_env": GOOGLE_REQUIRED_ENV,
            "missing_env": missing,
        }
    if provider == "outlook":
        values = {
            "MICROSOFT_OAUTH_CLIENT_ID": settings.microsoft_oauth_client_id,
            "MICROSOFT_OAUTH_CLIENT_SECRET": settings.microsoft_oauth_client_secret,
            "MICROSOFT_OAUTH_REDIRECT_URI": settings.microsoft_oauth_redirect_uri,
        }
        missing = [key for key in OUTLOOK_REQUIRED_ENV if not values[key]]
        return {
            "provider": provider,
            "configured": not missing,
            "authorization_enabled": not missing,
            "redirect_uri": settings.microsoft_oauth_redirect_uri,
            "scopes": OUTLOOK_OAUTH_SCOPES,
            "required_env": OUTLOOK_REQUIRED_ENV,
            "missing_env": missing,
        }
    raise ValueError("Unsupported inbox provider")


def list_oauth_provider_statuses() -> list[dict[str, Any]]:
    return [get_oauth_provider_status("gmail"), get_oauth_provider_status("outlook")]


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(72)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest()).rstrip(b"=").decode("utf-8")
    return verifier, challenge


def build_oauth_state(provider: str, user_id: int, return_to: str = "/settings") -> tuple[str, str]:
    verifier, challenge = _pkce_pair()
    payload = {
        "provider": provider,
        "user_id": user_id,
        "return_to": _normalize_return_to(return_to),
        "code_verifier": verifier,
        "nonce": secrets.token_urlsafe(16),
        "exp": _utcnow() + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=OAUTH_STATE_ALGORITHM), challenge


def decode_oauth_state(provider: str, state_token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(state_token, settings.secret_key, algorithms=[OAUTH_STATE_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid OAuth state") from exc
    if payload.get("provider") != provider:
        raise ValueError("OAuth provider mismatch")
    if not payload.get("user_id") or not payload.get("code_verifier"):
        raise ValueError("Incomplete OAuth state")
    payload["return_to"] = _normalize_return_to(str(payload.get("return_to", "/settings")))
    return payload


def build_oauth_authorization_url(provider: str, user_id: int, return_to: str = "/settings") -> dict[str, str]:
    config = _oauth_config(provider)
    state_token, code_challenge = build_oauth_state(provider, user_id, return_to)
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": " ".join(_oauth_scopes(provider)),
        "state": state_token,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if provider == "gmail":
        params["access_type"] = "offline"
        params["include_granted_scopes"] = "true"
        params["prompt"] = "consent"
    else:
        params["response_mode"] = "query"
    return {"provider": provider, "authorization_url": f"{config['authorize_url']}?{urlencode(params)}"}


def _token_expiry(expires_in: int | None) -> str:
    if not expires_in:
        return ""
    return (_utcnow() + timedelta(seconds=max(0, expires_in - 60))).isoformat()


def _persist_connection_tokens(
    db: Session,
    *,
    user_id: int,
    provider: str,
    email: str,
    scopes: list[str],
    access_token: str,
    refresh_token: str = "",
    expires_in: int | None = None,
    connected_via: str,
) -> InboxConnection:
    existing = (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user_id, InboxConnection.provider == provider, InboxConnection.email == email)
        .first()
    )
    previous_metadata = existing.metadata_json if existing else {}
    metadata = {
        **sanitize_connection_metadata(previous_metadata),
        "oauth_connected": True,
        "token_present": True,
        "refresh_token_present": bool(refresh_token or previous_metadata.get("refresh_token_encrypted")),
        "provider": provider,
        "connected_via": connected_via,
        "token_expires_at": _token_expiry(expires_in) or str(previous_metadata.get("token_expires_at", "")),
        "access_token_encrypted": encrypt_token(access_token),
    }
    if refresh_token:
        metadata["refresh_token_encrypted"] = encrypt_token(refresh_token)
    elif previous_metadata.get("refresh_token_encrypted"):
        metadata["refresh_token_encrypted"] = previous_metadata["refresh_token_encrypted"]
    if existing:
        existing.status = "connected"
        existing.scopes = scopes
        existing.token_masked = mask_token(access_token)
        existing.metadata_json = metadata
        db.commit()
        db.refresh(existing)
        return existing
    row = InboxConnection(
        user_id=user_id,
        provider=provider,
        email=email,
        status="connected",
        scopes=scopes,
        token_masked=mask_token(access_token),
        metadata_json=metadata,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _exchange_google_code(code: str, code_verifier: str) -> dict[str, Any]:
    config = _google_oauth_config()
    response = httpx.post(
        config["token_url"],
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def _exchange_outlook_code(code: str, code_verifier: str) -> dict[str, Any]:
    config = _outlook_oauth_config()
    response = httpx.post(
        config["token_url"],
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
            "scope": " ".join(OUTLOOK_OAUTH_SCOPES),
            "code_verifier": code_verifier,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def _fetch_google_profile(access_token: str) -> dict[str, Any]:
    response = httpx.get(
        _google_oauth_config()["userinfo_url"],
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def _fetch_outlook_profile(access_token: str) -> dict[str, Any]:
    response = httpx.get(
        _outlook_oauth_config()["userinfo_url"],
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def complete_oauth_connection(db: Session, provider: str, code: str, state_token: str) -> tuple[InboxConnection, str]:
    state = decode_oauth_state(provider, state_token)
    if provider == "gmail":
        token_payload = _exchange_google_code(code, state["code_verifier"])
        profile = _fetch_google_profile(token_payload["access_token"])
        email = str(profile.get("email", "")).strip()
    elif provider == "outlook":
        token_payload = _exchange_outlook_code(code, state["code_verifier"])
        profile = _fetch_outlook_profile(token_payload["access_token"])
        email = str(profile.get("mail") or profile.get("userPrincipalName") or "").strip()
    else:
        raise ValueError("Unsupported inbox provider")
    if not email:
        raise ValueError("Provider profile did not include an email address")
    connection = _persist_connection_tokens(
        db,
        user_id=int(state["user_id"]),
        provider=provider,
        email=email,
        scopes=_oauth_scopes(provider),
        access_token=token_payload["access_token"],
        refresh_token=str(token_payload.get("refresh_token", "")),
        expires_in=token_payload.get("expires_in"),
        connected_via="oauth",
    )
    return connection, state["return_to"]


def _refresh_google_access_token(refresh_token: str) -> dict[str, Any]:
    config = _google_oauth_config()
    response = httpx.post(
        config["token_url"],
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def _refresh_outlook_access_token(refresh_token: str) -> dict[str, Any]:
    config = _outlook_oauth_config()
    response = httpx.post(
        config["token_url"],
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": " ".join(OUTLOOK_OAUTH_SCOPES),
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def _refresh_access_token_if_needed(db: Session, connection: InboxConnection) -> str:
    metadata = connection.metadata_json or {}
    refresh_token_encrypted = str(metadata.get("refresh_token_encrypted", "")).strip()
    expires_at_raw = str(metadata.get("token_expires_at", "")).strip()
    access_token_encrypted = str(metadata.get("access_token_encrypted", "")).strip()
    if not access_token_encrypted:
        raise ValueError("Inbox connection is missing an access token")
    if expires_at_raw:
        try:
            expires_at = datetime.fromisoformat(expires_at_raw)
        except ValueError:
            expires_at = None
        if expires_at and expires_at > _utcnow():
            return decrypt_token(access_token_encrypted)
    else:
        return decrypt_token(access_token_encrypted)
    if not refresh_token_encrypted:
        return decrypt_token(access_token_encrypted)

    refresh_token = decrypt_token(refresh_token_encrypted)
    token_payload = (
        _refresh_google_access_token(refresh_token)
        if connection.provider == "gmail"
        else _refresh_outlook_access_token(refresh_token)
    )
    refreshed = _persist_connection_tokens(
        db,
        user_id=connection.user_id,
        provider=connection.provider,
        email=connection.email,
        scopes=connection.scopes,
        access_token=token_payload["access_token"],
        refresh_token=str(token_payload.get("refresh_token", "")),
        expires_in=token_payload.get("expires_in"),
        connected_via=str((connection.metadata_json or {}).get("connected_via", "oauth")),
    )
    return decrypt_token(str((refreshed.metadata_json or {}).get("access_token_encrypted", "")))


def _gmail_query(sender_hint: str = "", subject_hint: str = "") -> str:
    terms: list[str] = ["newer_than:7d"]
    if sender_hint:
        terms.append(f"from:{sender_hint}")
    if subject_hint:
        terms.append(f"subject:{subject_hint}")
    return " ".join(terms)


def _decode_gmail_body(data: str) -> str:
    padded = data + "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="ignore")


def _extract_gmail_body(payload: dict[str, Any]) -> str:
    body_data = str(payload.get("body", {}).get("data", "")).strip()
    if body_data:
        return _decode_gmail_body(body_data)
    for part in payload.get("parts", []) or []:
        body = _extract_gmail_body(part)
        if body:
            return body
    return ""


def _fetch_gmail_messages(access_token: str, sender_hint: str = "", subject_hint: str = "", limit: int = 10) -> list[dict]:
    headers = {"Authorization": f"Bearer {access_token}"}
    list_response = httpx.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=headers,
        params={"maxResults": min(limit, MAX_PROVIDER_MESSAGES), "q": _gmail_query(sender_hint, subject_hint)},
        timeout=10.0,
    )
    list_response.raise_for_status()
    messages: list[dict] = []
    for item in list_response.json().get("messages", []) or []:
        message_response = httpx.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{item['id']}",
            headers=headers,
            params={"format": "full"},
            timeout=10.0,
        )
        message_response.raise_for_status()
        payload = message_response.json().get("payload", {})
        headers_map = {
            str(header.get("name", "")).lower(): str(header.get("value", ""))
            for header in payload.get("headers", []) or []
        }
        messages.append(
            {
                "sender": headers_map.get("from", ""),
                "subject": headers_map.get("subject", ""),
                "body": _extract_gmail_body(payload) or message_response.json().get("snippet", ""),
            }
        )
    return messages


def _outlook_search(sender_hint: str = "", subject_hint: str = "") -> str:
    terms: list[str] = []
    if sender_hint:
        terms.append(f'from:{sender_hint}')
    if subject_hint:
        terms.append(f'subject:{subject_hint}')
    return " ".join(terms)


def _fetch_outlook_messages(access_token: str, sender_hint: str = "", subject_hint: str = "", limit: int = 10) -> list[dict]:
    headers = {"Authorization": f"Bearer {access_token}", "ConsistencyLevel": "eventual"}
    params = {
        "$top": min(limit, MAX_PROVIDER_MESSAGES),
        "$select": "subject,from,bodyPreview,receivedDateTime",
        "$orderby": "receivedDateTime desc",
    }
    search = _outlook_search(sender_hint, subject_hint)
    if search:
        params["$search"] = f'"{search}"'
    response = httpx.get(
        "https://graph.microsoft.com/v1.0/me/messages",
        headers=headers,
        params=params,
        timeout=10.0,
    )
    response.raise_for_status()
    return [
        {
            "sender": str(item.get("from", {}).get("emailAddress", {}).get("address", "")),
            "subject": str(item.get("subject", "")),
            "body": str(item.get("bodyPreview", "")),
        }
        for item in response.json().get("value", []) or []
    ]


def fetch_inbox_messages(
    db: Session,
    connection: InboxConnection,
    sender_hint: str = "",
    subject_hint: str = "",
    limit: int = 10,
) -> list[dict]:
    access_token = _refresh_access_token_if_needed(db, connection)
    if connection.provider == "gmail":
        return _fetch_gmail_messages(access_token, sender_hint, subject_hint, limit)
    if connection.provider == "outlook":
        return _fetch_outlook_messages(access_token, sender_hint, subject_hint, limit)
    raise ValueError("Unsupported inbox provider")


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
    return _persist_connection_tokens(
        db,
        user_id=user_id,
        provider=provider,
        email=email,
        scopes=scopes,
        access_token=token,
        connected_via="manual",
    )


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
