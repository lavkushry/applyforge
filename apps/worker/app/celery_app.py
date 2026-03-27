from celery import Celery

from app.config import settings

celery_app = Celery('applyforge-worker', broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_routes = {'app.tasks.*': {'queue': 'applyforge'}}
