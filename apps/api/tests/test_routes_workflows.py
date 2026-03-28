from pathlib import Path

from sqlalchemy.orm import Session

from app.api.routes import applications as applications_routes
from app.api.routes import inbox as inbox_routes
from app.api.routes import jobs as jobs_routes
from app.api.routes import roles as roles_routes
from app.core.config import settings
from app.models.entities import ApplicationRun, ApplicationStep, InboxOtpEvent, Job, TargetRole
from app.schemas.inbox import InboxConnectionCreate, InboxOtpRequest
from app.schemas.roles import TargetRoleIn, TargetRoleSourceIn
from app.services.files import render_resume_pdf
from app.services.inbox import create_inbox_connection
from app.services.resume_themes import seed_resume_themes


def test_role_scrape_now_populates_feed_and_scores(db_session: Session, user, profile, monkeypatch) -> None:
    seed_resume_themes(db_session)
    payload = TargetRoleIn(
        name="Senior Platform Engineer",
        aliases=["Platform Engineer"],
        keywords=["python", "kubernetes", "platform"],
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
    )
    role = roles_routes.create_role(payload, user, db_session)
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

    run = roles_routes.scrape_now(role.id, user, db_session)
    feed = jobs_routes.job_feed(role.id, None, user, db_session)

    assert run.status == "completed"
    assert run.discovered_count == 1
    assert run.inserted_count == 1
    assert len(feed) == 1
    assert feed[0]["role_name"] == "Senior Platform Engineer"
    assert feed[0]["event_type"] == "discovered"
    assert feed[0]["job"]["latest_score"] > 0
    assert feed[0]["job"]["latest_recommendation"] in {"high priority", "maybe", "skip"}


def test_request_application_otp_logs_masked_step(db_session: Session, user, profile) -> None:
    job = Job(
        user_id=user.id,
        title="Senior Full-Stack Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/1",
        description="React FastAPI platform role requiring authorization verification.",
        normalized_description={},
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["react", "fastapi"],
        stack_tags=["react", "fastapi"],
        domain_tags=["saas"],
        source_metadata={},
        latest_score=91.0,
        latest_recommendation="high_priority",
        dedupe_key="acme-senior-full-stack-engineer-1",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    application = applications_routes.prepare(job.id, user, db_session)
    run = ApplicationRun(application_id=application.id, mode="assisted", status="paused", current_step="wait_for_otp")
    db_session.add(run)
    db_session.flush()
    application.latest_run_id = run.id
    db_session.commit()
    db_session.refresh(run)

    create_inbox_connection(
        db_session,
        user_id=user.id,
        provider="gmail",
        email=user.email,
        token="abcdefgh12345678",
        scopes=["gmail.readonly"],
    )

    response = applications_routes.request_otp(
        job.id,
        InboxOtpRequest(
            run_id=run.id,
            sender_hint="greenhouse",
            subject_hint="verification",
            messages=[
                {
                    "sender": "jobs@greenhouse.io",
                    "subject": "Verification code",
                    "body": "Use 482913 to continue your application.",
                }
            ],
        ),
        user,
        db_session,
    )

    steps = db_session.query(ApplicationStep).filter(ApplicationStep.run_id == run.id).all()
    otp_events = db_session.query(InboxOtpEvent).filter(InboxOtpEvent.run_id == run.id).all()

    assert response["status"] == "resolved"
    assert response["code"] == "482913"
    assert response["masked_code"] == "***2913"
    assert len(steps) == 1
    assert steps[0].step_kind == "otp_lookup"
    assert steps[0].status == "completed"
    assert steps[0].masked_output["masked_code"] == "***2913"
    assert "code" not in steps[0].output
    assert len(otp_events) == 1
    assert otp_events[0].code_last4 == "2913"


def test_inbox_connection_response_hides_encrypted_token(db_session: Session, user) -> None:
    connection = inbox_routes.connect_gmail(
        InboxConnectionCreate(
            provider="gmail",
            email=user.email,
            token="abcdefgh12345678",
            scopes=["gmail.readonly"],
        ),
        user,
        db_session,
    )

    stored = inbox_routes.list_connections(user, db_session)

    assert connection.metadata_json["oauth_connected"] is True
    assert "access_token_encrypted" not in connection.metadata_json
    assert stored[0].metadata_json["token_present"] is True
    assert "access_token_encrypted" not in stored[0].metadata_json


def test_oauth_start_returns_provider_authorization_url(monkeypatch, user) -> None:
    monkeypatch.setattr(settings, "google_oauth_client_id", "google-client-id")
    monkeypatch.setattr(settings, "google_oauth_client_secret", "google-client-secret")
    monkeypatch.setattr(settings, "google_oauth_redirect_uri", "http://localhost:8000/inbox/gmail/oauth/callback")

    payload = inbox_routes.oauth_start("gmail", "/settings", user)

    assert payload["provider"] == "gmail"
    assert "accounts.google.com" in payload["authorization_url"]
    assert "state=" in payload["authorization_url"]


def test_oauth_callback_redirects_to_settings_on_success(db_session: Session, user, monkeypatch) -> None:
    fake_connection = create_inbox_connection(
        db_session,
        user_id=user.id,
        provider="gmail",
        email="alex@example.com",
        token="abcdefgh12345678",
        scopes=["gmail.readonly"],
    )
    monkeypatch.setattr(
        "app.api.routes.inbox.complete_oauth_connection",
        lambda db, provider, code, state: (fake_connection, "/settings"),
    )

    response = inbox_routes.oauth_callback("gmail", code="auth-code", state="state-token", db=db_session)

    assert response.status_code == 302
    assert response.headers["location"].startswith(f"{settings.web_origin}/settings?")
    assert "inbox_status=connected" in response.headers["location"]


def test_request_application_otp_fetches_provider_messages_when_none_supplied(db_session: Session, user, profile, monkeypatch) -> None:
    job = Job(
        user_id=user.id,
        title="Senior Full-Stack Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/2",
        description="React FastAPI platform role requiring authorization verification.",
        normalized_description={},
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["react", "fastapi"],
        stack_tags=["react", "fastapi"],
        domain_tags=["saas"],
        source_metadata={},
        latest_score=91.0,
        latest_recommendation="high priority",
        dedupe_key="acme-senior-full-stack-engineer-2",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    application = applications_routes.prepare(job.id, user, db_session)
    run = ApplicationRun(application_id=application.id, mode="assisted", status="paused", current_step="wait_for_otp")
    db_session.add(run)
    db_session.flush()
    application.latest_run_id = run.id
    db_session.commit()

    create_inbox_connection(
        db_session,
        user_id=user.id,
        provider="outlook",
        email=user.email,
        token="abcdefgh12345678",
        scopes=["mail.read"],
    )

    monkeypatch.setattr(
        "app.api.routes.applications.fetch_inbox_messages",
        lambda db, connection, sender_hint="", subject_hint="": [
            {
                "sender": "careers@contoso.com",
                "subject": "Verification code",
                "body": "Your verification code is 654321",
            }
        ],
    )

    response = applications_routes.request_otp(
        job.id,
        InboxOtpRequest(run_id=run.id, sender_hint="contoso", subject_hint="verification", messages=[]),
        user,
        db_session,
    )

    steps = db_session.query(ApplicationStep).filter(ApplicationStep.run_id == run.id).all()

    assert response["status"] == "resolved"
    assert response["code"] == "654321"
    assert response["provider"] == "outlook"
    assert response["message_count"] == 1
    assert steps[0].output["message_count"] == 1


def test_render_resume_pdf_falls_back_to_internal_renderer(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("app.services.files._render_resume_pdf_with_rendercv", lambda content, theme=None: None)
    monkeypatch.setattr(settings, "storage_path", str(tmp_path))

    path = render_resume_pdf(
        {
            "basics": {"full_name": "Alex Builder", "email": "alex@example.com", "location": "Remote"},
            "summary": "Builds reliable systems.",
            "skills": ["Python", "FastAPI"],
            "experience": [{"title": "Staff Engineer", "company": "Forge Labs"}],
            "projects": [],
            "education": [],
        },
        {"slug": "classic-ats-light", "accent_color": "#0f172a", "metadata_json": {}},
    )

    assert Path(path).exists()
    assert Path(path).suffix == ".pdf"
