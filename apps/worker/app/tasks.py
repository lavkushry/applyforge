from celery.utils.log import get_task_logger

from app.celery_app import celery_app
from app.job_enrichment_runner import run_job_enrichment
from app.logging_utils import configure_logging
from app.playwright_runner import run_application_flow

configure_logging()

logger = get_task_logger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3, name="app.tasks.execute_application_run")
def execute_application_run(self, run_id: int, packet: dict) -> dict:
    logger.info(
        "execute_application_run",
        extra={
            "task_name": self.name,
            "task_id": self.request.id,
            "run_id": run_id,
            "mode": packet.get("mode", "assisted"),
            "retry_count": self.request.retries,
        },
    )
    return run_application_flow(run_id, packet)


@celery_app.task(bind=True, name="app.tasks.execute_job_enrichment")
def execute_job_enrichment(self, run_id: int, job_id: int, role_id: int, user_id: int, source_context: dict | None = None) -> dict:
    logger.info(
        "execute_job_enrichment",
        extra={
            "task_name": self.name,
            "task_id": self.request.id,
            "run_id": run_id,
            "job_id": job_id,
            "role_id": role_id,
            "user_id": user_id,
        },
    )
    return run_job_enrichment(run_id, job_id, role_id, user_id, source_context or {})


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def execute_assisted_apply(self, application_url: str, answers: dict) -> dict:
    logger.info(
        "execute_assisted_apply",
        extra={
            "task_name": self.name,
            "task_id": self.request.id,
            "application_url": application_url,
            "answer_keys": sorted(answers.keys()),
        },
    )
    return {
        "status": "paused",
        "steps": [
            {
                "name": "compatibility_mode",
                "status": "paused",
                "output": {"application_url": application_url, "answer_keys": sorted(answers.keys())},
            }
        ],
    }
