import hashlib
from datetime import datetime, timezone
from pathlib import Path

from app.db import SessionLocal
from app.models import Application, ApplicationRun, ApplicationStep, UploadedFile


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class RunRecorder:
    def __init__(self, run_id: int):
        self.run_id = run_id

    def set_status(self, status: str, current_step: str, error_message: str = "") -> None:
        with SessionLocal() as db:
            run = db.query(ApplicationRun).filter(ApplicationRun.id == self.run_id).first()
            if not run:
                return
            run.status = status
            run.current_step = current_step
            run.error_message = error_message
            if status in {"completed", "failed", "paused", "uncertain"}:
                run.finished_at = utcnow()
            if status == "completed":
                application = db.query(Application).filter(Application.id == run.application_id).first()
                if application:
                    application.status = "applied"
            db.commit()

    def log_step(
        self,
        *,
        name: str,
        status: str,
        output: dict | None = None,
        masked_output: dict | None = None,
        step_kind: str = "workflow",
        requires_approval: bool = False,
        screenshot_file_id: int | None = None,
        retry_count: int = 0,
    ) -> None:
        with SessionLocal() as db:
            step = ApplicationStep(
                run_id=self.run_id,
                name=name,
                status=status,
                step_kind=step_kind,
                requires_approval=requires_approval,
                output=output or {},
                masked_output=masked_output or {},
                screenshot_file_id=screenshot_file_id,
                retry_count=retry_count,
                completed_at=utcnow() if status in {"completed", "failed", "paused"} else None,
            )
            db.add(step)
            run = db.query(ApplicationRun).filter(ApplicationRun.id == self.run_id).first()
            if run:
                run.current_step = name
            db.commit()


def persist_uploaded_file(*, user_id: int | None, path: str, original_name: str, mime_type: str) -> int:
    file_path = Path(path)
    content = file_path.read_bytes()
    with SessionLocal() as db:
        uploaded = UploadedFile(
            user_id=user_id,
            original_name=original_name,
            path=str(file_path),
            mime_type=mime_type,
            size_bytes=len(content),
            checksum=sha256_bytes(content),
        )
        db.add(uploaded)
        db.commit()
        db.refresh(uploaded)
        return uploaded.id
