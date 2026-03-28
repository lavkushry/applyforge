FROM python:3.12-slim
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
WORKDIR /app
COPY apps/worker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && playwright install chromium \
    && useradd --create-home --shell /bin/bash appworker \
    && mkdir -p /ms-playwright /app/artifacts \
    && chown -R appworker:appworker /app /ms-playwright
COPY apps/worker /app
USER appworker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "-Q", "applyforge", "-E"]
