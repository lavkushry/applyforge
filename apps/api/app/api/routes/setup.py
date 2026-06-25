from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.roles import _serialize_role
from app.db.session import get_db
from app.models.entities import (
    CandidateProfile,
    InboxConnection,
    Job,
    Resume,
    ResumeVersion,
    TargetRole,
    TargetRoleSource,
    User,
)
from app.schemas.setup import WizardBootstrapRequest, WizardSummaryOut
from app.services.discovery_registry import (
    get_search_template,
    get_source_preset,
    load_discovery_registry,
)
from app.services.jobspy_service import prepare_target_role_source_payload

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/wizard", response_model=WizardSummaryOut)
def wizard_summary(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    profile = (
        db.query(CandidateProfile.basics, CandidateProfile.skills)
        .filter(CandidateProfile.user_id == user.id)
        .first()
    )

    # PERFORMANCE OPTIMIZATION: Consolidate 5 independent existence/count queries into a single DB round-trip
    # Expected impact: Eliminates 4 sequential network calls, reducing dashboard initialization latency.
    stats = db.query(
        select(
            select(Resume.id)
            .where(Resume.user_id == user.id, Resume.active.is_(True))
            .exists()
        )
        .scalar_subquery()
        .label("resume_ready"),
        select(
            select(InboxConnection.id)
            .where(
                InboxConnection.user_id == user.id,
                InboxConnection.status == "connected",
            )
            .exists()
        )
        .scalar_subquery()
        .label("inbox_ready"),
        select(func.count(TargetRole.id))
        .where(TargetRole.user_id == user.id)
        .scalar_subquery()
        .label("role_count"),
        select(func.count(Job.id))
        .where(Job.user_id == user.id, Job.active.is_(True))
        .scalar_subquery()
        .label("job_count"),
        select(func.count(ResumeVersion.id))
        .where(
            ResumeVersion.resume_id.in_(
                select(Resume.id).where(Resume.user_id == user.id)
            )
        )
        .scalar_subquery()
        .label("tailored_resume_count"),
    ).first()

    role_count = stats.role_count if stats else 0
    job_count = stats.job_count if stats else 0
    tailored_resume_count = stats.tailored_resume_count if stats else 0

    profile_ready = bool(
        profile
        and profile.basics
        and profile.basics.get("full_name")
        and profile.skills
    )
    resume_ready = bool(stats.resume_ready if stats else False)
    inbox_ready = bool(stats.inbox_ready if stats else False)

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

    existing = (
        db.query(TargetRole)
        .filter(TargetRole.user_id == user.id, TargetRole.name == template["role_name"])
        .first()
    )
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
