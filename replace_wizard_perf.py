import os

filepath = "apps/api/app/api/routes/setup.py"
with open(filepath, "r") as f:
    content = f.read()

search = """@router.get("/wizard", response_model=WizardSummaryOut)
def wizard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    active_resume = db.query(Resume).filter(Resume.user_id == user.id, Resume.active.is_(True)).first()
    inbox = (
        db.query(InboxConnection)
        .filter(InboxConnection.user_id == user.id, InboxConnection.status == "connected")
        .order_by(InboxConnection.updated_at.desc())
        .first()
    )
    role_count = db.query(TargetRole).filter(TargetRole.user_id == user.id).count()
    job_count = db.query(Job).filter(Job.user_id == user.id, Job.active.is_(True)).count()
    tailored_resume_count = (
        db.query(ResumeVersion)
        .join(Resume, Resume.id == ResumeVersion.resume_id)
        .filter(Resume.user_id == user.id)
        .count()
    )

    profile_ready = bool(profile and profile.basics.get("full_name") and profile.skills)
    resume_ready = bool(active_resume)
    inbox_ready = bool(inbox)"""

replace = r"""@router.get("/wizard", response_model=WizardSummaryOut)
def wizard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    from sqlalchemy import select, func

    subq_profile_basics = select(CandidateProfile.basics).where(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()
    subq_profile_skills = select(CandidateProfile.skills).where(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()

    subq_resume_exists = select(select(Resume.id).where(Resume.user_id == user.id, Resume.active.is_(True)).limit(1).exists()).scalar_subquery()
    subq_inbox_exists = select(select(InboxConnection.id).where(InboxConnection.user_id == user.id, InboxConnection.status == "connected").limit(1).exists()).scalar_subquery()

    subq_role_count = select(func.count(TargetRole.id)).where(TargetRole.user_id == user.id).scalar_subquery()
    subq_job_count = select(func.count(Job.id)).where(Job.user_id == user.id, Job.active.is_(True)).scalar_subquery()

    subq_tailored_count = select(func.count(ResumeVersion.id)).join(Resume, Resume.id == ResumeVersion.resume_id).where(Resume.user_id == user.id).scalar_subquery()

    stmt = select(
        subq_profile_basics.label("profile_basics"),
        subq_profile_skills.label("profile_skills"),
        subq_resume_exists.label("resume_ready"),
        subq_inbox_exists.label("inbox_ready"),
        subq_role_count.label("role_count"),
        subq_job_count.label("job_count"),
        subq_tailored_count.label("tailored_resume_count")
    )

    result = db.execute(stmt).first()

    if result:
        profile_ready = bool(result.profile_basics and result.profile_basics.get("full_name") and result.profile_skills)
        resume_ready = bool(result.resume_ready)
        inbox_ready = bool(result.inbox_ready)
        role_count = result.role_count or 0
        job_count = result.job_count or 0
        tailored_resume_count = result.tailored_resume_count or 0
    else:
        profile_ready = resume_ready = inbox_ready = False
        role_count = job_count = tailored_resume_count = 0"""

if search in content:
    content = content.replace(search, replace)
    with open(filepath, "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("Search string not found")
