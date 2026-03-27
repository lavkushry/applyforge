from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Resume, ResumeVersion, UploadedFile, User
from app.schemas.applications import ExportResumePdfRequest
from app.services.files import render_resume_pdf

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{file_id}")
def get_file(file_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FileResponse:
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id, UploadedFile.user_id == user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file.path)


@router.post("/export-resume-pdf")
def export_resume_pdf(
    payload: ExportResumePdfRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    resume_version = db.query(ResumeVersion).filter(ResumeVersion.id == payload.resume_version_id).first()
    if not resume_version:
        raise HTTPException(status_code=404, detail="Resume version not found")
    resume = db.query(Resume).filter(Resume.id == resume_version.resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")
    path = render_resume_pdf(resume_version.content_json)
    uploaded = UploadedFile(
        user_id=user.id,
        original_name=f"resume-version-{resume_version.id}.pdf",
        path=path,
        mime_type="application/pdf",
    )
    db.add(uploaded)
    db.flush()
    resume_version.pdf_file_id = uploaded.id
    db.commit()
    return {"file_id": uploaded.id, "path": path}
