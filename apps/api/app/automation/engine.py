from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import ApplicationRun, ApplicationStep


class StepEngine:
    def __init__(self, db: Session, run: ApplicationRun):
        self.db = db
        self.run = run

    def log_step(self, name: str, status: str = 'pending', output: dict | None = None, retry_count: int = 0) -> ApplicationStep:
        step = ApplicationStep(
            run_id=self.run.id,
            name=name,
            status=status,
            output=output or {},
            retry_count=retry_count,
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def complete(self, status: str) -> None:
        self.run.status = status
        self.run.finished_at = datetime.utcnow()
        self.db.commit()
