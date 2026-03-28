from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import User
from app.services.bootstrap import ensure_bootstrap_default_user


def test_bootstrap_default_user_created_for_empty_dev_db(db_session: Session, monkeypatch) -> None:
    monkeypatch.setattr(settings, "bootstrap_default_user", True)
    monkeypatch.setattr(settings, "env", "dev")
    monkeypatch.setattr(settings, "bootstrap_default_user_email", "defaultuser@applyforge.dev")
    monkeypatch.setattr(settings, "bootstrap_default_user_password", "defaultuser123")
    monkeypatch.setattr("app.services.bootstrap.hash_password", lambda password: f"hashed:{password}")

    user = ensure_bootstrap_default_user(db_session)

    assert user is not None
    assert user.email == "defaultuser@applyforge.dev"
    assert user.password_hash == "hashed:defaultuser123"
    assert db_session.query(User).filter(User.email == "defaultuser@applyforge.dev").count() == 1


def test_bootstrap_default_user_skips_when_existing_user_present(db_session: Session, user, monkeypatch) -> None:
    monkeypatch.setattr(settings, "bootstrap_default_user", True)
    monkeypatch.setattr(settings, "env", "dev")
    monkeypatch.setattr(settings, "bootstrap_default_user_email", "defaultuser@applyforge.dev")
    monkeypatch.setattr(settings, "bootstrap_default_user_password", "defaultuser123")

    created = ensure_bootstrap_default_user(db_session)

    assert created is None
    assert db_session.query(User).filter(User.email == "defaultuser@applyforge.dev").count() == 0
