from datetime import datetime, timezone


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


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def transition_run_state(run, *, event: str, current_step: str, error_message: str = ""):
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
