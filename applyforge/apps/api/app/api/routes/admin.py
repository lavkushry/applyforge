from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import ApplicationRun, ApplicationStep, User

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/runs')
def runs(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ApplicationRun]:
    return db.query(ApplicationRun).order_by(ApplicationRun.started_at.desc()).limit(50).all()


@router.get('/errors')
def errors(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ApplicationStep]:
    return db.query(ApplicationStep).filter(ApplicationStep.status.in_(['failed', 'paused'])).all()


@router.get('/health')
def health() -> dict:
    return {'status': 'ok'}
