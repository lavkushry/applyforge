import importlib

from app.core.config import settings


def dispatch_job_enrichment(*, run_id: int, job_id: int, role_id: int, user_id: int, source_context: dict | None = None) -> str:
    celery_module = importlib.import_module("celery")
    celery_client = celery_module.Celery("applyforge-api", broker=settings.redis_url, backend=settings.redis_url)
    task = celery_client.send_task(
        "app.tasks.execute_job_enrichment",
        kwargs={
            "run_id": run_id,
            "job_id": job_id,
            "role_id": role_id,
            "user_id": user_id,
            "source_context": source_context or {},
        },
        queue="applyforge",
    )
    return str(task.id)
