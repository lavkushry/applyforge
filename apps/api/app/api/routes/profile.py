from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CandidateProfile, UploadedFile, User
from app.schemas.profile import CandidateProfileIn
from app.services.files import save_upload
from app.services.resume_parser import parse_resume_file

router = APIRouter(prefix='/profile', tags=['profile'])


@router.get('')
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
    return profile


@router.post('')
def create_profile(
    payload: CandidateProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CandidateProfile:
    if db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first():
        raise HTTPException(status_code=400, detail='Profile exists')
    profile = CandidateProfile(user_id=user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put('')
def update_profile(
    payload: CandidateProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
    for k, v in payload.model_dump().items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile


@router.post('/upload-resume')
async def upload_resume(
    file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    content = await file.read()
    saved_path = save_upload(file.filename, content)
    uploaded = UploadedFile(user_id=user.id, path=saved_path, mime_type=file.content_type or 'application/octet-stream')
    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)
    return {'file_id': uploaded.id, 'path': uploaded.path}


@router.post('/parse-resume')
def parse_resume(file_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    uploaded = db.query(UploadedFile).filter(UploadedFile.id == file_id, UploadedFile.user_id == user.id).first()
    if not uploaded:
        raise HTTPException(status_code=404, detail='File not found')
    parsed = parse_resume_file(uploaded.path)
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if profile:
        for k, v in parsed.items():
            setattr(profile, k, v)
    else:
        profile = CandidateProfile(user_id=user.id, **parsed)
        db.add(profile)
    db.commit()
    return {'parsed': parsed}
