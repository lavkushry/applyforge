from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import ApplicationRun, ApplicationStep


class StepEngine:
    def __init__(self, db: Session, run: ApplicationRun):
        self.db = db
        self.run = run

    def log_step(
        self,
        name: str,
        status: str = "pending",
        output: dict | None = None,
        retry_count: int = 0,
        screenshot_file_id: int | None = None,
    ) -> ApplicationStep:
        step = ApplicationStep(
            run_id=self.run.id,
            name=name,
            status=status,
            output=output or {},
            retry_count=retry_count,
            screenshot_file_id=screenshot_file_id,
            completed_at=datetime.utcnow() if status in {"completed", "failed", "paused"} else None,
        )
        self.db.add(step)
        self.run.current_step = name
        self.db.commit()
        self.db.refresh(step)
        return step

    def complete(self, status: str) -> None:
        self.run.status = status
        self.run.finished_at = datetime.utcnow()
        self.db.commit()
