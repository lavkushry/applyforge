FROM python:3.12-slim
WORKDIR /app
COPY apps/worker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && playwright install chromium
COPY apps/worker /app
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]
