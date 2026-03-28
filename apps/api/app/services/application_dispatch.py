import importlib

from app.core.config import settings


def dispatch_application_run(mode: str, run_id: int, packet: dict) -> str:
    celery_module = importlib.import_module("celery")
    celery_client = celery_module.Celery("applyforge-api", broker=settings.redis_url, backend=settings.redis_url)
    task = celery_client.send_task(
        "app.tasks.execute_application_run",
        kwargs={"run_id": run_id, "packet": packet},
        queue="applyforge",
    )
    return str(task.id)
