from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import (
    Application,
    ApplicationRun,
    ApplicationStep,
    AuditLog,
    InboxConnection,
    InboxOtpEvent,
    Job,
    JobIngestionRun,
    TargetRole,
    User,
)
from app.schemas.common import HealthResponse
from app.services.recovery import resume_application_run, retry_job_enrichment

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/runs")
def runs(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(ApplicationRun, Application)
        .join(Application, Application.id == ApplicationRun.application_id)
        .filter(Application.user_id == user.id)
        .order_by(ApplicationRun.started_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": run.id,
            "application_id": application.id,
            "job_id": application.job_id,
            "mode": run.mode,
            "status": run.status,
            "current_step": run.current_step,
            "error_message": run.error_message,
            "external_task_id": run.external_task_id,
            "retry_metadata": run.retry_metadata,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
        }
        for run, application in rows
    ]


@router.get("/ingestion-runs")
def ingestion_runs(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(JobIngestionRun, TargetRole)
        .join(TargetRole, TargetRole.id == JobIngestionRun.role_id)
        .filter(TargetRole.user_id == user.id)
        .order_by(JobIngestionRun.started_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": run.id,
            "role_id": role.id,
            "role_name": role.name,
            "status": run.status,
            "source_count": run.source_count,
            "discovered_count": run.discovered_count,
            "inserted_count": run.inserted_count,
            "updated_count": run.updated_count,
            "enriched_count": run.enriched_count,
            "failed_count": run.failed_count,
            "expired_count": run.expired_count,
            "error_message": run.error_message,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
        }
        for run, role in rows
    ]


@router.get("/errors")
def errors(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(ApplicationStep, ApplicationRun, Application)
        .join(ApplicationRun, ApplicationRun.id == ApplicationStep.run_id)
        .join(Application, Application.id == ApplicationRun.application_id)
        .filter(
            Application.user_id == user.id,
            ApplicationStep.status.in_(["failed", "paused"]),
        )
        .order_by(ApplicationStep.started_at.desc())
        .all()
    )
    return [
        {
            "id": step.id,
            "run_id": run.id,
            "application_id": application.id,
            "job_id": application.job_id,
            "name": step.name,
            "step_kind": step.step_kind,
            "status": step.status,
            "requires_approval": step.requires_approval,
            "screenshot_file_id": step.screenshot_file_id,
            "retry_count": step.retry_count,
            "output": step.masked_output or step.output,
        }
        for step, run, application in rows
    ]


@router.get("/prompt-logs")
def prompt_logs(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(AuditLog)
        .filter(
            AuditLog.action.like("prompt.%"),
            (AuditLog.user_id == user.id) | (AuditLog.user_id.is_(None)),
        )
        .order_by(AuditLog.created_at.desc())
        .limit(25)
        .all()
    )
    return [
        {
            "id": row.id,
            "action": row.action,
            "metadata": row.event_metadata,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/otp-events")
def otp_events(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(InboxOtpEvent, InboxConnection)
        .join(InboxConnection, InboxConnection.id == InboxOtpEvent.connection_id)
        .filter(InboxConnection.user_id == user.id)
        .order_by(InboxOtpEvent.created_at.desc())
        .limit(25)
        .all()
    )
    return [
        {
            "id": event.id,
            "connection_id": event.connection_id,
            "run_id": event.run_id,
            "status": event.status,
            "sender": event.sender,
            "subject_masked": event.subject_masked,
            "code_last4": event.code_last4,
            "error_message": event.error_message,
            "created_at": event.created_at,
        }
        for event, _connection in rows
    ]


@router.get("/enrichment-errors")
def enrichment_errors(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(Job, TargetRole)
        .join(TargetRole, TargetRole.id == Job.role_id)
        .filter(Job.user_id == user.id, Job.enrichment_status == "failed")
        .order_by(Job.updated_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "job_id": job.id,
            "role_id": role.id,
            "role_name": role.name,
            "title": job.title,
            "company": job.company,
            "application_url": job.application_url,
            "error_message": job.enrichment_error,
            "source_kind": job.enrichment_metadata.get("source_kind", ""),
            "source_url": job.enrichment_metadata.get("source_url", ""),
            "updated_at": job.updated_at,
        }
        for job, role in rows
    ]


@router.post("/jobs/{job_id}/retry-enrichment")
def retry_enrichment(
    job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    run = retry_job_enrichment(db, user=user, job=job)
    return {
        "message": "Enrichment retry queued",
        "job_id": job.id,
        "run_id": run.id,
        "status": run.status,
    }


@router.post("/runs/{run_id}/retry")
def retry_run(
    run_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    run_row = (
        db.query(ApplicationRun, Application)
        .join(Application, Application.id == ApplicationRun.application_id)
        .filter(ApplicationRun.id == run_id, Application.user_id == user.id)
        .first()
    )
    if not run_row:
        raise HTTPException(status_code=404, detail="Run not found")
    run, application = run_row
    resumed = resume_application_run(db, run=run)
    return {
        "message": "Run retry queued",
        "run_id": resumed.id,
        "application_id": application.id,
        "status": resumed.status,
        "external_task_id": resumed.external_task_id,
    }


@router.get("/health", response_model=HealthResponse)
def health(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> HealthResponse:
    # Security: Require authentication to view health diagnostics
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
