from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CandidateProfile, User
from app.schemas.resume_templates import (
    ResumeTemplateCatalogResponse,
    ResumeTemplateOut,
    ResumeTemplateRenderRequest,
    ResumeTemplateRenderResponse,
    ResumeTemplateSectionOut,
)
from app.services.resume_templates import (
    get_resume_template,
    list_resume_templates,
    load_resume_sections,
    profile_to_resume_content,
    render_resume_template as render_resume_template_content,
)

router = APIRouter(prefix="/resume/templates", tags=["resume-templates"])


@router.get("", response_model=ResumeTemplateCatalogResponse)
def list_template_catalog(user: User = Depends(get_current_user)) -> ResumeTemplateCatalogResponse:
    return ResumeTemplateCatalogResponse(
        templates=[ResumeTemplateOut.model_validate(template) for template in list_resume_templates()],
        sections=[ResumeTemplateSectionOut.model_validate(section) for section in load_resume_sections()],
    )


@router.post("/render", response_model=ResumeTemplateRenderResponse)
def render_resume_template(
    payload: ResumeTemplateRenderRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeTemplateRenderResponse:
    try:
        template = get_resume_template(payload.template_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    content = payload.content
    if content is None:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        content = profile_to_resume_content(profile)

    return ResumeTemplateRenderResponse(
        template=ResumeTemplateOut.model_validate(template),
        rendered_content=render_resume_template_content(content, payload.template_key),
        sections=[ResumeTemplateSectionOut.model_validate(section) for section in load_resume_sections()],
    )
