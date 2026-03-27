from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import ApplicationRun, ApplicationStep, AuditLog, User
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
