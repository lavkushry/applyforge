from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.entities import (
    Application,
    ApplicationRun,
    ApplicationStatus,
    ApplicationStep,
    AuditLog,
    CandidateProfile,
    Job,
    JobScore,
    ResumeTheme,
    Resume,
    ResumeVersion,
    Setting,
    TargetRole,
    User,
)
from app.services.job_normalizer import normalize_job_payload
from app.services.resume_themes import seed_resume_themes
from app.services.scoring import score_job
from app.services.tailor import generate_cover_letter, tailor_resume


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_resume_themes(db)

    user = db.query(User).filter(User.email == "demo@applyforge.dev").first()
    if not user:
        user = User(email="demo@applyforge.dev", password_hash=hash_password("demo1234"))
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        profile = CandidateProfile(
            user_id=user.id,
            basics={
                "full_name": "Alex Builder",
                "headline": "Staff-level full-stack engineer",
                "email": user.email,
                "location": "Bengaluru, India",
                "target_role": "Senior Full Stack Engineer",
                "preferred_locations": ["remote", "india"],
            },
            summary="Full-stack engineer building AI and automation products with strong product execution.",
            skills=["Python", "FastAPI", "TypeScript", "React", "Docker", "Kubernetes"],
            experience=[
                {
                    "title": "Staff Engineer",
                    "company": "Forge Labs",
                    "highlights": [
                        "Built AI-assisted workflows for high-volume users.",
                        "Owned platform automation and developer tooling.",
                    ],
                }
            ],
            projects=[{"name": "ApplyForge", "highlights": ["AI job hunt operating system MVP"]}],
            education=[{"institution": "IIT Example", "degree": "B.Tech Computer Science"}],
            certifications=[{"name": "AWS Certified Developer"}],
            links=[
                {"label": "linkedin", "url": "https://linkedin.com/in/alex-builder"},
                {"label": "github", "url": "https://github.com/alex-builder"},
                {"label": "portfolio", "url": "https://alexbuilder.dev"},
            ],
            preferences={"visa_required": False, "work_authorization": "Authorized to work in India"},
            saved_answers={
                "work_authorization": "Authorized to work in India without sponsorship.",
                "years_of_experience": "8+ years",
                "notice_period": "30 days",
                "relocation": "Open to remote-first roles and selective relocation.",
            },
            fact_locked=True,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    resume = db.query(Resume).filter(Resume.user_id == user.id, Resume.active.is_(True)).first()
    if not resume:
        resume = Resume(user_id=user.id, title="Master Resume", parse_status="parsed", active=True)
        db.add(resume)
        db.commit()
        db.refresh(resume)

    if db.query(Job).filter(Job.user_id == user.id).count() == 0:
        role = db.query(TargetRole).filter(TargetRole.user_id == user.id, TargetRole.name == "Senior Full Stack Engineer").first()
        if not role:
            role = TargetRole(
                user_id=user.id,
                name="Senior Full Stack Engineer",
                aliases=["Full Stack Engineer", "Staff Engineer"],
                keywords=["python", "fastapi", "react", "typescript", "ai"],
                preferred_locations=["remote", "india"],
                remote_preference="remote",
                seniority="senior",
                automation_enabled=True,
                min_auto_apply_score=80.0,
            )
            db.add(role)
            db.commit()
            db.refresh(role)
        seed_jobs = [
            normalize_job_payload(
                {
                    "role_id": role.id,
                    "title": "Senior Full Stack Engineer",
                    "company": "Nimbus AI",
                    "location": "Remote, US",
                    "description": "Looking for Python, FastAPI, React, TypeScript, Docker, and AI product delivery experience.",
                    "remote_type": "remote",
                    "source": "manual",
                    "application_url": "https://example.com/job/1",
                    "tags": ["ai", "saas"],
                    "salary": "$150k - $180k",
                    "seniority": "senior",
                    "employment_type": "full-time",
                    "visa_support": "unknown",
                }
            ),
            normalize_job_payload(
                {
                    "role_id": role.id,
                    "title": "Platform Engineer",
                    "company": "Atlas Cloud",
                    "location": "Hybrid - Bengaluru",
                    "description": "Python, Kubernetes, Docker, and cloud systems experience required for platform automation.",
                    "remote_type": "hybrid",
                    "source": "manual",
                    "application_url": "https://example.com/job/2",
                    "tags": ["platform"],
                    "salary": "Competitive",
                    "seniority": "senior",
                    "employment_type": "full-time",
                    "visa_support": "not-provided",
                }
            ),
        ]
        db.add_all([Job(user_id=user.id, **payload) for payload in seed_jobs])
        db.commit()

    jobs = db.query(Job).filter(Job.user_id == user.id).all()
    default_theme = db.query(ResumeTheme).filter(ResumeTheme.slug == "classic-ats-light").first()
    for job in jobs:
        if not db.query(JobScore).filter(JobScore.job_id == job.id).first():
            score_payload = score_job(
                {
                    "basics": profile.basics,
                    "skills": profile.skills,
                    "summary": profile.summary,
                    "preferences": profile.preferences,
                },
                {
                    "title": job.title,
                    "description": job.description,
                    "location": job.location,
                    "remote_type": job.remote_type,
                    "seniority": job.seniority,
                    "salary": job.salary,
                    "tags": job.tags,
                },
            )
            db.add(JobScore(job_id=job.id, **score_payload))

        if not db.query(ResumeVersion).filter(ResumeVersion.job_id == job.id).first():
            tailored = tailor_resume(
                {
                    "basics": profile.basics,
                    "summary": profile.summary,
                    "skills": profile.skills,
                    "experience": profile.experience,
                    "projects": profile.projects,
                    "education": profile.education,
                    "certifications": profile.certifications,
                    "links": profile.links,
                    "preferences": profile.preferences,
                    "saved_answers": profile.saved_answers,
                    "fact_locked": profile.fact_locked,
                },
                {"title": job.title, "company": job.company, "description": job.description},
            )
            db.add(
                ResumeVersion(
                    resume_id=resume.id,
                    job_id=job.id,
                    theme_id=default_theme.id if default_theme else None,
                    title=f"{job.company} - {job.title}",
                    variant="tailored",
                    content_json=tailored,
                    theme_variant=default_theme.slug if default_theme else "classic-ats-light",
                    export_status="ready",
                )
            )

    db.commit()

    application = db.query(Application).filter(Application.user_id == user.id).first()
    if not application:
        first_job = jobs[0]
        application = Application(
            user_id=user.id,
            job_id=first_job.id,
            status=ApplicationStatus.ready_to_apply,
            notes="Demo application run seeded for diagnostics.",
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        run_row = ApplicationRun(application_id=application.id, mode="assisted", status="paused", current_step="pause_before_submit")
        db.add(run_row)
        db.flush()
        application.latest_run_id = run_row.id
        db.commit()
        db.refresh(run_row)

        db.add_all(
            [
                ApplicationStep(run_id=run_row.id, name="open_application_url", status="completed", output={"ok": True}),
                ApplicationStep(run_id=run_row.id, name="fill_contact_fields", status="completed", output={"email": user.email}),
                ApplicationStep(
                    run_id=run_row.id,
                    name="pause_before_submit",
                    status="paused",
                    output={"requires_approval": True},
                ),
            ]
        )
        db.commit()

    if db.query(Setting).filter(Setting.user_id == user.id).count() == 0:
        db.add_all(
            [
                Setting(user_id=user.id, key="automation_preferences", value={"mode": "assisted", "pause_on_risk": True}),
                Setting(user_id=user.id, key="job_filters", value={"remote_only": False, "keyword_focus": ["python", "ai"]}),
                Setting(user_id=user.id, key="resume_preferences", value={"default_theme": "classic-ats-light", "ats_mode": True}),
            ]
        )
        db.commit()

    if db.query(AuditLog).filter(AuditLog.user_id == user.id).count() == 0:
        db.add(
            AuditLog(
                user_id=user.id,
                action="prompt.resume_tailoring",
                event_metadata={"mode": "deterministic_stub", "payload": {"job_count": len(jobs)}},
            )
        )
        db.commit()

    db.close()
    print("Seed complete: demo@applyforge.dev / demo1234")


if __name__ == "__main__":
    run()
