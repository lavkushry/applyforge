from celery import Celery

from app.config import settings

celery_app = Celery(
    "applyforge-worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)
celery_app.conf.update(
    task_default_queue="applyforge",
    task_routes={"app.tasks.*": {"queue": "applyforge"}},
    broker_connection_retry_on_startup=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
)
