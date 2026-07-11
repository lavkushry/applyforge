from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, JSON, select, func
from sqlalchemy.orm import declarative_base, Session
import os

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    basics = Column(JSON)
    skills = Column(JSON)

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    active = Column(Boolean)

class InboxConnection(Base):
    __tablename__ = "inbox_connections"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)

class TargetRole(Base):
    __tablename__ = "target_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    active = Column(Boolean)

class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

session = Session(engine)

u = User()
session.add(u)
session.commit()

p = CandidateProfile(user_id=u.id, basics={"full_name": "Test User"}, skills=["Python"])
session.add(p)

r = Resume(user_id=u.id, active=True)
session.add(r)
session.commit()

user_id = u.id

profile_basics_sq = select(CandidateProfile.basics).where(CandidateProfile.user_id == user_id).limit(1).scalar_subquery()
profile_skills_sq = select(CandidateProfile.skills).where(CandidateProfile.user_id == user_id).limit(1).scalar_subquery()
active_resume_sq = select(select(Resume.id).where(Resume.user_id == user_id, Resume.active.is_(True)).exists()).scalar_subquery()
inbox_sq = select(select(InboxConnection.id).where(InboxConnection.user_id == user_id, InboxConnection.status == "connected").exists()).scalar_subquery()
role_count_sq = select(func.count(TargetRole.id)).where(TargetRole.user_id == user_id).scalar_subquery()
job_count_sq = select(func.count(Job.id)).where(Job.user_id == user_id, Job.active.is_(True)).scalar_subquery()
tailored_resume_count_sq = select(func.count(ResumeVersion.id)).join(Resume, Resume.id == ResumeVersion.resume_id).where(Resume.user_id == user_id).scalar_subquery()

q = select(
    profile_basics_sq,
    profile_skills_sq,
    active_resume_sq,
    inbox_sq,
    role_count_sq,
    job_count_sq,
    tailored_resume_count_sq
)

print(q)
result = session.execute(q).first()
print(result)

profile_basics, profile_skills, has_active_resume, has_inbox, role_count, job_count, tailored_resume_count = result
print(profile_basics, profile_skills, has_active_resume, has_inbox, role_count, job_count, tailored_resume_count)
