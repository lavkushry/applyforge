import enum
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApplicationStatus(str, enum.Enum):
    discovered = "discovered"
    shortlisted = "shortlisted"
    tailored = "tailored"
    ready_to_apply = "ready_to_apply"
    applied = "applied"
    interview = "interview"
    rejected = "rejected"
    offer = "offer"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    profiles: Mapped[list["CandidateProfile"]] = relationship(back_populates="user")
    companies: Mapped[list["Company"]] = relationship(back_populates="user")
    jobs: Mapped[list["Job"]] = relationship(back_populates="user")
    applications: Mapped[list["Application"]] = relationship(back_populates="user")


class CandidateProfile(TimestampMixin, Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    basics: Mapped[dict] = mapped_column(JSON, default=dict)
    summary: Mapped[str] = mapped_column(Text, default='')
    skills: Mapped[list] = mapped_column(JSON, default=list)
    experience: Mapped[list] = mapped_column(JSON, default=list)
    projects: Mapped[list] = mapped_column(JSON, default=list)
    education: Mapped[list] = mapped_column(JSON, default=list)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    links: Mapped[list] = mapped_column(JSON, default=list)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    saved_answers: Mapped[dict] = mapped_column(JSON, default=dict)
    fact_locked: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped["User"] = relationship(back_populates="profiles")


class ResumeTheme(TimestampMixin, Base):
    __tablename__ = "resume_themes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    accent_color: Mapped[str] = mapped_column(String(20), default="#0f172a")
    layout_mode: Mapped[str] = mapped_column(String(40), default="single-column")
    is_ats_safe: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Resume(TimestampMixin, Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120), default="Master Resume")
    uploaded_file_id: Mapped[int | None] = mapped_column(ForeignKey("uploaded_files.id"), nullable=True)
    original_text: Mapped[str] = mapped_column(Text, default="")
    parse_status: Mapped[str] = mapped_column(String(30), default="pending")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ResumeVersion(TimestampMixin, Base):
    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    theme_id: Mapped[int | None] = mapped_column(ForeignKey("resume_themes.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160), default="Tailored Resume")
    variant: Mapped[str] = mapped_column(String(40), default="tailored")
    theme_variant: Mapped[str] = mapped_column(String(40), default="classic-ats-light")
    ats_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    content_json: Mapped[dict] = mapped_column(JSON, default=dict)
    diff_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    export_status: Mapped[str] = mapped_column(String(30), default="pending")
    pdf_file_id: Mapped[int | None] = mapped_column(ForeignKey("uploaded_files.id"), nullable=True)


class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    kind: Mapped[str] = mapped_column(String(60), default="manual")
    base_url: Mapped[str] = mapped_column(String(255), default="")


class Company(TimestampMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (UniqueConstraint("user_id", "normalized_name", name="uq_companies_user_normalized_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str] = mapped_column(String(500), default="")
    careers_url: Mapped[str] = mapped_column(String(500), default="")
    linkedin_url: Mapped[str] = mapped_column(String(500), default="")
    hq_location: Mapped[str] = mapped_column(String(255), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped["User"] = relationship(back_populates="companies")


class CompanyCareerPortal(TimestampMixin, Base):
    __tablename__ = "company_career_portals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    provider_kind: Mapped[str] = mapped_column(String(60), default="direct_site")
    base_url: Mapped[str] = mapped_column(String(500), default="")
    board_token: Mapped[str] = mapped_column(String(255), default="")
    health_status: Mapped[str] = mapped_column(String(40), default="unknown")
    supports_structured_fetch: Mapped[bool] = mapped_column(Boolean, default=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class CompanyContact(TimestampMixin, Base):
    __tablename__ = "company_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    linkedin_url: Mapped[str] = mapped_column(String(500), default="")
    contact_type: Mapped[str] = mapped_column(String(40), default="recruiter")
    source: Mapped[str] = mapped_column(String(120), default="manual")
    source_url: Mapped[str] = mapped_column(String(500), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class TargetRole(TimestampMixin, Base):
    __tablename__ = "target_roles"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_target_roles_user_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    preferred_locations: Mapped[list] = mapped_column(JSON, default=list)
    remote_preference: Mapped[str] = mapped_column(String(40), default="remote")
    salary_target: Mapped[str] = mapped_column(String(120), default="")
    visa_preference: Mapped[str] = mapped_column(String(80), default="unknown")
    seniority: Mapped[str] = mapped_column(String(80), default="mid")
    companies_include: Mapped[list] = mapped_column(JSON, default=list)
    companies_exclude: Mapped[list] = mapped_column(JSON, default=list)
    scrape_cadence_minutes: Mapped[int] = mapped_column(Integer, default=30)
    automation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    min_auto_apply_score: Mapped[float] = mapped_column(Float, default=85.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class TargetRoleSource(TimestampMixin, Base):
    __tablename__ = "target_role_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("target_roles.id"))
    kind: Mapped[str] = mapped_column(String(60), default="manual")
    label: Mapped[str] = mapped_column(String(120), default="")
    base_url: Mapped[str] = mapped_column(String(500), default="")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class JobIngestionRun(Base):
    __tablename__ = "job_ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("target_roles.id"))
    status: Mapped[str] = mapped_column(String(30), default="queued")
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    discovered_count: Mapped[int] = mapped_column(Integer, default=0)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    enriched_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    expired_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    source_id: Mapped[int | None] = mapped_column(ForeignKey("job_sources.id"), nullable=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    role_id: Mapped[int | None] = mapped_column(ForeignKey("target_roles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255), default="")
    remote_type: Mapped[str] = mapped_column(String(50), default="unknown")
    salary: Mapped[str] = mapped_column(String(120), default="")
    source: Mapped[str] = mapped_column(String(120), default="manual")
    application_url: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text)
    normalized_description: Mapped[dict] = mapped_column(JSON, default=dict)
    seniority: Mapped[str] = mapped_column(String(80), default="")
    employment_type: Mapped[str] = mapped_column(String(80), default="")
    visa_support: Mapped[str] = mapped_column(String(80), default="unknown")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    stack_tags: Mapped[list] = mapped_column(JSON, default=list)
    domain_tags: Mapped[list] = mapped_column(JSON, default=list)
    source_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    enrichment_status: Mapped[str] = mapped_column(String(30), default="completed")
    enrichment_error: Mapped[str] = mapped_column(Text, default="")
    enrichment_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    enrichment_revision: Mapped[int] = mapped_column(Integer, default=1)
    source_document_file_id: Mapped[int | None] = mapped_column(ForeignKey("uploaded_files.id"), nullable=True)
    latest_score: Mapped[float] = mapped_column(Float, default=0.0)
    latest_score_revision: Mapped[int] = mapped_column(Integer, default=1)
    latest_recommendation: Mapped[str] = mapped_column(String(30), default="unscored")
    last_scored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    dedupe_key: Mapped[str] = mapped_column(String(255), unique=True)
    user: Mapped["User"] = relationship(back_populates="jobs")


class JobFeedEvent(Base):
    __tablename__ = "job_feed_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("target_roles.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    run_id: Mapped[int | None] = mapped_column(ForeignKey("job_ingestion_runs.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(40), default="discovered")
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class JobScore(Base):
    __tablename__ = "job_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    role_id: Mapped[int | None] = mapped_column(ForeignKey("target_roles.id"), nullable=True)
    enrichment_revision: Mapped[int] = mapped_column(Integer, default=1)
    overall_score: Mapped[float] = mapped_column(Float)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CoverLetter(TimestampMixin, Base):
    __tablename__ = "cover_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    content: Mapped[str] = mapped_column(Text)
    tone: Mapped[str] = mapped_column(String(40), default="concise")


class Application(TimestampMixin, Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False), default=ApplicationStatus.discovered
    )
    notes: Mapped[str] = mapped_column(Text, default="")
    latest_run_id: Mapped[int | None] = mapped_column(ForeignKey("application_runs.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="applications")


class ApplicationRun(Base):
    __tablename__ = "application_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    role_id: Mapped[int | None] = mapped_column(ForeignKey("target_roles.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    current_step: Mapped[str] = mapped_column(String(120), default="queued")
    external_task_id: Mapped[str] = mapped_column(String(120), default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    policy_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    prepared_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ApplicationStep(Base):
    __tablename__ = "application_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("application_runs.id"))
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    step_kind: Mapped[str] = mapped_column(String(40), default="workflow")
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    screenshot_file_id: Mapped[int | None] = mapped_column(ForeignKey("uploaded_files.id"), nullable=True)
    output: Mapped[dict] = mapped_column(JSON, default=dict)
    masked_output: Mapped[dict] = mapped_column(JSON, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    original_name: Mapped[str] = mapped_column(String(255), default="")
    path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    checksum: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Setting(Base):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_settings_user_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    key: Mapped[str] = mapped_column(String(120))
    value: Mapped[dict] = mapped_column(JSON, default=dict)


class InboxConnection(TimestampMixin, Base):
    __tablename__ = "inbox_connections"
    __table_args__ = (UniqueConstraint("user_id", "provider", "email", name="uq_inbox_connections_user_provider_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="connected")
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    token_masked: Mapped[str] = mapped_column(String(255), default="")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class InboxOtpEvent(Base):
    __tablename__ = "inbox_otp_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey("inbox_connections.id"))
    run_id: Mapped[int | None] = mapped_column(ForeignKey("application_runs.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    sender: Mapped[str] = mapped_column(String(255), default="")
    subject_masked: Mapped[str] = mapped_column(String(255), default="")
    code_last4: Mapped[str] = mapped_column(String(8), default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
