from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import ApplicationRun, ApplicationStep, AuditLog, InboxOtpEvent, JobIngestionRun, User
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/runs")
def runs(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(ApplicationRun).order_by(ApplicationRun.started_at.desc()).limit(50).all()
    return [
        {
            "id": row.id,
            "application_id": row.application_id,
            "mode": row.mode,
            "status": row.status,
            "current_step": row.current_step,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
        }
        for row in rows
    ]


@router.get("/ingestion-runs")
def ingestion_runs(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(JobIngestionRun).order_by(JobIngestionRun.started_at.desc()).limit(50).all()
    return [
        {
            "id": row.id,
            "role_id": row.role_id,
            "status": row.status,
            "source_count": row.source_count,
            "discovered_count": row.discovered_count,
            "inserted_count": row.inserted_count,
            "updated_count": row.updated_count,
            "error_message": row.error_message,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
        }
        for row in rows
    ]


@router.get("/errors")
def errors(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(ApplicationStep).filter(ApplicationStep.status.in_(["failed", "paused"])).all()
    return [
        {"id": row.id, "run_id": row.run_id, "name": row.name, "status": row.status, "output": row.output}
        for row in rows
    ]


@router.get("/prompt-logs")
def prompt_logs(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(AuditLog).filter(AuditLog.action.like("prompt.%")).order_by(AuditLog.created_at.desc()).limit(25).all()
    return [
        {"id": row.id, "action": row.action, "metadata": row.event_metadata, "created_at": row.created_at}
        for row in rows
    ]


@router.get("/otp-events")
def otp_events(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(InboxOtpEvent).order_by(InboxOtpEvent.created_at.desc()).limit(25).all()
    return [
        {
            "id": row.id,
            "connection_id": row.connection_id,
            "run_id": row.run_id,
            "status": row.status,
            "sender": row.sender,
            "subject_masked": row.subject_masked,
            "code_last4": row.code_last4,
            "error_message": row.error_message,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    redis_status = "unavailable"
    try:
        Redis.from_url(settings.redis_url).ping()
        redis_status = "ok"
    except Exception:
        redis_status = "unavailable"
    return HealthResponse(
        status="ok",
        database="ok",
        redis=redis_status,
        timestamp=datetime.now(timezone.utc),
    )
