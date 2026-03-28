from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base
from app.models.entities import CandidateProfile, User


@pytest.fixture
def db_session(tmp_path) -> Generator[Session, None, None]:
    db_path = tmp_path / "applyforge-test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def user(db_session: Session) -> User:
    row = User(email="alex@example.com", password_hash="test-password-hash")
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


@pytest.fixture
def profile(db_session: Session, user: User) -> CandidateProfile:
    row = CandidateProfile(
        user_id=user.id,
        basics={
            "full_name": "Alex Builder",
            "email": user.email,
            "phone": "+1 555-555-5555",
            "location": "Remote",
            "headline": "Staff Full-Stack Engineer",
        },
        summary="Staff-level engineer building reliable job-hunt automation systems.",
        skills=["Python", "FastAPI", "TypeScript", "React", "Playwright", "Kubernetes"],
        experience=[
            {
                "title": "Staff Engineer",
                "company": "Forge Labs",
                "highlights": ["Built workflow automation", "Owned platform reliability"],
            }
        ],
        projects=[],
        education=[],
        certifications=[],
        links=[{"label": "LinkedIn", "url": "https://linkedin.com/in/alexbuilder"}],
        preferences={"work_authorization": "Authorized to work in the United States"},
        saved_answers={"notice_period": "Two weeks"},
        fact_locked=True,
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row
