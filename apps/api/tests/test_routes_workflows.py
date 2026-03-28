from pathlib import Path

from sqlalchemy.orm import Session

from app.api.routes import setup as setup_routes
from app.api.routes import application_runs as application_runs_routes
from app.api.routes import applications as applications_routes
from app.api.routes import inbox as inbox_routes
from app.api.routes import jobs as jobs_routes
from app.api.routes import roles as roles_routes
from app.core.config import settings
from app.models.entities import ApplicationRun, ApplicationStep, CoverLetter, InboxOtpEvent, Job, Resume, ResumeVersion, TargetRole, UploadedFile
from app.schemas.inbox import InboxConnectionCreate, InboxOtpRequest
from app.schemas.roles import TargetRoleIn, TargetRoleSourceIn
from app.services.files import render_resume_pdf
from app.services.inbox import create_inbox_connection
from app.services.resume_themes import seed_resume_themes


def test_roles_source_presets_return_packaged_catalog(db_session: Session, user) -> None:
    payload = roles_routes.source_presets(user)

    assert payload["source_presets"]
    assert payload["search_templates"]
    assert "linkedin.com" in payload["blocked_domains"]
    assert any(item["kind"] == "workday_board" for item in payload["source_presets"])
    assert any(item["key"] == "senior-fullstack-remote" for item in payload["search_templates"])


def test_setup_wizard_summary_and_bootstrap_role(db_session: Session, user, profile) -> None:
    summary = setup_routes.wizard_summary(user, db_session)

    assert summary["profile_ready"] is True
    assert summary["resume_ready"] is False
    assert summary["role_count"] == 0
    assert summary["recommended_templates"]
    assert any(step["key"] == "roles" and step["status"] == "needs_action" for step in summary["steps"])

    bootstrapped = setup_routes.bootstrap_role(
        setup_routes.WizardBootstrapRequest(template_key="senior-fullstack-remote"),
        user,
        db_session,
    )

    assert bootstrapped["name"] == "Senior Full-Stack Engineer"
    assert bootstrapped["sources"]
    assert any(source["kind"] == "workday_board" for source in bootstrapped["sources"])

    repeat = setup_routes.bootstrap_role(
        setup_routes.WizardBootstrapRequest(template_key="senior-fullstack-remote"),
        user,
        db_session,
    )
    assert repeat["id"] == bootstrapped["id"]


def test_workday_source_fetcher_maps_common_payload(monkeypatch) -> None:
    from app.services.role_ingestion import fetch_jobs_for_source

    source = roles_routes.TargetRoleSource(
        role_id=1,
        kind="workday_board",
        label="Acme Workday",
        base_url="https://acme.wd1.myworkdayjobs.com/careers",
        config={"api_url": "https://acme.wd1.myworkdayjobs.com/wday/cxs/acme/careers/jobs"},
        enabled=True,
    )

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "jobPostings": [
                    {
                        "title": "Staff Platform Engineer",
                        "locationsText": "Remote",
                        "externalPath": "/job/Remote/Staff-Platform-Engineer_JR123",
                        "bulletFields": ["Platform", "Remote"],
                        "jobDescription": "Own platform systems and developer experience.",
                    }
                ]
            }

    monkeypatch.setattr("app.services.role_ingestion.httpx.get", lambda *args, **kwargs: FakeResponse())

    jobs = fetch_jobs_for_source(source)

    assert len(jobs) == 1
    assert jobs[0]["source"] == "workday"
    assert jobs[0]["title"] == "Staff Platform Engineer"
    assert jobs[0]["application_url"].startswith("https://acme.wd1.myworkdayjobs.com/careers/")


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
    monkeypatch.setattr(
        "app.services.role_ingestion.dispatch_job_enrichment",
        lambda *, run_id, job_id, role_id, user_id, source_context=None: _sync_enrichment_dispatch(
            db_session,
            run_id=run_id,
            job_id=job_id,
            role_id=role_id,
            user_id=user_id,
            source_context=source_context,
        ),
    )

    run = roles_routes.scrape_now(role.id, user, db_session)
    feed = jobs_routes.job_feed(role.id, None, user, db_session)
    feed_event_types = {item["event_type"] for item in feed}
    feed_job = next(item["job"] for item in feed if item["job"])

    assert run.status == "completed"
    assert run.discovered_count == 1
    assert run.inserted_count == 1
    assert run.enriched_count == 1
    assert {"discovered", "enriched", "score_changed"}.issubset(feed_event_types)
    assert next(item["role_name"] for item in feed if item["role_name"]) == "Senior Platform Engineer"
    assert feed_job["latest_score"] > 0
    assert feed_job["latest_recommendation"] in {"high priority", "maybe", "skip"}
    assert feed_job["enrichment_status"] == "completed"
    assert feed_job["enrichment_revision"] >= 1
    assert feed_job["source_document_file_id"] is not None


def _sync_enrichment_dispatch(db_session: Session, *, run_id: int, job_id: int, role_id: int, user_id: int, source_context: dict | None) -> str:
    run = db_session.query(roles_routes.JobIngestionRun).filter(roles_routes.JobIngestionRun.id == run_id).first()
    job = db_session.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
    role = db_session.query(TargetRole).filter(TargetRole.id == role_id, TargetRole.user_id == user_id).first()
    assert run is not None
    assert job is not None
    assert role is not None
    from app.services.role_ingestion import process_job_enrichment

    process_job_enrichment(
        db_session,
        run=run,
        user_id=user_id,
        role=role,
        job=job,
        source_context=source_context,
    )
    return f"sync-{job_id}"


def test_role_scrape_now_dispatches_pending_enrichment(db_session: Session, user, profile, monkeypatch) -> None:
    payload = TargetRoleIn(
        name="Founding Platform Engineer",
        aliases=["Platform Engineer"],
        keywords=["python", "platform"],
        preferred_locations=["Remote"],
        remote_preference="remote",
        salary_target="$180k+",
        visa_preference="unknown",
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

    monkeypatch.setattr(
        "app.services.role_ingestion.fetch_jobs_for_source",
        lambda _source: [
            {
                "title": "Founding Platform Engineer",
                "company": "Acme",
                "location": "Remote",
                "remote_type": "remote",
                "salary": "$190,000",
                "application_url": "https://jobs.acme.dev/founding-platform",
                "description": "Python platform automation and reliability engineering.",
                "source": "greenhouse",
                "source_metadata": {"source_label": "Acme"},
            }
        ],
    )
    dispatched: list[dict] = []
    monkeypatch.setattr(
        "app.services.role_ingestion.dispatch_job_enrichment",
        lambda *, run_id, job_id, role_id, user_id, source_context=None: dispatched.append(
            {
                "run_id": run_id,
                "job_id": job_id,
                "role_id": role_id,
                "user_id": user_id,
                "source_context": source_context,
            }
        )
        or "task-queued",
    )

    run = roles_routes.scrape_now(role.id, user, db_session)
    feed = jobs_routes.job_feed(role.id, None, user, db_session)
    job = db_session.query(Job).filter(Job.role_id == role.id).first()

    assert run.status == "running"
    assert run.discovered_count == 1
    assert run.enriched_count == 0
    assert len(dispatched) == 1
    assert feed[0]["event_type"] == "discovered"
    assert job is not None
    assert job.enrichment_status == "pending"
    assert job.latest_score == 0.0


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

    prepared = applications_routes.prepare(job.id, user, db_session)
    run = ApplicationRun(application_id=prepared["application"]["id"], mode="assisted", status="paused", current_step="wait_for_otp")
    db_session.add(run)
    db_session.flush()
    application = db_session.query(applications_routes.Application).filter(applications_routes.Application.id == prepared["application"]["id"]).first()
    assert application is not None
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


def test_oauth_provider_statuses_report_missing_config(monkeypatch, user) -> None:
    monkeypatch.setattr(settings, "google_oauth_client_id", "")
    monkeypatch.setattr(settings, "google_oauth_client_secret", "")
    monkeypatch.setattr(settings, "google_oauth_redirect_uri", "http://localhost:8000/inbox/gmail/oauth/callback")
    monkeypatch.setattr(settings, "microsoft_oauth_client_id", "")
    monkeypatch.setattr(settings, "microsoft_oauth_client_secret", "")
    monkeypatch.setattr(settings, "microsoft_oauth_redirect_uri", "http://localhost:8000/inbox/outlook/oauth/callback")

    payload = inbox_routes.oauth_provider_statuses(user)

    assert len(payload) == 2
    gmail = next(item for item in payload if item.provider == "gmail")
    outlook = next(item for item in payload if item.provider == "outlook")
    assert gmail.configured is False
    assert "GOOGLE_OAUTH_CLIENT_ID" in gmail.missing_env
    assert outlook.configured is False
    assert "MICROSOFT_OAUTH_CLIENT_ID" in outlook.missing_env


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

    prepared = applications_routes.prepare(job.id, user, db_session)
    run = ApplicationRun(application_id=prepared["application"]["id"], mode="assisted", status="paused", current_step="wait_for_otp")
    db_session.add(run)
    db_session.flush()
    application = db_session.query(applications_routes.Application).filter(applications_routes.Application.id == prepared["application"]["id"]).first()
    assert application is not None
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


def test_prepare_returns_packet_summary_with_readiness(db_session: Session, user, profile) -> None:
    uploaded = UploadedFile(
        user_id=user.id,
        original_name="tailored-resume.pdf",
        path="/tmp/tailored-resume.pdf",
        mime_type="application/pdf",
        size_bytes=1200,
        checksum="resume-checksum",
    )
    db_session.add(uploaded)
    db_session.flush()

    resume = Resume(user_id=user.id, title="Master Resume", parse_status="parsed", active=True)
    db_session.add(resume)
    db_session.flush()

    version = ResumeVersion(
        resume_id=resume.id,
        title="Acme Resume",
        variant="tailored",
        content_json={"summary": "Tailored summary"},
        export_status="exported",
        pdf_file_id=uploaded.id,
    )
    db_session.add(version)

    job = Job(
        user_id=user.id,
        title="Senior Full-Stack Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/prepare",
        description="React FastAPI role requiring communication and platform ownership.",
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
        dedupe_key="acme-senior-full-stack-engineer-prepare",
    )
    db_session.add(job)
    db_session.flush()

    cover_letter = CoverLetter(job_id=job.id, content="Concise cover letter", tone="concise")
    db_session.add(cover_letter)
    db_session.commit()
    db_session.refresh(job)

    payload = applications_routes.prepare(job.id, user, db_session)

    assert payload["application"]["job_id"] == job.id
    assert payload["packet"]["ready"] is True
    assert payload["packet"]["resume_file_id"] == uploaded.id
    assert payload["packet"]["cover_letter_id"] == cover_letter.id
    assert payload["packet"]["missing_answers"] == []
    assert payload["packet"]["risk_summary"] == []


def test_run_assisted_queues_worker_task_and_stores_prepared_payload(db_session: Session, user, profile, monkeypatch) -> None:
    uploaded = UploadedFile(
        user_id=user.id,
        original_name="resume.pdf",
        path="/tmp/resume.pdf",
        mime_type="application/pdf",
        size_bytes=900,
        checksum="resume-checksum",
    )
    db_session.add(uploaded)
    db_session.flush()
    resume = Resume(user_id=user.id, title="Master Resume", parse_status="parsed", active=True)
    db_session.add(resume)
    db_session.flush()
    db_session.add(
        ResumeVersion(
            resume_id=resume.id,
            job_id=None,
            title="Latest Resume",
            variant="tailored",
            content_json={"summary": "Tailored summary"},
            export_status="exported",
            pdf_file_id=uploaded.id,
        )
    )
    job = Job(
        user_id=user.id,
        title="Senior Full-Stack Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/run-assisted",
        description="React FastAPI role requiring communication and platform ownership.",
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
        dedupe_key="acme-senior-full-stack-engineer-run-assisted",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    monkeypatch.setattr("app.api.routes.applications.dispatch_application_run", lambda mode, run_id, packet: "task-123")

    run = applications_routes.run_assisted(job.id, user, db_session)
    stored = db_session.query(ApplicationRun).filter(ApplicationRun.id == run.id).first()

    assert stored is not None
    assert stored.status == "queued"
    assert stored.external_task_id == "task-123"
    assert stored.prepared_payload["job"]["application_url"] == job.application_url
    assert stored.prepared_payload["resume_file_id"] == uploaded.id
    assert stored.prepared_payload["mode"] == "assisted"


def test_run_draft_creates_completed_packet_review_run(db_session: Session, user, profile) -> None:
    uploaded = UploadedFile(
        user_id=user.id,
        original_name="resume.pdf",
        path="/tmp/resume.pdf",
        mime_type="application/pdf",
        size_bytes=900,
        checksum="resume-checksum",
    )
    db_session.add(uploaded)
    db_session.flush()
    resume = Resume(user_id=user.id, title="Master Resume", parse_status="parsed", active=True)
    db_session.add(resume)
    db_session.flush()
    db_session.add(
        ResumeVersion(
            resume_id=resume.id,
            job_id=None,
            title="Latest Resume",
            variant="tailored",
            content_json={"summary": "Tailored summary"},
            export_status="exported",
            pdf_file_id=uploaded.id,
        )
    )
    job = Job(
        user_id=user.id,
        title="Senior Full-Stack Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/run-draft",
        description="React FastAPI role requiring communication and platform ownership.",
        normalized_description={
            "must_have_skills": ["React", "FastAPI"],
            "nice_to_have_skills": ["Docker"],
            "extraction_confidence": 0.88,
        },
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["react", "fastapi"],
        stack_tags=["react", "fastapi"],
        domain_tags=["saas"],
        source_metadata={},
        enrichment_status="completed",
        enrichment_revision=1,
        latest_score=91.0,
        latest_score_revision=1,
        latest_recommendation="high priority",
        dedupe_key="acme-senior-full-stack-engineer-run-draft",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    run = applications_routes.run_draft(job.id, user, db_session)
    steps = db_session.query(ApplicationStep).filter(ApplicationStep.run_id == run.id).all()

    assert run.mode == "draft"
    assert run.status == "completed"
    assert steps[-1].name == "draft_packet_ready"
    assert steps[-1].status == "completed"


def test_applications_dashboard_and_serialization_include_pipeline_state(db_session: Session, user, profile) -> None:
    uploaded = UploadedFile(
        user_id=user.id,
        original_name="resume.pdf",
        path="/tmp/resume.pdf",
        mime_type="application/pdf",
        size_bytes=900,
        checksum="resume-checksum",
    )
    db_session.add(uploaded)
    db_session.flush()
    resume = Resume(user_id=user.id, title="Master Resume", parse_status="parsed", active=True)
    db_session.add(resume)
    db_session.flush()
    db_session.add(
        ResumeVersion(
            resume_id=resume.id,
            job_id=1,
            title="Acme Resume",
            variant="tailored",
            content_json={"summary": "Tailored summary"},
            export_status="exported",
            pdf_file_id=uploaded.id,
        )
    )
    job = Job(
        id=1,
        user_id=user.id,
        title="Senior Full-Stack Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/dashboard",
        description="React FastAPI role requiring communication and platform ownership.",
        normalized_description={
            "must_have_skills": ["React", "FastAPI"],
            "nice_to_have_skills": ["Docker"],
            "extraction_confidence": 0.88,
        },
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["react", "fastapi"],
        stack_tags=["react", "fastapi"],
        domain_tags=["saas"],
        source_metadata={},
        enrichment_status="completed",
        enrichment_revision=1,
        latest_score=91.0,
        latest_score_revision=1,
        latest_recommendation="high priority",
        dedupe_key="acme-senior-full-stack-engineer-dashboard",
    )
    db_session.add(job)
    db_session.flush()
    db_session.add(CoverLetter(job_id=job.id, content="Concise cover letter", tone="concise"))
    application = applications_routes._ensure_application(job.id, user.id, db_session)
    run = ApplicationRun(application_id=application.id, mode="assisted", status="paused", current_step="pause_before_submit")
    db_session.add(run)
    db_session.flush()
    db_session.add(
        ApplicationStep(
            run_id=run.id,
            name="manual_question_review_required",
            status="paused",
            step_kind="field_detection",
            requires_approval=True,
            output={"reason": "Manual review required for unsupported screening questions"},
        )
    )
    application.latest_run_id = run.id
    db_session.commit()

    applications = applications_routes.list_applications(user, db_session)
    dashboard = applications_routes.dashboard(user, db_session)

    assert applications[0]["pipeline"]["enriched"] is True
    assert applications[0]["pipeline"]["scored"] is True
    assert applications[0]["pipeline"]["tailored"] is True
    assert applications[0]["pipeline"]["cover_letter"] is True
    assert applications[0]["latest_run"]["status"] == "paused"
    assert applications[0]["action_required"]["name"] == "manual_question_review_required"
    assert applications[0]["action_required"]["step_kind"] == "field_detection"
    assert "unsupported screening questions" in applications[0]["action_required"]["reason"]
    assert dashboard["pipeline_counts"]["tracked"] == 1
    assert dashboard["pipeline_counts"]["packet_ready"] == 1
    assert dashboard["run_counts"]["paused"] == 1


def test_mark_applied_and_reset_ready_update_application_status(db_session: Session, user) -> None:
    job = Job(
        user_id=user.id,
        title="Platform Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="",
        source="manual",
        application_url="https://careers.acme.dev/jobs/status",
        description="Platform engineering role.",
        normalized_description={},
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["python"],
        stack_tags=["python"],
        domain_tags=["platform"],
        source_metadata={},
        enrichment_status="completed",
        enrichment_revision=1,
        latest_score=80.0,
        latest_score_revision=1,
        latest_recommendation="high priority",
        dedupe_key="acme-platform-engineer-status",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    application = applications_routes._ensure_application(job.id, user.id, db_session)
    applied = applications_routes.mark_applied(application.id, user, db_session)
    applied_status = applied.status
    reset = applications_routes.reset_ready(application.id, user, db_session)

    assert applied_status == "applied"
    assert reset.status == "ready_to_apply"


def test_resume_run_requeues_paused_run_with_existing_packet(db_session: Session, user, monkeypatch) -> None:
    job = Job(
        user_id=user.id,
        title="Platform Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="",
        source="manual",
        application_url="https://careers.acme.dev/jobs/resume-run",
        description="Platform engineering role.",
        normalized_description={},
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["python"],
        stack_tags=["python"],
        domain_tags=["platform"],
        source_metadata={},
        enrichment_status="completed",
        enrichment_revision=1,
        latest_score=88.0,
        latest_score_revision=1,
        latest_recommendation="high priority",
        dedupe_key="acme-platform-engineer-resume-run",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    application = applications_routes._ensure_application(job.id, user.id, db_session)
    run = ApplicationRun(
        application_id=application.id,
        mode="assisted",
        status="paused",
        current_step="captcha_or_antibot_detected",
        external_task_id="task-old",
        prepared_payload={
            "mode": "assisted",
            "job": {"application_url": job.application_url},
            "answers": {"email": user.email},
        },
    )
    db_session.add(run)
    db_session.flush()
    db_session.add(
        ApplicationStep(
            run_id=run.id,
            name="captcha_or_antibot_detected",
            status="paused",
            step_kind="anti_bot",
            requires_approval=True,
            output={"reason": "Manual security challenge detected"},
        )
    )
    application.latest_run_id = run.id
    db_session.commit()

    def fake_dispatch(mode: str, run_id: int, packet: dict) -> str:
        assert mode == "assisted"
        assert run_id == run.id
        assert packet["job"]["application_url"] == job.application_url
        return "task-resume-123"

    monkeypatch.setattr("app.api.routes.application_runs.dispatch_application_run", fake_dispatch)
    resumed = application_runs_routes.resume_run(run.id, user, db_session)

    steps = db_session.query(ApplicationStep).filter(ApplicationStep.run_id == run.id).order_by(ApplicationStep.id.asc()).all()

    assert resumed.status == "queued"
    assert resumed.current_step == "resume_requested"
    assert resumed.external_task_id == "task-resume-123"
    assert resumed.finished_at is None
    assert steps[-1].name == "resume_requested"
    assert steps[-1].step_kind == "control"


def test_run_auto_pauses_when_preflight_blocks_dispatch(db_session: Session, user, profile, monkeypatch) -> None:
    role = roles_routes.create_role(
        TargetRoleIn(
            name="Senior Platform Engineer",
            aliases=["Platform Engineer"],
            keywords=["python", "platform"],
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
    job = Job(
        user_id=user.id,
        role_id=role.id,
        title="Senior Platform Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$180,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/run-auto",
        description="Python platform role requiring communication and ownership.",
        normalized_description={},
        seniority="senior",
        employment_type="full-time",
        visa_support="unknown",
        tags=["python"],
        stack_tags=["python"],
        domain_tags=["platform"],
        source_metadata={},
        latest_score=70.0,
        latest_recommendation="maybe",
        dedupe_key="acme-senior-platform-engineer-run-auto",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    def fail_dispatch(mode, run_id, packet):
        raise AssertionError("dispatch_application_run should not be called when preflight blocks auto mode")

    monkeypatch.setattr("app.api.routes.applications.dispatch_application_run", fail_dispatch)

    run = applications_routes.run_auto(job.id, user, db_session)
    steps = db_session.query(ApplicationStep).filter(ApplicationStep.run_id == run.id).all()

    assert run.status == "paused"
    assert run.external_task_id == ""
    assert steps[-1].name == "auto_apply_preflight_gate"
    assert steps[-1].requires_approval is True
    assert "score" in steps[-1].output["reason"].lower()


def test_score_route_records_current_enrichment_revision(db_session: Session, user, profile) -> None:
    job = Job(
        user_id=user.id,
        title="Staff Platform Engineer",
        company="Acme",
        location="Remote",
        remote_type="remote",
        salary="$205,000",
        source="manual",
        application_url="https://careers.acme.dev/jobs/score",
        description="Own platform systems and developer experience.",
        normalized_description={
            "must_have_skills": ["Python", "Kubernetes"],
            "nice_to_have_skills": ["Docker"],
            "extraction_confidence": 0.82,
        },
        seniority="staff",
        employment_type="full-time",
        visa_support="unknown",
        tags=["python", "kubernetes"],
        stack_tags=["python", "kubernetes"],
        domain_tags=["platform"],
        source_metadata={},
        enrichment_status="completed",
        enrichment_revision=4,
        latest_score=0.0,
        latest_score_revision=0,
        latest_recommendation="unscored",
        dedupe_key="acme-staff-platform-engineer-score",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    score = jobs_routes.score(job.id, None, user, db_session)
    refreshed_job = db_session.query(Job).filter(Job.id == job.id).first()

    assert score.enrichment_revision == 4
    assert score.score_breakdown["application_readiness"] >= 7
    assert refreshed_job is not None
    assert refreshed_job.latest_score_revision == 4
