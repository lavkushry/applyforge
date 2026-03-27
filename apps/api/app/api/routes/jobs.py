from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CandidateProfile, CoverLetter, Job, JobFeedEvent, JobScore, Resume, ResumeVersion, TargetRole, User
from app.schemas.jobs import (
    CoverLetterResponse,
    JobCreate,
    JobOut,
    JobScoreRequest,
    JobScoreResponse,
    ResumeTailorRequest,
    ResumeVersionResponse,
)
from app.services.job_normalizer import normalize_job_payload
from app.services.llm import log_prompt_invocation
from app.services.resume_themes import get_theme_by_id
from app.services.scoring import score_job
from app.services.tailor import generate_cover_letter, tailor_resume

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _require_profile(user_id: int, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create profile first")
    return profile


def _ensure_resume(user_id: int, db: Session) -> Resume:
    resume = db.query(Resume).filter(Resume.user_id == user_id, Resume.active.is_(True)).first()
    if resume:
        return resume
    resume = Resume(user_id=user_id)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def _require_role(user_id: int, role_id: int | None, db: Session) -> TargetRole | None:
    if not role_id:
        return None
    role = db.query(TargetRole).filter(TargetRole.id == role_id, TargetRole.user_id == user_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/manual", response_model=JobOut)
def create_job(payload: JobCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Job:
    _require_role(user.id, payload.role_id, db)
    normalized = normalize_job_payload(payload.model_dump(mode="json"))
    if db.query(Job).filter(Job.dedupe_key == normalized["dedupe_key"]).first():
        raise HTTPException(status_code=409, detail="Duplicate job")
    log_prompt_invocation(
        db,
        user_id=user.id,
        prompt_name="job_normalization",
        payload={"title": payload.title, "company": payload.company, "description_excerpt": payload.description[:250]},
    )
    job = Job(user_id=user.id, **normalized)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/import", response_model=JobOut)
def import_job(payload: JobCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Job:
    return create_job(payload, user, db)


@router.get("", response_model=list[JobOut])
def list_jobs(
    q: str | None = Query(default=None),
    remote_type: str | None = Query(default=None),
    role_id: int | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Job]:
    query = db.query(Job).filter(Job.user_id == user.id)
    if q:
        needle = f"%{q}%"
        query = query.filter((Job.title.ilike(needle)) | (Job.company.ilike(needle)) | (Job.description.ilike(needle)))
    if remote_type:
        query = query.filter(Job.remote_type == remote_type)
    if role_id:
        query = query.filter(Job.role_id == role_id)
    return query.order_by(Job.created_at.desc()).all()


@router.get("/feed")
def job_feed(
    role_id: int | None = Query(default=None),
    event_type: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(JobFeedEvent).join(Job, Job.id == JobFeedEvent.job_id).filter(Job.user_id == user.id)
    if role_id:
        query = query.filter(JobFeedEvent.role_id == role_id)
    if event_type:
        query = query.filter(JobFeedEvent.event_type == event_type)
    events = query.order_by(JobFeedEvent.created_at.desc()).limit(100).all()
    jobs = {
        job.id: job
        for job in db.query(Job).filter(Job.id.in_([event.job_id for event in events])).all()
    } if events else {}
    roles = {
        role.id: role.name
        for role in db.query(TargetRole).filter(TargetRole.id.in_([event.role_id for event in events])).all()
    } if events else {}
    return [
        {
            "id": event.id,
            "role_id": event.role_id,
            "role_name": roles.get(event.role_id, ""),
            "job_id": event.job_id,
            "run_id": event.run_id,
            "event_type": event.event_type,
            "event_metadata": event.event_metadata,
            "created_at": event.created_at,
            "job": JobOut.model_validate(jobs[event.job_id]).model_dump(mode="json") if event.job_id in jobs else None,
        }
        for event in events
    ]


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/score", response_model=JobScoreResponse)
def score(
    job_id: int,
    payload: JobScoreRequest | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobScore:
    job = get_job(job_id, user, db)
    profile = _require_profile(user.id, db)
    role = _require_role(user.id, payload.role_id if payload else job.role_id, db)
    log_prompt_invocation(
        db,
        user_id=user.id,
        prompt_name="job_scoring_explainer",
        payload={"job_id": job.id, "profile_skills": profile.skills[:10]},
    )
    score_result = score_job(
        {
            "basics": profile.basics,
            "skills": profile.skills,
            "summary": profile.summary,
            "preferences": profile.preferences,
        },
        {
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "remote_type": job.remote_type,
            "seniority": job.seniority,
            "salary": job.salary,
            "tags": job.tags,
        },
        {
            "name": role.name,
            "aliases": role.aliases,
            "keywords": role.keywords,
            "preferred_locations": role.preferred_locations,
            "remote_preference": role.remote_preference,
            "salary_target": role.salary_target,
            "visa_preference": role.visa_preference,
            "seniority": role.seniority,
        }
        if role
        else None,
    )
    job.latest_score = score_result["overall_score"]
    job.latest_recommendation = score_result["recommendation"]
    score_row = JobScore(job_id=job.id, role_id=role.id if role else None, **score_result)
    db.add(score_row)
    db.commit()
    db.refresh(score_row)
    return score_row


@router.post("/{job_id}/tailor", response_model=ResumeVersionResponse)
def tailor(
    job_id: int,
    payload: ResumeTailorRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeVersion:
    job = get_job(job_id, user, db)
    profile = _require_profile(user.id, db)
    resume = _ensure_resume(user.id, db)
    role = _require_role(user.id, payload.role_id or job.role_id, db)
    theme = get_theme_by_id(db, payload.theme_id)
    log_prompt_invocation(
        db,
        user_id=user.id,
        prompt_name="resume_tailoring",
        payload={"job_id": job.id, "job_title": job.title},
    )
    content = tailor_resume(
        {
            "basics": profile.basics,
            "summary": profile.summary,
            "skills": profile.skills,
            "experience": profile.experience,
            "projects": profile.projects,
            "education": profile.education,
            "certifications": profile.certifications,
            "links": profile.links,
            "preferences": profile.preferences,
            "saved_answers": profile.saved_answers,
            "fact_locked": profile.fact_locked,
        },
        {"title": job.title, "company": job.company, "description": job.description},
        {
            "name": role.name,
            "aliases": role.aliases,
            "keywords": role.keywords,
            "preferred_locations": role.preferred_locations,
            "remote_preference": role.remote_preference,
        }
        if role
        else None,
    )
    diff_metadata = content.pop("diff_metadata", {})
    version = ResumeVersion(
        resume_id=resume.id,
        job_id=job.id,
        theme_id=theme.id if theme else None,
        title=f"{job.company} - {job.title}",
        variant="tailored",
        theme_variant=theme.slug if theme else "classic-ats-light",
        ats_mode=payload.ats_mode,
        content_json=content,
        diff_metadata=diff_metadata,
        export_status="ready",
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/{job_id}/eligibility")
def eligibility(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    job = get_job(job_id, user, db)
    role = _require_role(user.id, job.role_id, db)
    threshold = role.min_auto_apply_score if role else 85.0
    eligible = bool(role and role.automation_enabled and job.latest_score >= threshold)
    return {
        "eligible": eligible,
        "latest_score": job.latest_score,
        "threshold": threshold,
        "role_id": role.id if role else None,
        "role_name": role.name if role else "",
        "reason": "Eligible for auto-apply" if eligible else "Needs assisted review or higher score",
    }


@router.post("/{job_id}/cover-letter", response_model=CoverLetterResponse)
def cover_letter(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CoverLetter:
    job = get_job(job_id, user, db)
    profile = _require_profile(user.id, db)
    log_prompt_invocation(
        db,
        user_id=user.id,
        prompt_name="cover_letter",
        payload={"job_id": job.id, "job_title": job.title},
    )
    content = generate_cover_letter(
        {"basics": profile.basics, "summary": profile.summary, "skills": profile.skills},
        {"title": job.title, "company": job.company, "description": job.description},
    )
    row = db.query(CoverLetter).filter(CoverLetter.job_id == job.id).first()
    if row:
        row.content = content
    else:
        row = CoverLetter(job_id=job.id, content=content)
        db.add(row)
    db.commit()
    db.refresh(row)
    return row
