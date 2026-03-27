from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.automation.engine import StepEngine
from app.db.session import get_db
from app.models.entities import Application, ApplicationRun, ApplicationStatus, CandidateProfile, Job, User
from app.schemas.applications import ApplicationOut, ApplicationRunOut
from app.services.tailor import detect_risky_question, generate_application_answer

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


@router.post("/{job_id}/prepare", response_model=ApplicationOut)
def prepare(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Application:
    if not db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first():
        raise HTTPException(status_code=404, detail="Job not found")
    return _ensure_application(job_id, user.id, db)


@router.post("/{job_id}/run-assisted", response_model=ApplicationRunOut)
def run_assisted(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    run = ApplicationRun(application_id=application.id, mode="assisted", status="running")
    db.add(run)
    db.flush()
    application.latest_run_id = run.id
    db.commit()
    db.refresh(run)
    engine = StepEngine(db, run)
    engine.log_step("open_application_url", "completed", {"url": job.application_url})
    engine.log_step("fill_contact_fields", "completed", {"email": user.email})
    risk = detect_risky_question("Confirm salary expectations and visa status before submit")
    engine.log_step("risk_review", "paused", risk)
    engine.log_step("pause_before_submit", "paused", {"requires_user_approval": True})
    engine.complete("paused")
    return run


@router.post("/{job_id}/run-auto", response_model=ApplicationRunOut)
def run_auto(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = _ensure_application(job_id, user.id, db)
    run = ApplicationRun(application_id=application.id, mode="auto", status="running")
    db.add(run)
    db.flush()
    application.latest_run_id = run.id
    db.commit()
    db.refresh(run)
    engine = StepEngine(db, run)
    profile = _get_profile(user.id, db)
    engine.log_step("open_application_url", "completed", {"url": job.application_url})
    answer = generate_application_answer(
        "What is your work authorization status?",
        {
            "saved_answers": profile.saved_answers if profile else {},
            "preferences": profile.preferences if profile else {},
            "links": profile.links if profile else [],
        },
    )
    engine.log_step("answer_common_questions", "completed", answer)
    if answer["requires_review"]:
        engine.log_step("pause_before_submit", "paused", {"reason": "Unknown work authorization answer"})
        engine.complete("paused")
    else:
        engine.log_step("submit_application", "completed", {"submitted": False, "mode": "skeleton"})
        engine.complete("completed")
    return run


@router.get("")
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Application).filter(Application.user_id == user.id).order_by(Application.created_at.desc()).all()
    jobs = {
        job.id: job
        for job in db.query(Job).filter(Job.id.in_([application.job_id for application in rows])).all()
    } if rows else {}
    return [
        {
            **ApplicationOut.model_validate(application).model_dump(mode="json"),
            "job": {
                "id": jobs[application.job_id].id,
                "title": jobs[application.job_id].title,
                "company": jobs[application.job_id].company,
            }
            if application.job_id in jobs
            else None,
        }
        for application in rows
    ]


@router.get("/{application_id}")
def get_application(application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    job = db.query(Job).filter(Job.id == application.job_id).first()
    return {
        "application": ApplicationOut.model_validate(application).model_dump(mode="json"),
        "job": {"id": job.id, "title": job.title, "company": job.company} if job else None,
    }
