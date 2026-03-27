from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ResumeVersion, UploadedFile, User
from app.services.files import render_resume_pdf

router = APIRouter(prefix='/files', tags=['files'])


@router.get('/{file_id}')
def get_file(file_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FileResponse:
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail='Not found')
    return FileResponse(file.path)


@router.post('/export-resume-pdf')
def export_resume_pdf(resume_version_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    rv = db.query(ResumeVersion).filter(ResumeVersion.id == resume_version_id).first()
    if not rv:
        raise HTTPException(status_code=404, detail='Resume version not found')
    path = render_resume_pdf(rv.content_json)
    uploaded = UploadedFile(user_id=user.id, path=path, mime_type='application/pdf')
    db.add(uploaded)
    db.flush()
    rv.pdf_file_id = uploaded.id
    db.commit()
    return {'file_id': uploaded.id, 'path': path}
