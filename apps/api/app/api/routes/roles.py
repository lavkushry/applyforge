from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import JobFeedEvent, JobIngestionRun, TargetRole, TargetRoleSource, User
from app.schemas.roles import JobIngestionRunOut, TargetRoleIn, TargetRoleOut, TargetRoleSourceOut
from app.services.role_ingestion import ingest_target_role

router = APIRouter(prefix="/roles", tags=["roles"])


def _role_or_404(role_id: int, user_id: int, db: Session) -> TargetRole:
    role = db.query(TargetRole).filter(TargetRole.id == role_id, TargetRole.user_id == user_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


def _serialize_role(role: TargetRole, db: Session) -> TargetRoleOut:
    sources = db.query(TargetRoleSource).filter(TargetRoleSource.role_id == role.id).order_by(TargetRoleSource.id.asc()).all()
    payload = {
        "id": role.id,
        "user_id": role.user_id,
        "name": role.name,
        "aliases": role.aliases,
        "keywords": role.keywords,
        "preferred_locations": role.preferred_locations,
        "remote_preference": role.remote_preference,
        "salary_target": role.salary_target,
        "visa_preference": role.visa_preference,
        "seniority": role.seniority,
        "companies_include": role.companies_include,
        "companies_exclude": role.companies_exclude,
        "scrape_cadence_minutes": role.scrape_cadence_minutes,
        "automation_enabled": role.automation_enabled,
        "min_auto_apply_score": role.min_auto_apply_score,
        "active": role.active,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "sources": [TargetRoleSourceOut.model_validate(source).model_dump(mode="json") for source in sources],
    }
    return TargetRoleOut.model_validate(payload)


@router.get("", response_model=list[TargetRoleOut])
def list_roles(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[TargetRoleOut]:
    roles = db.query(TargetRole).filter(TargetRole.user_id == user.id).order_by(TargetRole.updated_at.desc()).all()
    return [_serialize_role(role, db) for role in roles]


@router.post("", response_model=TargetRoleOut)
def create_role(payload: TargetRoleIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TargetRoleOut:
    role = TargetRole(user_id=user.id, **payload.model_dump(mode="json", exclude={"sources"}))
    db.add(role)
    db.flush()
    for source in payload.sources:
        db.add(TargetRoleSource(role_id=role.id, **source.model_dump(mode="json")))
    db.commit()
    db.refresh(role)
    return _serialize_role(role, db)


@router.put("/{role_id}", response_model=TargetRoleOut)
def update_role(role_id: int, payload: TargetRoleIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TargetRoleOut:
    role = _role_or_404(role_id, user.id, db)
    for key, value in payload.model_dump(mode="json", exclude={"sources"}).items():
        setattr(role, key, value)
    db.query(TargetRoleSource).filter(TargetRoleSource.role_id == role.id).delete()
    db.flush()
    for source in payload.sources:
        db.add(TargetRoleSource(role_id=role.id, **source.model_dump(mode="json")))
    db.commit()
    db.refresh(role)
    return _serialize_role(role, db)


@router.post("/{role_id}/scrape-now", response_model=JobIngestionRunOut)
def scrape_now(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> JobIngestionRun:
    role = _role_or_404(role_id, user.id, db)
    return ingest_target_role(db, user.id, role)


@router.get("/ingestion-runs", response_model=list[JobIngestionRunOut])
def list_ingestion_runs(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[JobIngestionRun]:
    role_ids = [role.id for role in db.query(TargetRole).filter(TargetRole.user_id == user.id).all()]
    if not role_ids:
        return []
    return (
        db.query(JobIngestionRun)
        .filter(JobIngestionRun.role_id.in_(role_ids))
        .order_by(JobIngestionRun.started_at.desc())
        .limit(50)
        .all()
    )


@router.get("/{role_id}/events")
def list_role_events(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    role = _role_or_404(role_id, user.id, db)
    events = (
        db.query(JobFeedEvent)
        .filter(JobFeedEvent.role_id == role.id)
        .order_by(JobFeedEvent.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": event.id,
            "role_id": event.role_id,
            "job_id": event.job_id,
            "run_id": event.run_id,
            "event_type": event.event_type,
            "event_metadata": event.event_metadata,
            "created_at": event.created_at,
        }
        for event in events
    ]
