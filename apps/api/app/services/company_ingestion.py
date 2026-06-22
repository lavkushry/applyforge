from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.entities import (
    Company,
    CompanyCareerPortal,
    Job,
    JobIngestionRun,
    TargetRole,
)
from app.services.company_directory import (
    normalize_company_name,
    resolve_company_for_job,
)
from app.services.job_dispatch import dispatch_job_enrichment
from app.services.job_normalizer import normalize_job_payload
from app.services.role_ingestion import (
    _log_feed_event,
    _maybe_finalize_run,
    fetch_jobs_for_source,
    record_enrichment_failure,
    utcnow,
)


@dataclass(frozen=True)
class PortalSourceDescriptor:
    kind: str
    label: str
    base_url: str
    config: dict = field(default_factory=dict)


def _portal_source_descriptor(
    company: Company, portal: CompanyCareerPortal
) -> PortalSourceDescriptor:
    provider_kind = portal.provider_kind.strip().lower()
    kind_map = {
        "greenhouse": "greenhouse_board",
        "greenhouse_board": "greenhouse_board",
        "lever": "lever_board",
        "lever_board": "lever_board",
        "workday": "workday_board",
        "workday_board": "workday_board",
        "direct_site": "direct_url",
        "direct_url": "direct_url",
    }
    source_kind = kind_map.get(provider_kind, "direct_url")
    config = dict(portal.resolution_metadata or {})
    if source_kind == "greenhouse_board" and portal.board_token:
        config["board_token"] = portal.board_token
    if source_kind == "lever_board" and portal.board_token:
        config["site_token"] = portal.board_token
    return PortalSourceDescriptor(
        kind=source_kind,
        label=company.name,
        base_url=portal.base_url or company.careers_url or company.website_url,
        config=config,
    )


def _expire_missing_company_jobs(
    db: Session,
    *,
    user_id: int,
    role: TargetRole,
    company: Company,
    portal_ids: list[int],
    seen_dedupe_keys: set[str],
    run: JobIngestionRun,
) -> int:
    expired_count = 0
    query = db.query(Job).filter(
        Job.user_id == user_id,
        Job.role_id == role.id,
        Job.company_id == company.id,
        Job.active.is_(True),
    )
    if portal_ids:
        query = query.filter(Job.company_portal_id.in_(portal_ids))
    active_jobs = query.all()
    for job in active_jobs:
        if job.dedupe_key in seen_dedupe_keys:
            continue
        job.active = False
        job.expired_at = utcnow()
        expired_count += 1
        _log_feed_event(
            db,
            role_id=role.id,
            job_id=job.id,
            run_id=run.id,
            event_type="expired",
            event_metadata={
                "company": job.company,
                "title": job.title,
                "company_id": company.id,
            },
        )
    return expired_count


def ingest_company(
    db: Session,
    *,
    user_id: int,
    company: Company,
    role: TargetRole,
    portal_id: int | None = None,
) -> JobIngestionRun:
    portal_query = db.query(CompanyCareerPortal).filter(
        CompanyCareerPortal.company_id == company.id
    )
    if portal_id is not None:
        portal_query = portal_query.filter(CompanyCareerPortal.id == portal_id)
    portals = portal_query.order_by(CompanyCareerPortal.id.asc()).all()

    run = JobIngestionRun(
        role_id=role.id,
        company_id=company.id,
        company_portal_id=portal_id,
        trigger_kind="company_portal_scrape"
        if portal_id is not None
        else "company_scrape",
        status="running",
    )
    db.add(run)
    db.flush()

    run.source_count = len(portals)
    if not portals:
        run.status = "failed"
        run.error_message = "No company portals configured"
        run.finished_at = utcnow()
        db.commit()
        db.refresh(run)
        return run

    discovered_count = 0
    inserted_count = 0
    updated_count = 0
    seen_dedupe_keys: set[str] = set()
    portal_ids = [portal.id for portal in portals]

    for portal in portals:
        source = _portal_source_descriptor(company, portal)
        portal.last_run_id = run.id
        try:
            payloads = fetch_jobs_for_source(source)
        except Exception as exc:
            run.failed_count += 1
            run.error_message = "\n".join(
                filter(
                    None, [run.error_message, f"{portal.base_url or portal.id}: {exc}"]
                )
            )
            portal.last_checked_at = utcnow()
            portal.last_error = str(exc)
            portal.last_job_count = 0
            portal.health_status = "error"
            continue

        portal.last_checked_at = utcnow()
        portal.last_success_at = utcnow()
        portal.last_error = ""
        portal.last_job_count = len(payloads)
        portal.health_status = "healthy"

        for payload in payloads:
            discovered_count += 1
            run.discovered_count = discovered_count
            normalized = normalize_job_payload({**payload, "role_id": role.id})
            seen_dedupe_keys.add(normalized["dedupe_key"])
            job_company_name = normalized.get("company", company.name)
            if normalize_company_name(job_company_name) == company.normalized_name:
                resolved_company = company
            else:
                resolved_company = resolve_company_for_job(
                    db,
                    user_id=user_id,
                    company_name=job_company_name,
                    application_url=normalized.get("application_url", ""),
                    source_url=source.base_url,
                    explicit_company_id=company.id,
                )
            normalized["company_id"] = (
                resolved_company.id if resolved_company else company.id
            )
            normalized["company_portal_id"] = portal.id
            existing = (
                db.query(Job).filter(Job.dedupe_key == normalized["dedupe_key"]).first()
            )
            event_type = "discovered"
            if existing:
                existing.role_id = role.id
                existing.company_id = normalized["company_id"]
                existing.company_portal_id = portal.id
                existing.last_seen_at = utcnow()
                existing.active = True
                existing.expired_at = None
                existing.source_metadata = normalized.get("source_metadata", {})
                existing.description = normalized["description"]
                existing.location = normalized["location"]
                existing.remote_type = normalized["remote_type"]
                existing.salary = normalized["salary"]
                existing.application_url = normalized["application_url"]
                existing.source = normalized["source"]
                existing.enrichment_status = "pending"
                existing.enrichment_error = ""
                job = existing
                updated_count += 1
                event_type = "updated"
            else:
                job = Job(
                    user_id=user_id,
                    first_seen_at=utcnow(),
                    last_seen_at=utcnow(),
                    enrichment_status="pending",
                    enrichment_revision=0,
                    latest_score_revision=0,
                    latest_recommendation="unscored",
                    **normalized,
                )
                db.add(job)
                db.flush()
                inserted_count += 1
                run.inserted_count = inserted_count

            _log_feed_event(
                db,
                role_id=role.id,
                job_id=job.id,
                run_id=run.id,
                event_type=event_type,
                event_metadata={
                    "source": normalized.get("source"),
                    "company": job.company,
                    "company_id": company.id,
                    "company_portal_id": portal.id,
                },
            )

            try:
                dispatch_job_enrichment(
                    run_id=run.id,
                    job_id=job.id,
                    role_id=role.id,
                    user_id=user_id,
                    source_context={
                        "source_kind": source.kind,
                        "source_url": source.base_url,
                        "company_id": company.id,
                        "company_portal_id": portal.id,
                    },
                )
            except Exception as exc:
                process_error = f"{job.company} / {job.title}: dispatch failed: {exc}"
                record_enrichment_failure(
                    db, run=run, role_id=role.id, job=job, error_message=process_error
                )

            if event_type == "updated":
                run.updated_count = updated_count

    run.discovered_count = discovered_count
    run.inserted_count = inserted_count
    run.updated_count = updated_count
    run.expired_count = _expire_missing_company_jobs(
        db,
        user_id=user_id,
        role=role,
        company=company,
        portal_ids=portal_ids,
        seen_dedupe_keys=seen_dedupe_keys,
        run=run,
    )
    if discovered_count == 0:
        _maybe_finalize_run(run)
    elif run.enriched_count + run.failed_count < discovered_count:
        run.status = "running"
        run.finished_at = None
    else:
        _maybe_finalize_run(run)
    db.commit()
    db.refresh(run)
    return run
