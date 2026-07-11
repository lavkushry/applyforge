import re
with open("apps/api/app/api/routes/setup.py", "r") as f:
    content = f.read()

replacement = r"""@router.get("/wizard", response_model=WizardSummaryOut)
def wizard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    from sqlalchemy import select, func

    profile_basics_sq = select(CandidateProfile.basics).where(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()
    profile_skills_sq = select(CandidateProfile.skills).where(CandidateProfile.user_id == user.id).limit(1).scalar_subquery()
    active_resume_sq = select(select(Resume.id).where(Resume.user_id == user.id, Resume.active.is_(True)).exists()).scalar_subquery()
    inbox_sq = select(select(InboxConnection.id).where(InboxConnection.user_id == user.id, InboxConnection.status == "connected").exists()).scalar_subquery()
    role_count_sq = select(func.count(TargetRole.id)).where(TargetRole.user_id == user.id).scalar_subquery()
    job_count_sq = select(func.count(Job.id)).where(Job.user_id == user.id, Job.active.is_(True)).scalar_subquery()
    tailored_resume_count_sq = (
        select(func.count(ResumeVersion.id))
        .join(Resume, Resume.id == ResumeVersion.resume_id)
        .where(Resume.user_id == user.id)
        .scalar_subquery()
    )

    query = select(
        profile_basics_sq,
        profile_skills_sq,
        active_resume_sq,
        inbox_sq,
        role_count_sq,
        job_count_sq,
        tailored_resume_count_sq,
    )

    result = db.execute(query).first()

    if result:
        profile_basics, profile_skills, resume_ready, inbox_ready, role_count, job_count, tailored_resume_count = result
        profile_ready = bool((profile_basics or {}).get("full_name") and profile_skills)
    else:
        profile_ready = resume_ready = inbox_ready = False
        role_count = job_count = tailored_resume_count = 0
"""

start_str = '@router.get("/wizard", response_model=WizardSummaryOut)\ndef wizard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:\n'
end_str = '\n    profile_ready = bool(profile and profile.basics.get("full_name") and profile.skills)\n    resume_ready = bool(active_resume)\n    inbox_ready = bool(inbox)'

start_idx = content.find(start_str)
end_idx = content.find(end_str) + len(end_str)
new_content = content[:start_idx] + replacement + content[end_idx:]

with open("apps/api/app/api/routes/setup.py", "w") as f:
    f.write(new_content)
