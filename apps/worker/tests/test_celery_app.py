from app.celery_app import celery_app


def test_worker_registers_application_and_enrichment_tasks() -> None:
    celery_app.loader.import_default_modules()
    registered_tasks = celery_app.tasks

    assert "app.tasks.execute_application_run" in registered_tasks
    assert "app.tasks.execute_job_enrichment" in registered_tasks
