from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Resume, ResumeTheme, ResumeVersion, User
from app.schemas.jobs import ResumePreviewResponse, ResumeThemeOut
from app.services.resume_themes import build_preview_blocks, get_theme_by_id

router = APIRouter(tags=["resume-themes"])


@router.get("/resume-themes", response_model=list[ResumeThemeOut])
def list_resume_themes(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ResumeTheme]:
    return db.query(ResumeTheme).filter(ResumeTheme.active.is_(True)).order_by(ResumeTheme.id.asc()).all()


@router.post("/resume-versions/{resume_version_id}/preview", response_model=ResumePreviewResponse)
def preview_resume_version(
    resume_version_id: int,
    theme_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumePreviewResponse:
    resume_version = db.query(ResumeVersion).filter(ResumeVersion.id == resume_version_id).first()
    if not resume_version:
        raise HTTPException(status_code=404, detail="Resume version not found")
    resume = db.query(Resume).filter(Resume.id == resume_version.resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found")
    theme = get_theme_by_id(db, theme_id or resume_version.theme_id)
    return ResumePreviewResponse(
        theme=ResumeThemeOut.model_validate(theme),
        blocks=build_preview_blocks(resume_version.content_json),
    )
