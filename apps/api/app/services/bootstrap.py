from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.entities import User


def ensure_bootstrap_default_user(db: Session) -> User | None:
    if not settings.bootstrap_default_user:
        return None
    if settings.env.lower() == "prod":
        return None

    existing_default = db.query(User).filter(User.email == settings.bootstrap_default_user_email).first()
    if existing_default:
        return existing_default

    if db.query(User.id).first():
        return None

    user = User(
        email=settings.bootstrap_default_user_email,
        password_hash=hash_password(settings.bootstrap_default_user_password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
