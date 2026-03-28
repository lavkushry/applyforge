from sqlalchemy.orm import Session

from app.api.routes import companies as companies_routes
from app.api.routes import jobs as jobs_routes
from app.api.routes import roles as roles_routes
from app.models.entities import CompanyCareerPortal, Job, JobIngestionRun, TargetRole
from app.schemas.companies import (
    CompanyContactCreate,
    CompanyCreate,
    CompanyPortalCreate,
    CompanyScrapeRequest,
    CompanyUpdate,
)
from app.schemas.jobs import JobCreate
from app.schemas.roles import TargetRoleIn, TargetRoleSourceIn


def test_company_crud_and_nested_resources(db_session: Session, user) -> None:
    company = companies_routes.create_company(
        CompanyCreate(
            name="Acme",
            website_url="https://acme.dev",
            careers_url="https://careers.acme.dev",
            linkedin_url="https://linkedin.com/company/acme",
            hq_location="Remote",
            industry="Developer Tools",
            notes="Priority hiring target",
            active=True,
        ),
        user,
        db_session,
    )

    companies = companies_routes.list_companies(user, db_session)
    assert len(companies) == 1
    assert companies[0].normalized_name == "acme"

    portal = companies_routes.create_company_portal(
        company.id,
        CompanyPortalCreate(
            provider_kind="greenhouse",
            base_url="https://boards.greenhouse.io/acme",
            board_token="acme",
            health_status="healthy",
            supports_structured_fetch=True,
            notes="Canonical board",
        ),
        user,
        db_session,
    )
    contact = companies_routes.create_company_contact(
        company.id,
        CompanyContactCreate(
            full_name="Jamie Recruiter",
            title="Senior Recruiter",
            email="jamie@acme.dev",
            linkedin_url="https://linkedin.com/in/jamie-recruiter",
            contact_type="recruiter",
            source="manual",
            source_url="https://linkedin.com/in/jamie-recruiter",
            confidence=0.91,
            notes="Reached out in March",
        ),
        user,
        db_session,
    )

    updated_company = companies_routes.update_company(
        company.id,
        CompanyUpdate(
            name="Acme",
            website_url="https://acme.dev",
            careers_url="https://jobs.acme.dev",
            linkedin_url="https://linkedin.com/company/acme",
            hq_location="New York, NY",
            industry="Developer Tools",
            notes="Updated careers endpoint",
            active=True,
        ),
        user,
        db_session,
    )
    detail = companies_routes.get_company(company.id, user, db_session)

    assert updated_company.careers_url == "https://jobs.acme.dev"
    assert len(detail.portals) == 1
    assert len(detail.contacts) == 1
    assert detail.portals[0].id == portal.id
    assert detail.contacts[0].id == contact.id

    updated_portal = companies_routes.update_company_portal(
        company.id,
        portal.id,
        CompanyPortalCreate(
            provider_kind="greenhouse",
            base_url="https://boards.greenhouse.io/acme-inc",
            board_token="acme-inc",
            health_status="healthy",
            supports_structured_fetch=True,
            notes="Updated board token",
        ),
        user,
        db_session,
    )
    updated_contact = companies_routes.update_company_contact(
        company.id,
        contact.id,
        CompanyContactCreate(
            full_name="Jamie Recruiter",
            title="Lead Recruiter",
            email="jamie@acme.dev",
            linkedin_url="https://linkedin.com/in/jamie-recruiter",
            contact_type="recruiter",
            source="manual",
            source_url="https://linkedin.com/in/jamie-recruiter",
            confidence=0.95,
            notes="Verified",
        ),
        user,
        db_session,
    )

    assert updated_portal.board_token == "acme-inc"
    assert updated_contact.title == "Lead Recruiter"

    delete_portal = companies_routes.delete_company_portal(company.id, portal.id, user, db_session)
    delete_contact = companies_routes.delete_company_contact(company.id, contact.id, user, db_session)

    assert delete_portal["message"] == "Company portal deleted"
    assert delete_contact["message"] == "Company contact deleted"
    assert companies_routes.get_company(company.id, user, db_session).portals == []
    assert companies_routes.get_company(company.id, user, db_session).contacts == []


def test_manual_job_creation_links_existing_company(db_session: Session, user) -> None:
    company = companies_routes.create_company(
        CompanyCreate(name="Acme", website_url="https://acme.dev", active=True),
        user,
        db_session,
    )

    job = jobs_routes.create_job(
        JobCreate(
            title="Senior Platform Engineer",
            company="Acme",
            role_id=None,
            location="Remote",
            remote_type="remote",
            salary="$180k",
            source="manual",
            application_url="https://careers.acme.dev/jobs/123",
            description="Python and Kubernetes platform engineering role with reliability ownership.",
            seniority="senior",
            employment_type="full-time",
            visa_support="unknown",
            tags=["python", "kubernetes"],
        ),
        user,
        db_session,
    )

    assert job.company_id == company.id
    stored = db_session.query(Job).filter(Job.id == job.id).first()
    assert stored is not None
    assert stored.company_id == company.id


def test_role_ingestion_links_job_to_company_directory(db_session: Session, user, profile, monkeypatch) -> None:
    companies_routes.create_company(
        CompanyCreate(name="Acme", website_url="https://acme.dev", active=True),
        user,
        db_session,
    )
    role = roles_routes.create_role(
        TargetRoleIn(
            name="Senior Platform Engineer",
            aliases=["Platform Engineer"],
            keywords=["python", "platform", "kubernetes"],
            preferred_locations=["Remote"],
            remote_preference="remote",
            salary_target="$180k+",
            visa_preference="no_sponsorship_needed",
            seniority="senior",
            companies_include=[],
            companies_exclude=[],
            scrape_cadence_minutes=15,
            automation_enabled=True,
            min_auto_apply_score=85,
            active=True,
            sources=[
                TargetRoleSourceIn(
                    kind="greenhouse_board",
                    label="Acme",
                    base_url="https://boards.greenhouse.io/acme",
                    config={"board_token": "acme"},
                    enabled=True,
                )
            ],
        ),
        user,
        db_session,
    )
    role_row = db_session.query(TargetRole).filter(TargetRole.id == role.id).first()
    assert role_row is not None

    def fake_fetch_jobs_for_source(_source) -> list[dict]:
        return [
            {
                "title": "Senior Platform Engineer",
                "company": "Acme",
                "location": "Remote",
                "remote_type": "remote",
                "salary": "$190,000",
                "application_url": "https://jobs.acme.dev/platform",
                "description": "Python Kubernetes platform automation and reliability engineering.",
                "source": "greenhouse",
                "source_metadata": {"source_label": "Acme"},
            }
        ]

    monkeypatch.setattr("app.services.role_ingestion.fetch_jobs_for_source", fake_fetch_jobs_for_source)

    roles_routes.scrape_now(role.id, user, db_session)

    job = db_session.query(Job).filter(Job.company == "Acme").first()
    assert job is not None
    assert job.company_id is not None


def test_company_resolve_portals_creates_structured_greenhouse_portal(db_session: Session, user) -> None:
    company = companies_routes.create_company(
        CompanyCreate(
            name="Acme",
            website_url="https://acme.dev",
            careers_url="https://boards.greenhouse.io/acme",
            active=True,
        ),
        user,
        db_session,
    )

    portals = companies_routes.resolve_company_portals(company.id, user, db_session)

    assert len(portals) == 1
    assert portals[0].provider_kind == "greenhouse"
    assert portals[0].board_token == "acme"
    assert portals[0].supports_structured_fetch is True
    assert portals[0].resolution_metadata["resolved_from"] == "https://boards.greenhouse.io/acme"


def test_company_scrape_run_tracks_company_and_portal_context(db_session: Session, user, profile, monkeypatch) -> None:
    company = companies_routes.create_company(
        CompanyCreate(
            name="Acme",
            website_url="https://acme.dev",
            careers_url="https://boards.greenhouse.io/acme",
            active=True,
        ),
        user,
        db_session,
    )
    portal = companies_routes.create_company_portal(
        company.id,
        CompanyPortalCreate(
            provider_kind="greenhouse",
            base_url="https://boards.greenhouse.io/acme",
            board_token="acme",
            supports_structured_fetch=True,
            notes="Canonical board",
        ),
        user,
        db_session,
    )
    role = roles_routes.create_role(
        TargetRoleIn(
            name="Senior Platform Engineer",
            aliases=["Platform Engineer"],
            keywords=["python", "platform", "kubernetes"],
            preferred_locations=["Remote"],
            remote_preference="remote",
            salary_target="$180k+",
            visa_preference="no_sponsorship_needed",
            seniority="senior",
            companies_include=[],
            companies_exclude=[],
            scrape_cadence_minutes=15,
            automation_enabled=True,
            min_auto_apply_score=85,
            active=True,
            sources=[],
        ),
        user,
        db_session,
    )
    role_row = db_session.query(TargetRole).filter(TargetRole.id == role.id).first()
    assert role_row is not None

    def fake_fetch_jobs_for_source(_source) -> list[dict]:
        return [
            {
                "title": "Senior Platform Engineer",
                "company": "Acme",
                "location": "Remote",
                "remote_type": "remote",
                "salary": "$190,000",
                "application_url": "https://jobs.acme.dev/platform",
                "description": "Python Kubernetes platform automation and reliability engineering.",
                "source": "greenhouse",
                "source_metadata": {"source_label": "Acme"},
            }
        ]

    monkeypatch.setattr("app.services.company_ingestion.fetch_jobs_for_source", fake_fetch_jobs_for_source)
    monkeypatch.setattr("app.services.company_ingestion.dispatch_job_enrichment", lambda **_kwargs: "task-123")

    run = companies_routes.scrape_company_jobs(
        company.id,
        CompanyScrapeRequest(role_id=role.id, portal_id=portal.id),
        user,
        db_session,
    )
    runs = companies_routes.list_company_ingestion_runs(company.id, user, db_session)

    assert run.company_id == company.id
    assert run.company_portal_id == portal.id
    assert run.role_id == role.id
    assert run.trigger_kind == "company_portal_scrape"
    assert run.source_count == 1
    assert run.discovered_count == 1
    assert run.inserted_count == 1
    assert len(runs) == 1
    assert runs[0].id == run.id

    stored_portal = db_session.query(CompanyCareerPortal).filter(CompanyCareerPortal.id == portal.id).first()
    assert stored_portal is not None
    assert stored_portal.last_run_id == run.id
    assert stored_portal.last_job_count == 1
    assert stored_portal.last_success_at is not None
    assert stored_portal.last_error == ""

    job = db_session.query(Job).filter(Job.company == "Acme").first()
    assert job is not None
    assert job.company_id == company.id
    assert job.company_portal_id == portal.id
    assert job.role_id == role.id

    run_row = db_session.query(JobIngestionRun).filter(JobIngestionRun.id == run.id).first()
    assert run_row is not None
    assert run_row.company_id == company.id
    assert run_row.company_portal_id == portal.id
