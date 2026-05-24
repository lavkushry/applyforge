from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.roles import _serialize_role
from app.db.session import get_db
from app.models.entities import CandidateProfile, InboxConnection, Job, Resume, ResumeVersion, TargetRole, TargetRoleSource, User
from app.schemas.setup import WizardBootstrapRequest, WizardSummaryOut
from app.services.discovery_registry import get_search_template, get_source_preset, load_discovery_registry
from app.services.jobspy_service import prepare_target_role_source_payload

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/wizard", response_model=WizardSummaryOut)
def wizard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    profile_basics_sq = select(CandidateProfile.basics).filter(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()
    profile_skills_sq = select(CandidateProfile.skills).filter(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()

    active_resume_sq = select(Resume.id).filter(Resume.user_id == user.id, Resume.active.is_(True)).limit(1).scalar_subquery()

    inbox_sq = (
        select(InboxConnection.id)
        .filter(InboxConnection.user_id == user.id, InboxConnection.status == "connected")
        .order_by(InboxConnection.updated_at.desc())
        .limit(1)
        .scalar_subquery()
    )

    role_count_sq = select(func.count(TargetRole.id)).filter(TargetRole.user_id == user.id).scalar_subquery()
    job_count_sq = select(func.count(Job.id)).filter(Job.user_id == user.id, Job.active.is_(True)).scalar_subquery()

    tailored_resume_count_sq = (
        select(func.count(ResumeVersion.id))
        .join(Resume, Resume.id == ResumeVersion.resume_id)
        .filter(Resume.user_id == user.id)
        .scalar_subquery()
    )

    stmt = select(
        profile_basics_sq.label("basics"),
        profile_skills_sq.label("skills"),
        active_resume_sq.label("has_resume"),
        inbox_sq.label("has_inbox"),
        role_count_sq.label("role_count"),
        job_count_sq.label("job_count"),
        tailored_resume_count_sq.label("tailored_count")
    )

    result = db.execute(stmt).first()

    profile_ready = bool(result and result.basics and result.basics.get("full_name") and result.skills)
    resume_ready = bool(result and result.has_resume)
    inbox_ready = bool(result and result.has_inbox)

    role_count = result.role_count if result else 0
    job_count = result.job_count if result else 0
    tailored_resume_count = result.tailored_count if result else 0

    steps = [
        {
            "key": "profile",
            "title": "Complete master profile",
            "description": "Structured candidate facts drive scoring, tailoring, and safe answer reuse.",
            "status": "complete" if profile_ready else "needs_action",
            "href": "/profile",
        },
        {
            "key": "resume",
            "title": "Upload or parse a resume",
            "description": "A parsed resume unlocks tailoring, export, and apply packets.",
            "status": "complete" if resume_ready else "needs_action",
            "href": "/resume",
        },
        {
            "key": "roles",
            "title": "Define a role strategy",
            "description": "Role strategies tell ApplyForge what to discover, score, and automate.",
            "status": "complete" if role_count else "needs_action",
            "href": "/roles",
        },
        {
            "key": "inbox",
            "title": "Connect inbox access",
            "description": "Optional but useful for OTP retrieval during assisted applications.",
            "status": "complete" if inbox_ready else "optional",
            "href": "/settings",
        },
        {
            "key": "jobs",
            "title": "Start discovery",
            "description": "Run a scrape or manual import to populate the realtime job feed.",
            "status": "complete" if job_count else "needs_action",
            "href": "/jobs",
        },
    ]

    registry = load_discovery_registry()
    return {
        "profile_ready": profile_ready,
        "resume_ready": resume_ready,
        "inbox_ready": inbox_ready,
        "role_count": role_count,
        "job_count": job_count,
        "tailored_resume_count": tailored_resume_count,
        "steps": steps,
        "recommended_templates": registry["search_templates"],
        "blocked_domains": registry["blocked_domains"],
    }


@router.post("/wizard/bootstrap-role")
def bootstrap_role(
    payload: WizardBootstrapRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    template = get_search_template(payload.template_key)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    existing = db.query(TargetRole).filter(TargetRole.user_id == user.id, TargetRole.name == template["role_name"]).first()
    if existing:
        return _serialize_role(existing, db).model_dump(mode="json")

    role = TargetRole(
        user_id=user.id,
        name=template["role_name"],
        aliases=template.get("aliases", []),
        keywords=template.get("keywords", []),
        preferred_locations=template.get("preferred_locations", []),
        remote_preference=template.get("remote_preference", "remote"),
        salary_target="",
        visa_preference="unknown",
        seniority=template.get("seniority", "mid"),
        companies_include=[],
        companies_exclude=[],
        scrape_cadence_minutes=30,
        automation_enabled=True,
        min_auto_apply_score=85.0,
        active=True,
    )
    db.add(role)
    db.flush()

    for preset_key in template.get("source_preset_keys", []):
        preset = get_source_preset(preset_key)
        if not preset:
            continue
        db.add(
            TargetRoleSource(
                role_id=role.id,
                **prepare_target_role_source_payload(
                    kind=preset["kind"],
                    label=preset["label"],
                    base_url=preset["base_url"],
                    config=preset.get("config", {}),
                    enabled=True,
                    role_name=template["role_name"],
                    preferred_locations=template.get("preferred_locations", []),
                    remote_preference=template.get("remote_preference", "remote"),
                ),
            )
        )

    db.commit()
    db.refresh(role)
    return _serialize_role(role, db).model_dump(mode="json")
