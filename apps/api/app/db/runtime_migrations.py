from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


PHASE_1_COLUMN_UPGRADES: dict[str, dict[str, str]] = {
    "company_career_portals": {
        "last_success_at": "ALTER TABLE company_career_portals ADD COLUMN last_success_at DATETIME",
        "last_error": "ALTER TABLE company_career_portals ADD COLUMN last_error TEXT NOT NULL DEFAULT ''",
        "last_job_count": "ALTER TABLE company_career_portals ADD COLUMN last_job_count INTEGER NOT NULL DEFAULT 0",
        "last_run_id": "ALTER TABLE company_career_portals ADD COLUMN last_run_id INTEGER",
        "resolution_metadata": "ALTER TABLE company_career_portals ADD COLUMN resolution_metadata JSON NOT NULL DEFAULT '{}'",
    },
    "job_ingestion_runs": {
        "company_id": "ALTER TABLE job_ingestion_runs ADD COLUMN company_id INTEGER",
        "company_portal_id": "ALTER TABLE job_ingestion_runs ADD COLUMN company_portal_id INTEGER",
        "trigger_kind": "ALTER TABLE job_ingestion_runs ADD COLUMN trigger_kind VARCHAR(40) NOT NULL DEFAULT 'role_scrape'",
    },
    "jobs": {
        "company_portal_id": "ALTER TABLE jobs ADD COLUMN company_portal_id INTEGER",
    },
}


def ensure_runtime_schema_upgrades(engine: Engine) -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, column_upgrades in PHASE_1_COLUMN_UPGRADES.items():
            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, statement in column_upgrades.items():
                if column_name in existing_columns:
                    continue
                connection.execute(text(statement))
