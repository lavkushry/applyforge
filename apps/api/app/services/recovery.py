from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.automation.engine import StepEngine
from app.models.entities import ApplicationRun, Job, JobFeedEvent, JobIngestionRun, TargetRole, User
from app.services.application_dispatch import dispatch_application_run
from app.services.application_fsm import transition_run
from app.services.job_dispatch import dispatch_job_enrichment


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def resume_application_run(db: Session, *, run: ApplicationRun) -> ApplicationRun:
    if run.mode == "draft":
        raise HTTPException(status_code=400, detail="Draft runs cannot be resumed")
    if run.status not in {"paused", "uncertain", "failed"}:
        raise HTTPException(status_code=400, detail="Only paused, uncertain, or failed runs can be resumed")
    if not run.prepared_payload or not run.prepared_payload.get("job", {}).get("application_url"):
        raise HTTPException(status_code=400, detail="Run has no prepared payload to resume")

    engine = StepEngine(db, run)
    engine.log_step(
        "resume_requested",
        "completed",
        {
            "previous_status": run.status,
            "previous_step": run.current_step,
            "mode": run.mode,
        },
        step_kind="control",
    )

    transition_run(run, event="resume_requested", current_step="resume_requested")
    try:
        run.external_task_id = dispatch_application_run(run.mode, run.id, run.prepared_payload)
    except Exception as exc:
        run.status = "failed"
        run.error_message = f"Worker dispatch failed: {exc}"
        db.commit()
        raise HTTPException(status_code=502, detail="Worker dispatch failed while retrying the run") from exc
    db.commit()
    db.refresh(run)
    return run


def retry_job_enrichment(db: Session, *, user: User, job: Job) -> JobIngestionRun:
    if not job.role_id:
        raise HTTPException(status_code=400, detail="Job is not linked to a target role")

    role = db.query(TargetRole).filter(TargetRole.id == job.role_id, TargetRole.user_id == user.id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    run = JobIngestionRun(
        role_id=role.id,
        status="running",
        source_count=1,
        discovered_count=1,
        updated_count=1,
        started_at=utcnow(),
    )
    db.add(run)
    db.flush()

    job.enrichment_status = "pending"
    job.enrichment_error = ""
    job.last_seen_at = utcnow()
    job.active = True
    db.add(
        JobFeedEvent(
            role_id=role.id,
            job_id=job.id,
            run_id=run.id,
            event_type="enrichment_retry_requested",
            event_metadata={
                "source_kind": job.enrichment_metadata.get("source_kind", ""),
                "source_url": job.enrichment_metadata.get("source_url", "") or job.application_url,
            },
        )
    )
    db.commit()
    db.refresh(run)

    try:
        dispatch_job_enrichment(
            run_id=run.id,
            job_id=job.id,
            role_id=role.id,
            user_id=user.id,
            source_context={
                "source_kind": job.enrichment_metadata.get("source_kind", ""),
                "source_url": job.enrichment_metadata.get("source_url", "") or job.application_url,
            },
        )
    except Exception as exc:
        run.status = "failed"
        run.error_message = f"Enrichment dispatch failed: {exc}"
        job.enrichment_status = "failed"
        job.enrichment_error = f"Enrichment dispatch failed: {exc}"
        db.commit()
        raise HTTPException(status_code=502, detail="Worker dispatch failed while retrying enrichment") from exc
    return run
