from celery.utils.log import get_task_logger

from app.celery_app import celery_app
from app.playwright_runner import run_assisted_flow

logger = get_task_logger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def execute_assisted_apply(self, application_url: str, answers: dict) -> dict:
    logger.info('Running assisted flow for %s', application_url)
    return run_assisted_flow(application_url, answers)
