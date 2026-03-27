from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Application, ApplicationRun, ApplicationStep, User

router = APIRouter(prefix='/application-runs', tags=['application-runs'])


@router.get('/{run_id}')
def get_run(run_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    run = db.query(ApplicationRun).filter(ApplicationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    app = db.query(Application).filter(Application.id == run.application_id, Application.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail='Run not found')
    steps = db.query(ApplicationStep).filter(ApplicationStep.run_id == run.id).all()
    return {'run': run, 'steps': steps}
