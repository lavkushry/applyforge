from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Company, CompanyCareerPortal, CompanyContact, JobIngestionRun, TargetRole, User
from app.schemas.companies import (
    CompanyContactCreate,
    CompanyContactOut,
    CompanyCreate,
    CompanyDeleteResponse,
    CompanyDetailOut,
    CompanyOut,
    CompanyPortalCreate,
    CompanyPortalOut,
    CompanyScrapeRequest,
    CompanyUpdate,
)
from app.schemas.roles import JobIngestionRunOut
from app.services.company_directory import normalize_company_name
from app.services.company_ingestion import ingest_company
from app.services.company_portal_resolution import resolve_company_portals as resolve_company_portals_service

router = APIRouter(prefix="/companies", tags=["companies"])


def _company_or_404(company_id: int, user_id: int, db: Session) -> Company:
    company = db.query(Company).filter(Company.id == company_id, Company.user_id == user_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def _portal_or_404(company_id: int, portal_id: int, db: Session) -> CompanyCareerPortal:
    portal = (
        db.query(CompanyCareerPortal)
        .filter(CompanyCareerPortal.id == portal_id, CompanyCareerPortal.company_id == company_id)
        .first()
    )
    if not portal:
        raise HTTPException(status_code=404, detail="Company portal not found")
    return portal


def _contact_or_404(company_id: int, contact_id: int, db: Session) -> CompanyContact:
    contact = (
        db.query(CompanyContact)
        .filter(CompanyContact.id == contact_id, CompanyContact.company_id == company_id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Company contact not found")
    return contact


def _role_or_404(role_id: int, user_id: int, db: Session) -> TargetRole:
    role = db.query(TargetRole).filter(TargetRole.id == role_id, TargetRole.user_id == user_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


def _ensure_company_name_available(company_id: int | None, user_id: int, name: str, db: Session) -> str:
    normalized_name = normalize_company_name(name)
    existing = (
        db.query(Company)
        .filter(Company.user_id == user_id, Company.normalized_name == normalized_name)
        .first()
    )
    if existing and existing.id != company_id:
        raise HTTPException(status_code=409, detail="Company already exists")
    return normalized_name


def _serialize_company(company: Company, db: Session) -> CompanyDetailOut:
    portals = (
        db.query(CompanyCareerPortal)
        .filter(CompanyCareerPortal.company_id == company.id)
        .order_by(CompanyCareerPortal.updated_at.desc(), CompanyCareerPortal.id.desc())
        .all()
    )
    contacts = (
        db.query(CompanyContact)
        .filter(CompanyContact.company_id == company.id)
        .order_by(CompanyContact.updated_at.desc(), CompanyContact.id.desc())
        .all()
    )
    payload = {
        **CompanyOut.model_validate(company).model_dump(mode="json"),
        "portals": [CompanyPortalOut.model_validate(portal).model_dump(mode="json") for portal in portals],
        "contacts": [CompanyContactOut.model_validate(contact).model_dump(mode="json") for contact in contacts],
    }
    return CompanyDetailOut.model_validate(payload)


@router.get("", response_model=list[CompanyOut])
def list_companies(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Company]:
    return (
        db.query(Company)
        .filter(Company.user_id == user.id)
        .order_by(Company.updated_at.desc(), Company.id.desc())
        .all()
    )


@router.post("", response_model=CompanyOut)
def create_company(payload: CompanyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Company:
    normalized_name = _ensure_company_name_available(None, user.id, payload.name, db)
    company = Company(user_id=user.id, normalized_name=normalized_name, **payload.model_dump(mode="json"))
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyDetailOut)
def get_company(company_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CompanyDetailOut:
    company = _company_or_404(company_id, user.id, db)
    return _serialize_company(company, db)


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    payload: CompanyUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Company:
    company = _company_or_404(company_id, user.id, db)
    company.normalized_name = _ensure_company_name_available(company.id, user.id, payload.name, db)
    for key, value in payload.model_dump(mode="json").items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", response_model=CompanyDeleteResponse)
def delete_company(company_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    company = _company_or_404(company_id, user.id, db)
    db.query(CompanyCareerPortal).filter(CompanyCareerPortal.company_id == company.id).delete()
    db.query(CompanyContact).filter(CompanyContact.company_id == company.id).delete()
    db.delete(company)
    db.commit()
    return {"message": "Company deleted"}


@router.get("/{company_id}/portals", response_model=list[CompanyPortalOut])
def list_company_portals(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CompanyCareerPortal]:
    _company_or_404(company_id, user.id, db)
    return (
        db.query(CompanyCareerPortal)
        .filter(CompanyCareerPortal.company_id == company_id)
        .order_by(CompanyCareerPortal.updated_at.desc(), CompanyCareerPortal.id.desc())
        .all()
    )


@router.post("/{company_id}/resolve-portals", response_model=list[CompanyPortalOut])
def resolve_company_portals(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CompanyCareerPortal]:
    company = _company_or_404(company_id, user.id, db)
    return resolve_company_portals_service(db, company=company)


@router.post("/{company_id}/portals", response_model=CompanyPortalOut)
def create_company_portal(
    company_id: int,
    payload: CompanyPortalCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyCareerPortal:
    _company_or_404(company_id, user.id, db)
    portal = CompanyCareerPortal(company_id=company_id, **payload.model_dump(mode="json"))
    db.add(portal)
    db.commit()
    db.refresh(portal)
    return portal


@router.post("/{company_id}/scrape-now", response_model=JobIngestionRunOut)
def scrape_company_jobs(
    company_id: int,
    payload: CompanyScrapeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobIngestionRun:
    company = _company_or_404(company_id, user.id, db)
    role = _role_or_404(payload.role_id, user.id, db)
    if payload.portal_id is not None:
        _portal_or_404(company_id, payload.portal_id, db)
    elif not db.query(CompanyCareerPortal).filter(CompanyCareerPortal.company_id == company.id).first():
        resolve_company_portals_service(db, company=company)
    return ingest_company(db, user_id=user.id, company=company, role=role, portal_id=payload.portal_id)


@router.get("/{company_id}/ingestion-runs", response_model=list[JobIngestionRunOut])
def list_company_ingestion_runs(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JobIngestionRun]:
    _company_or_404(company_id, user.id, db)
    return (
        db.query(JobIngestionRun)
        .filter(JobIngestionRun.company_id == company_id)
        .order_by(JobIngestionRun.started_at.desc())
        .limit(50)
        .all()
    )


@router.put("/{company_id}/portals/{portal_id}", response_model=CompanyPortalOut)
def update_company_portal(
    company_id: int,
    portal_id: int,
    payload: CompanyPortalCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyCareerPortal:
    _company_or_404(company_id, user.id, db)
    portal = _portal_or_404(company_id, portal_id, db)
    for key, value in payload.model_dump(mode="json").items():
        setattr(portal, key, value)
    db.commit()
    db.refresh(portal)
    return portal


@router.delete("/{company_id}/portals/{portal_id}", response_model=CompanyDeleteResponse)
def delete_company_portal(
    company_id: int,
    portal_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _company_or_404(company_id, user.id, db)
    portal = _portal_or_404(company_id, portal_id, db)
    db.delete(portal)
    db.commit()
    return {"message": "Company portal deleted"}


@router.get("/{company_id}/contacts", response_model=list[CompanyContactOut])
def list_company_contacts(
    company_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CompanyContact]:
    _company_or_404(company_id, user.id, db)
    return (
        db.query(CompanyContact)
        .filter(CompanyContact.company_id == company_id)
        .order_by(CompanyContact.updated_at.desc(), CompanyContact.id.desc())
        .all()
    )


@router.post("/{company_id}/contacts", response_model=CompanyContactOut)
def create_company_contact(
    company_id: int,
    payload: CompanyContactCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyContact:
    _company_or_404(company_id, user.id, db)
    contact = CompanyContact(company_id=company_id, **payload.model_dump(mode="json"))
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.put("/{company_id}/contacts/{contact_id}", response_model=CompanyContactOut)
def update_company_contact(
    company_id: int,
    contact_id: int,
    payload: CompanyContactCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanyContact:
    _company_or_404(company_id, user.id, db)
    contact = _contact_or_404(company_id, contact_id, db)
    for key, value in payload.model_dump(mode="json").items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{company_id}/contacts/{contact_id}", response_model=CompanyDeleteResponse)
def delete_company_contact(
    company_id: int,
    contact_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _company_or_404(company_id, user.id, db)
    contact = _contact_or_404(company_id, contact_id, db)
    db.delete(contact)
    db.commit()
    return {"message": "Company contact deleted"}
