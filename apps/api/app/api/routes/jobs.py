import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CandidateProfile, CoverLetter, Job, JobScore, Resume, ResumeVersion, User
from app.schemas.jobs import JobCreate
from app.services.scoring import score_job
from app.services.tailor import generate_cover_letter, tailor_resume

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.post('/manual')
def create_job(payload: JobCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Job:
    dedupe_key = hashlib.sha256(f"{payload.title}|{payload.company}|{payload.application_url}".encode()).hexdigest()
    if db.query(Job).filter(Job.dedupe_key == dedupe_key).first():
        raise HTTPException(status_code=409, detail='Duplicate job')
    job = Job(user_id=user.id, dedupe_key=dedupe_key, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post('/import')
def import_job(payload: JobCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Job:
    return create_job(payload, user, db)


@router.get('')
def list_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Job]:
    return db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()


@router.get('/{job_id}')
def get_job(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return job


@router.post('/{job_id}/score')
def score(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> JobScore:
    job = get_job(job_id, user, db)
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail='Create profile first')
    result = score_job(profile.__dict__, job.description, job.title)
    score_row = JobScore(job_id=job.id, **result)
    db.add(score_row)
    db.commit()
    db.refresh(score_row)
    return score_row


@router.post('/{job_id}/tailor')
def tailor(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    job = get_job(job_id, user, db)
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail='Create profile first')
    resume = db.query(Resume).filter(Resume.user_id == user.id).first()
    if not resume:
        resume = Resume(user_id=user.id)
        db.add(resume)
        db.commit()
        db.refresh(resume)
    content = tailor_resume(profile.__dict__, job.__dict__)
    version = ResumeVersion(resume_id=resume.id, job_id=job.id, content_json=content)
    db.add(version)
    db.commit()
    db.refresh(version)
    return {'resume_version_id': version.id, 'content': content}


@router.post('/{job_id}/cover-letter')
def cover_letter(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CoverLetter:
    job = get_job(job_id, user, db)
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail='Create profile first')
    content = generate_cover_letter(profile.__dict__, job.__dict__)
    row = CoverLetter(job_id=job.id, content=content)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
