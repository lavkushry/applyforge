from sqlalchemy import create_engine, inspect, text

from app.db.runtime_migrations import ensure_runtime_schema_upgrades


def test_runtime_schema_upgrades_add_company_ingestion_columns(tmp_path) -> None:
    db_path = tmp_path / "applyforge-runtime-migrations.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE company_career_portals (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    provider_kind VARCHAR(60) DEFAULT 'direct_site',
                    base_url VARCHAR(500) DEFAULT '',
                    board_token VARCHAR(255) DEFAULT '',
                    health_status VARCHAR(40) DEFAULT 'unknown',
                    supports_structured_fetch BOOLEAN DEFAULT 0,
                    last_checked_at DATETIME,
                    notes TEXT DEFAULT '',
                    created_at DATETIME,
                    updated_at DATETIME
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE job_ingestion_runs (
                    id INTEGER PRIMARY KEY,
                    role_id INTEGER,
                    status VARCHAR(30) DEFAULT 'queued',
                    source_count INTEGER DEFAULT 0,
                    discovered_count INTEGER DEFAULT 0,
                    inserted_count INTEGER DEFAULT 0,
                    updated_count INTEGER DEFAULT 0,
                    enriched_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    expired_count INTEGER DEFAULT 0,
                    error_message TEXT DEFAULT '',
                    retry_metadata JSON DEFAULT '{}',
                    started_at DATETIME,
                    finished_at DATETIME
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    company_id INTEGER,
                    role_id INTEGER,
                    title VARCHAR(255),
                    company VARCHAR(255),
                    description TEXT,
                    dedupe_key VARCHAR(255)
                )
                """
            )
        )

    ensure_runtime_schema_upgrades(engine)

    inspector = inspect(engine)
    portal_columns = {column["name"] for column in inspector.get_columns("company_career_portals")}
    run_columns = {column["name"] for column in inspector.get_columns("job_ingestion_runs")}
    job_columns = {column["name"] for column in inspector.get_columns("jobs")}

    assert {"last_success_at", "last_error", "last_job_count", "last_run_id", "resolution_metadata"} <= portal_columns
    assert {"company_id", "company_portal_id", "trigger_kind"} <= run_columns
    assert {"company_portal_id"} <= job_columns
