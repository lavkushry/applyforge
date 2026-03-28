from datetime import datetime, timezone

import pytest

from app.models.entities import ApplicationRun
from app.services.application_fsm import available_run_actions, transition_run


def _run(status: str = "queued", current_step: str = "queued") -> ApplicationRun:
    return ApplicationRun(
        application_id=1,
        role_id=1,
        mode="assisted",
        status=status,
        current_step=current_step,
        external_task_id="",
        error_message="",
        policy_snapshot={},
        prepared_payload={},
    )


def test_available_run_actions_exposes_resume_for_operator_states() -> None:
    assert available_run_actions(_run(status="paused")) == ["resume"]
    assert available_run_actions(_run(status="uncertain")) == ["resume"]
    assert available_run_actions(_run(status="failed")) == ["resume"]
    assert available_run_actions(_run(status="running")) == []


def test_transition_run_moves_between_valid_states() -> None:
    run = _run(status="queued", current_step="preflight")

    transition_run(run, event="worker_started", current_step="worker_started")
    assert run.status == "running"
    assert run.current_step == "worker_started"

    transition_run(run, event="pause_requested", current_step="manual_question_review_required")
    assert run.status == "paused"
    assert run.current_step == "manual_question_review_required"
    assert run.finished_at is not None

    transition_run(run, event="resume_requested", current_step="resume_requested")
    assert run.status == "queued"
    assert run.current_step == "resume_requested"
    assert run.finished_at is None


def test_transition_run_rejects_invalid_transition() -> None:
    run = _run(status="completed", current_step="submit_application")
    run.finished_at = datetime.now(timezone.utc)

    with pytest.raises(ValueError):
        transition_run(run, event="worker_started", current_step="worker_started")
