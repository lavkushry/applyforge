import re

with open('apps/api/app/api/routes/setup.py', 'r') as f:
    content = f.read()

content = content.replace("from sqlalchemy.orm import Session", "from sqlalchemy.orm import Session\nfrom sqlalchemy import select, func")

search = """    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
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

replace = """    profile_basics_subq = (
        select(CandidateProfile.basics)
        .where(CandidateProfile.user_id == user.id)
        .limit(1)
        .scalar_subquery()
    )

    profile_skills_subq = (
        select(CandidateProfile.skills)
        .where(CandidateProfile.user_id == user.id)
        .limit(1)
        .scalar_subquery()
    )

    resume_exists_subq = (
        select(
            select(Resume.id)
            .where(Resume.user_id == user.id, Resume.active.is_(True))
            .exists()
        ).scalar_subquery()
    )

    inbox_exists_subq = (
        select(
            select(InboxConnection.id)
            .where(InboxConnection.user_id == user.id, InboxConnection.status == "connected")
            .exists()
        ).scalar_subquery()
    )

    role_count_subq = (
        select(func.count(TargetRole.id))
        .where(TargetRole.user_id == user.id)
        .scalar_subquery()
    )

    job_count_subq = (
        select(func.count(Job.id))
        .where(Job.user_id == user.id, Job.active.is_(True))
        .scalar_subquery()
    )

    tailored_resume_count_subq = (
        select(func.count(ResumeVersion.id))
        .where(ResumeVersion.resume_id.in_(
            select(Resume.id).where(Resume.user_id == user.id)
        ))
        .scalar_subquery()
    )

    row = db.execute(
        select(
            profile_basics_subq.label("profile_basics"),
            profile_skills_subq.label("profile_skills"),
            resume_exists_subq.label("resume_exists"),
            inbox_exists_subq.label("inbox_exists"),
            role_count_subq.label("role_count"),
            job_count_subq.label("job_count"),
            tailored_resume_count_subq.label("tailored_resume_count"),
        )
    ).mappings().first()

    if not row:
        row = {
            "profile_basics": None,
            "profile_skills": None,
            "resume_exists": False,
            "inbox_exists": False,
            "role_count": 0,
            "job_count": 0,
            "tailored_resume_count": 0,
        }

    profile_ready = bool(row["profile_basics"] and row["profile_basics"].get("full_name") and row["profile_skills"])
    resume_ready = bool(row["resume_exists"])
    inbox_ready = bool(row["inbox_exists"])
    role_count = row["role_count"] or 0
    job_count = row["job_count"] or 0
    tailored_resume_count = row["tailored_resume_count"] or 0"""

if search in content:
    with open('apps/api/app/api/routes/setup.py', 'w') as f:
        f.write(content.replace(search, replace))
    print("Patched successfully")
else:
    print("Could not find search block")
