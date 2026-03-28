from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.automation.engine import StepEngine
from app.db.session import get_db
from app.models.entities import (
    Application,
    ApplicationRun,
    ApplicationStep,
    ApplicationStatus,
    CandidateProfile,
    CoverLetter,
    InboxConnection,
    Job,
    ResumeVersion,
    TargetRole,
    User,
)
from app.schemas.inbox import InboxOtpRequest
from app.schemas.applications import ApplicationOut, ApplicationPrepareResponse, ApplicationRunOut
from app.services.application_dispatch import dispatch_application_run
from app.services.application_packets import build_application_packet, summarize_application_packet
from app.services.inbox import extract_otp, fetch_inbox_messages, record_otp_event

router = APIRouter(prefix="/applications", tags=["applications"])


def _ensure_application(job_id: int, user_id: int, db: Session) -> Application:
    existing = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user_id).first()
    if existing:
        return existing
    application = Application(job_id=job_id, user_id=user_id, status=ApplicationStatus.ready_to_apply)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def _get_profile(user_id: int, db: Session) -> CandidateProfile | None:
    return db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()


def _get_role(job: Job, user_id: int, db: Session) -> TargetRole | None:
    if not job.role_id:
        return None
    return db.query(TargetRole).filter(TargetRole.id == job.role_id, TargetRole.user_id == user_id).first()


def _get_latest_run(application: Application, db: Session) -> ApplicationRun | None:
    if application.latest_run_id:
        run = db.query(ApplicationRun).filter(ApplicationRun.id == application.latest_run_id).first()
        if run:
            return run
    return (
        db.query(ApplicationRun)
        .filter(ApplicationRun.application_id == application.id)
        .order_by(ApplicationRun.started_at.desc())
        .first()
    )


def _get_connected_inbox(user_id: int, db: Session) -> InboxConnection | None:
    return (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user_id, InboxConnection.status == "connected")
        .order_by(InboxConnection.updated_at.desc())
        .first()
    )


def _get_latest_action_required(run: ApplicationRun | None, db: Session) -> dict | None:
    if not run or run.status not in {"paused", "uncertain", "failed"}:
        return None

    step = (
        db.query(ApplicationStep)
        .filter(
            ApplicationStep.run_id == run.id,
            (ApplicationStep.requires_approval.is_(True)) | (ApplicationStep.status.in_(["paused", "failed"])),
        )
        .order_by(ApplicationStep.started_at.desc(), ApplicationStep.id.desc())
        .first()
    )
    if not step:
        if run.error_message:
            return {
                "name": run.current_step,
                "step_kind": "run_error",
                "reason": run.error_message,
            }
        return None

    visible_output = step.masked_output or step.output
    reason = visible_output.get("reason") or visible_output.get("error") or "Manual review required before this run can continue."
    return {
        "name": step.name,
        "step_kind": step.step_kind,
        "reason": str(reason),
    }


def _serialize_application(application: Application, user: User, db: Session) -> dict:
    job = db.query(Job).filter(Job.id == application.job_id, Job.user_id == user.id).first()
    latest_run = _get_latest_run(application, db)
    profile = _get_profile(user.id, db)
    role = _get_role(job, user.id, db) if job else None
    assisted_packet = (
        build_application_packet(
            db,
            application=application,
            job=job,
            user=user,
            profile=profile,
            role=role,
            mode="assisted",
        )
        if job
        else None
    )
    auto_packet = (
        build_application_packet(
            db,
            application=application,
            job=job,
            user=user,
            profile=profile,
            role=role,
            mode="auto",
        )
        if job
        else None
    )
    has_tailored_resume = bool(job and db.query(ResumeVersion.id).filter(ResumeVersion.job_id == job.id).first())
    has_cover_letter = bool(job and db.query(CoverLetter.id).filter(CoverLetter.job_id == job.id).first())
    return {
        **ApplicationOut.model_validate(application).model_dump(mode="json"),
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "application_url": job.application_url,
            "latest_score": job.latest_score,
            "latest_recommendation": job.latest_recommendation,
            "enrichment_status": job.enrichment_status,
            "enrichment_revision": job.enrichment_revision,
        }
        if job
        else None,
        "latest_run": {
            "id": latest_run.id,
            "mode": latest_run.mode,
            "status": latest_run.status,
            "current_step": latest_run.current_step,
        }
        if latest_run
        else None,
        "action_required": _get_latest_action_required(latest_run, db),
        "pipeline": {
            "discovered": True,
            "enriched": bool(job and job.enrichment_status == "completed"),
            "scored": bool(job and job.latest_score > 0 and job.latest_score_revision >= job.enrichment_revision),
            "tailored": has_tailored_resume,
            "cover_letter": has_cover_letter,
            "packet_ready": bool(assisted_packet and assisted_packet["ready"]),
            "auto_ready": bool(auto_packet and auto_packet["auto_submit_allowed"]),
        },
        "packet_summary": summarize_application_packet(assisted_packet) if assisted_packet else None,
    }


@router.post("/{job_id}/prepare", response_model=ApplicationPrepareResponse)
def prepare(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    profile = _get_profile(user.id, db)
    role = _get_role(job, user.id, db)
    packet = build_application_packet(
        db,
        application=application,
        job=job,
        user=user,
        profile=profile,
        role=role,
        mode="assisted",
    )
    return {
        "application": ApplicationOut.model_validate(application).model_dump(mode="json"),
        "packet": summarize_application_packet(packet),
    }


def _create_run(job: Job, application: Application, role: TargetRole | None, mode: str, packet: dict, db: Session) -> ApplicationRun:
    run = ApplicationRun(
        application_id=application.id,
        role_id=role.id if role else None,
        mode=mode,
        status="queued",
        current_step="preflight",
        prepared_payload=packet,
        policy_snapshot={
            "role_name": role.name if role else "",
            "automation_enabled": role.automation_enabled if role else False,
            "min_auto_apply_score": role.min_auto_apply_score if role else 85.0,
            "latest_score": job.latest_score,
            "ready": packet["ready"],
            "upload_ready": packet["upload_ready"],
            "missing_answers": packet["missing_answers"],
            "blocking_issues": packet["blocking_issues"],
            "auto_submit_allowed": packet["auto_submit_allowed"],
        },
    )
    db.add(run)
    db.flush()
    application.latest_run_id = run.id
    db.commit()
    db.refresh(run)
    return run


@router.post("/{job_id}/run-draft", response_model=ApplicationRunOut)
def run_draft(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    role = _get_role(job, user.id, db)
    profile = _get_profile(user.id, db)
    packet = build_application_packet(
        db,
        application=application,
        job=job,
        user=user,
        profile=profile,
        role=role,
        mode="draft",
    )
    run = _create_run(job, application, role, "draft", packet, db)
    engine = StepEngine(db, run)
    if not packet["ready"]:
        engine.log_step(
            "draft_packet_review",
            "paused",
            {"reason": ", ".join(packet["blocking_issues"] or packet["missing_answers"])},
            step_kind="preflight",
            requires_approval=True,
        )
        engine.complete("paused")
        db.refresh(run)
        return run
    engine.log_step(
        "draft_packet_ready",
        "completed",
        {
            "resume_file_id": packet["resume_file_id"],
            "cover_letter_id": packet["cover_letter_id"],
            "answer_keys": sorted(packet["answers"].keys()),
        },
        step_kind="draft",
    )
    engine.complete("completed")
    db.refresh(run)
    return run


@router.post("/{job_id}/run-assisted", response_model=ApplicationRunOut)
def run_assisted(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    role = _get_role(job, user.id, db)
    profile = _get_profile(user.id, db)
    packet = build_application_packet(
        db,
        application=application,
        job=job,
        user=user,
        profile=profile,
        role=role,
        mode="assisted",
    )
    run = _create_run(job, application, role, "assisted", packet, db)
    engine = StepEngine(db, run)
    if not packet["ready"]:
        engine.log_step(
            "application_preflight_gate",
            "paused",
            {"reason": ", ".join(packet["blocking_issues"] or packet["missing_answers"])},
            step_kind="preflight",
            requires_approval=True,
        )
        engine.complete("paused")
        return run
    try:
        run.external_task_id = dispatch_application_run("assisted", run.id, packet)
        run.status = "queued"
        run.current_step = "worker_dispatched"
        db.commit()
        db.refresh(run)
    except Exception as exc:
        run.status = "failed"
        run.error_message = f"Worker dispatch failed: {exc}"
        db.commit()
        engine.log_step("worker_dispatch_failed", "failed", {"error": str(exc)}, step_kind="dispatch")
        engine.complete("failed")
    return run


@router.post("/{job_id}/run-auto", response_model=ApplicationRunOut)
def run_auto(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    role = _get_role(job, user.id, db)
    profile = _get_profile(user.id, db)
    packet = build_application_packet(
        db,
        application=application,
        job=job,
        user=user,
        profile=profile,
        role=role,
        mode="auto",
    )
    run = _create_run(job, application, role, "auto", packet, db)
    engine = StepEngine(db, run)
    if not packet["auto_submit_allowed"]:
        engine.log_step(
            "auto_apply_preflight_gate",
            "paused",
            {"reason": "; ".join(packet["auto_policy_reasons"] or packet["blocking_issues"] or packet["missing_answers"])},
            step_kind="preflight",
            requires_approval=True,
        )
        engine.complete("paused")
        return run
    try:
        run.external_task_id = dispatch_application_run("auto", run.id, packet)
        run.status = "queued"
        run.current_step = "worker_dispatched"
        db.commit()
        db.refresh(run)
    except Exception as exc:
        run.status = "failed"
        run.error_message = f"Worker dispatch failed: {exc}"
        db.commit()
        engine.log_step("worker_dispatch_failed", "failed", {"error": str(exc)}, step_kind="dispatch")
        engine.complete("failed")
    return run


@router.post("/{job_id}/request-otp")
def request_otp(
    job_id: int,
    payload: InboxOtpRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    run = _get_latest_run(application, db)
    if not run:
        raise HTTPException(status_code=400, detail="Start an application run before requesting OTP")
    connection = _get_connected_inbox(user.id, db)
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
        run_id=run.id,
        status=result["status"],
        sender=result["sender"],
        subject=result["subject"],
        code_last4=result["code_last4"],
        error_message="" if result["status"] == "resolved" else "OTP requires manual review",
    )
    masked_code = f"***{result['code_last4']}" if result["code_last4"] else ""
    step_status = "completed" if result["status"] == "resolved" else "paused"
    StepEngine(db, run).log_step(
        "retrieve_email_otp",
        step_status,
        {
            "provider": connection.provider,
            "status": result["status"],
            "confidence": result["confidence"],
            "sender": result["sender"],
            "message_count": len(messages),
        },
        masked_output={"subject": event.subject_masked, "masked_code": masked_code},
        step_kind="otp_lookup",
        requires_approval=step_status == "paused",
    )
    if step_status == "paused":
        run.status = "paused"
        db.commit()

    return {
        "application_id": application.id,
        "run_id": run.id,
        "status": result["status"],
        "code": result["code"] if result["status"] == "resolved" else "",
        "masked_code": masked_code,
        "confidence": result["confidence"],
        "provider": connection.provider,
        "message_count": len(messages),
        "event_id": event.id,
    }


@router.get("")
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Application).filter(Application.user_id == user.id).order_by(Application.created_at.desc()).all()
    return [_serialize_application(application, user, db) for application in rows]


@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.query(Application).filter(Application.user_id == user.id).order_by(Application.created_at.desc()).all()
    serialized = [_serialize_application(application, user, db) for application in rows]
    status_counts: dict[str, int] = {}
    run_counts: dict[str, int] = {}
    pipeline_counts = {
        "tracked": len(serialized),
        "enriched": 0,
        "scored": 0,
        "tailored": 0,
        "cover_letter": 0,
        "packet_ready": 0,
        "auto_ready": 0,
        "applied": 0,
    }
    for row in serialized:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        latest_run = row.get("latest_run")
        if latest_run:
            run_counts[latest_run["status"]] = run_counts.get(latest_run["status"], 0) + 1
        pipeline = row["pipeline"]
        for key in ("enriched", "scored", "tailored", "cover_letter", "packet_ready", "auto_ready"):
            if pipeline[key]:
                pipeline_counts[key] += 1
        if row["status"] == ApplicationStatus.applied.value:
            pipeline_counts["applied"] += 1
    return {
        "status_counts": status_counts,
        "run_counts": run_counts,
        "pipeline_counts": pipeline_counts,
    }


@router.post("/{application_id}/mark-applied", response_model=ApplicationOut)
def mark_applied(application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Application:
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application.status = ApplicationStatus.applied
    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/reset-ready", response_model=ApplicationOut)
def reset_ready(application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Application:
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application.status = ApplicationStatus.ready_to_apply
    db.commit()
    db.refresh(application)
    return application


@router.get("/{application_id}")
def get_application(application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return _serialize_application(application, user, db)
