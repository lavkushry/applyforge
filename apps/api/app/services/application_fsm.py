from datetime import datetime, timezone

from app.models.entities import ApplicationRun

RUN_TRANSITIONS: dict[str, dict[str, str]] = {
    "pending": {
        "queue_requested": "queued",
        "worker_started": "running",
        "pause_requested": "paused",
        "failure_recorded": "failed",
    },
    "queued": {
        "worker_started": "running",
        "pause_requested": "paused",
        "failure_recorded": "failed",
        "completion_recorded": "completed",
        "uncertainty_recorded": "uncertain",
    },
    "running": {
        "pause_requested": "paused",
        "failure_recorded": "failed",
        "completion_recorded": "completed",
        "uncertainty_recorded": "uncertain",
    },
    "paused": {
        "resume_requested": "queued",
        "failure_recorded": "failed",
    },
    "uncertain": {
        "resume_requested": "queued",
        "pause_requested": "paused",
        "failure_recorded": "failed",
    },
    "failed": {
        "resume_requested": "queued",
    },
    "completed": {},
}

TERMINAL_RUN_STATES = {"paused", "failed", "completed", "uncertain"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def is_terminal_run_state(status: str) -> bool:
    return status in TERMINAL_RUN_STATES


def available_run_actions(run: ApplicationRun) -> list[str]:
    if run.mode != "draft" and run.status in {"paused", "uncertain", "failed"}:
        return ["resume"]
    return []


def transition_run(run: ApplicationRun, *, event: str, current_step: str, error_message: str = "") -> ApplicationRun:
    current_status = run.status or "pending"
    next_status = RUN_TRANSITIONS.get(current_status, {}).get(event)
    if next_status is None:
        raise ValueError(f"Invalid run transition: {current_status} -> {event}")

    run.status = next_status
    run.current_step = current_step
    if next_status in {"queued", "running", "pending"}:
        run.finished_at = None
    else:
        run.finished_at = utcnow()
    run.error_message = error_message if next_status == "failed" else ""
    return run
