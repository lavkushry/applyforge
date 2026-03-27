from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CandidateProfile, Resume, Setting, UploadedFile, User
from app.schemas.common import Message
from app.schemas.profile import (
    CandidateProfileIn,
    CandidateProfileOut,
    ProfileSettingsUpdate,
    ResumeParseResponse,
    ResumeUploadResponse,
)
from app.services.files import save_upload, sha256_bytes, validate_resume_upload
from app.services.llm import log_prompt_invocation
from app.services.resume_parser import extract_resume_text, parse_resume_file

router = APIRouter(prefix="/profile", tags=["profile"])


def _profile_payload(payload: CandidateProfileIn) -> dict:
    return payload.model_dump(mode="json")


@router.get("", response_model=CandidateProfileOut)
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("", response_model=CandidateProfileOut)
def create_profile(
    payload: CandidateProfileIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateProfile:
    if db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first():
        raise HTTPException(status_code=400, detail="Profile exists")
    profile = CandidateProfile(user_id=user.id, **_profile_payload(payload))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("", response_model=CandidateProfileOut)
def update_profile(
    payload: CandidateProfileIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in _profile_payload(payload).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    filename = file.filename or "resume.pdf"
    content = await file.read()
    validate_resume_upload(filename, file.content_type, len(content))
    saved_path = save_upload(filename, content)
    uploaded = UploadedFile(
        user_id=user.id,
        original_name=filename,
        path=saved_path,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        checksum=sha256_bytes(content),
    )
    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)
    return ResumeUploadResponse(file_id=uploaded.id, path=uploaded.path, checksum=uploaded.checksum)


@router.post("/parse-resume", response_model=ResumeParseResponse)
def parse_resume(
    file_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeParseResponse:
    uploaded = db.query(UploadedFile).filter(UploadedFile.id == file_id, UploadedFile.user_id == user.id).first()
    if not uploaded:
        raise HTTPException(status_code=404, detail="File not found")
    raw_text = extract_resume_text(uploaded.path)
    parsed = parse_resume_file(uploaded.path)
    log_prompt_invocation(
        db,
        user_id=user.id,
        prompt_name="resume_parse_cleanup",
        payload={"file_id": uploaded.id, "raw_excerpt": raw_text[:300]},
    )
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if profile:
        for key, value in parsed.items():
            setattr(profile, key, value)
    else:
        profile = CandidateProfile(user_id=user.id, **parsed)
        db.add(profile)

    resume = db.query(Resume).filter(Resume.user_id == user.id, Resume.active.is_(True)).first()
    if not resume:
        resume = Resume(
            user_id=user.id,
            uploaded_file_id=uploaded.id,
            original_text=raw_text,
            parse_status="parsed",
        )
        db.add(resume)
    else:
        resume.uploaded_file_id = uploaded.id
        resume.original_text = raw_text
        resume.parse_status = "parsed"

    db.commit()
    return ResumeParseResponse(parsed=CandidateProfileIn.model_validate(parsed))


@router.get("/settings")
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    settings_rows = db.query(Setting).filter(Setting.user_id == user.id).all()
    return {row.key: row.value for row in settings_rows}


@router.put("/settings", response_model=Message)
def update_settings(
    payload: ProfileSettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    for key, value in payload.values.items():
        existing = db.query(Setting).filter(Setting.user_id == user.id, Setting.key == key).first()
        if existing:
            existing.value = value
        else:
            db.add(Setting(user_id=user.id, key=key, value=value))
    db.commit()
    return Message(message="Settings updated")
