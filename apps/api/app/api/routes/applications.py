from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.automation.engine import StepEngine
from app.db.session import get_db
from app.models.entities import Application, ApplicationRun, Job, User

router = APIRouter(prefix='/applications', tags=['applications'])


def _ensure_application(job_id: int, user_id: int, db: Session) -> Application:
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user_id).first()
    if app:
        return app
    app = Application(job_id=job_id, user_id=user_id, status='ready_to_apply')
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.post('/{job_id}/prepare')
def prepare(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Application:
    if not db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first():
        raise HTTPException(status_code=404, detail='Job not found')
    return _ensure_application(job_id, user.id, db)


@router.post('/{job_id}/run-assisted')
def run_assisted(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    app = _ensure_application(job_id, user.id, db)
    run = ApplicationRun(application_id=app.id, mode='assisted', status='running')
    db.add(run)
    db.commit()
    db.refresh(run)
    engine = StepEngine(db, run)
    engine.log_step('open_application_url', 'completed', {'url': 'placeholder'})
    engine.log_step('fill_basics', 'completed', {'filled': True})
    engine.log_step('pause_before_submit', 'paused', {'requires_user_approval': True})
    engine.complete('paused')
    return run


@router.post('/{job_id}/run-auto')
def run_auto(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ApplicationRun:
    app = _ensure_application(job_id, user.id, db)
    run = ApplicationRun(application_id=app.id, mode='auto', status='running')
    db.add(run)
    db.commit()
    db.refresh(run)
    engine = StepEngine(db, run)
    engine.log_step('open_application_url', 'completed')
    engine.log_step('fill_form_fields', 'completed')
    engine.log_step('submit_application', 'completed')
    engine.complete('completed')
    return run


@router.get('')
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Application]:
    return db.query(Application).filter(Application.user_id == user.id).all()


@router.get('/{application_id}')
def get_application(application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Application:
    app = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail='Not found')
    return app
