from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import AuditLog


PROMPT_FILES = {
    "resume_parse_cleanup": "resume_parse_cleanup.txt",
    "job_normalization": "job_normalization.txt",
    "job_scoring_explainer": "job_scoring_explainer.txt",
    "resume_tailoring": "resume_tailoring.txt",
    "cover_letter": "cover_letter.txt",
    "application_answering": "application_answering.txt",
    "risk_detection": "risk_detection.txt",
}


def load_prompt(prompt_name: str) -> str:
    prompt_file = PROMPT_FILES[prompt_name]
    prompt_path = Path(settings.resolved_prompt_root) / prompt_file
    return prompt_path.read_text(encoding="utf-8")


def mask_sensitive_payload(payload: dict[str, Any]) -> dict[str, Any]:
    masked = {}
    for key, value in payload.items():
        lowered = key.lower()
        if any(token in lowered for token in ("email", "phone", "salary", "authorization", "password", "token")):
            masked[key] = "***"
            continue
        masked[key] = value
    return masked


def log_prompt_invocation(
    db: Session | None,
    *,
    user_id: int | None,
    prompt_name: str,
    payload: dict[str, Any],
    mode: str = "deterministic_stub",
) -> None:
    if db is None:
        return
    audit = AuditLog(
        user_id=user_id,
        action=f"prompt.{prompt_name}",
        event_metadata={
            "mode": mode,
            "model": settings.openai_model,
            "prompt_preview": load_prompt(prompt_name)[:160],
            "payload": mask_sensitive_payload(payload),
        },
    )
    db.add(audit)
    db.commit()
