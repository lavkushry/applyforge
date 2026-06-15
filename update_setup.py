import re

with open('apps/api/app/api/routes/setup.py', 'r') as f:
    content = f.read()

new_imports = "from sqlalchemy import select, func, exists\n"
if "from sqlalchemy import select" not in content:
    content = content.replace("from sqlalchemy.orm import Session\n", "from sqlalchemy.orm import Session\n" + new_imports)

search_block = '''@router.get("/wizard", response_model=WizardSummaryOut)
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
    inbox_ready = bool(inbox)'''

replace_block = '''@router.get("/wizard", response_model=WizardSummaryOut)
def wizard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    profile_basics_sq = select(CandidateProfile.basics).where(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()
    profile_skills_sq = select(CandidateProfile.skills).where(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()

    resume_exists_sq = select(
        select(Resume.id).where(Resume.user_id == user.id, Resume.active.is_(True)).exists()
    ).scalar_subquery()

    inbox_exists_sq = select(
        select(InboxConnection.id).where(InboxConnection.user_id == user.id, InboxConnection.status == "connected").exists()
    ).scalar_subquery()

    role_count_sq = select(func.count(TargetRole.id)).where(TargetRole.user_id == user.id).scalar_subquery()
    job_count_sq = select(func.count(Job.id)).where(Job.user_id == user.id, Job.active.is_(True)).scalar_subquery()

    tailored_resume_count_sq = (
        select(func.count(ResumeVersion.id))
        .join(Resume, Resume.id == ResumeVersion.resume_id)
        .where(Resume.user_id == user.id)
        .scalar_subquery()
    )

    result = db.execute(
        select(
            profile_basics_sq.label("profile_basics"),
            profile_skills_sq.label("profile_skills"),
            resume_exists_sq.label("resume_ready"),
            inbox_exists_sq.label("inbox_ready"),
            role_count_sq.label("role_count"),
            job_count_sq.label("job_count"),
            tailored_resume_count_sq.label("tailored_resume_count")
        )
    ).first()

    profile_ready = bool(
        result.profile_basics and
        isinstance(result.profile_basics, dict) and
        result.profile_basics.get("full_name") and
        result.profile_skills
    )
    resume_ready = bool(result.resume_ready)
    inbox_ready = bool(result.inbox_ready)
    role_count = result.role_count or 0
    job_count = result.job_count or 0
    tailored_resume_count = result.tailored_resume_count or 0'''

content = content.replace(search_block, replace_block)

with open('apps/api/app/api/routes/setup.py', 'w') as f:
    f.write(content)
