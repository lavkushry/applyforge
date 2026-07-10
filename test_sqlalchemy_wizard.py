import sys
import os

# Add apps/api to sys.path
sys.path.insert(0, os.path.abspath('apps/api'))

from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.entities import CandidateProfile, InboxConnection, Job, Resume, ResumeVersion, TargetRole, TargetRoleSource, User

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user = User(email="test@example.com", password_hash="pw")
db.add(user)
db.commit()

# Insert some test data
db.add(CandidateProfile(user_id=user.id, basics={"full_name": "Test User"}, skills=["Python"]))
db.add(Resume(user_id=user.id, active=True))
db.commit()

profile_basics_subq = (
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

print("row:", row)
