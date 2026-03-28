from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from sqlalchemy.orm import Session

from app.models.entities import CandidateProfile, Job, JobFeedEvent, JobIngestionRun, JobScore, TargetRole, TargetRoleSource
from app.services.company_directory import resolve_company_for_job
from app.services.job_dispatch import dispatch_job_enrichment
from app.services.job_enrichment import enrich_job_record
from app.services.job_normalizer import normalize_job_payload
from app.services.scoring import score_job


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _board_slug_from_url(url: str) -> str:
    path_bits = [bit for bit in urlparse(url).path.split("/") if bit]
    return path_bits[-1] if path_bits else ""


def _company_from_url(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    cleaned = hostname.replace("www.", "").split(".")[0]
    return cleaned.replace("-", " ").title() or "Unknown Company"


def _fetch_greenhouse_jobs(source: TargetRoleSource) -> list[dict]:
    board_token = source.config.get("board_token") or _board_slug_from_url(source.base_url)
    if not board_token:
        return []
    response = httpx.get(f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs", timeout=10.0)
    response.raise_for_status()
    jobs = []
    for item in response.json().get("jobs", []):
        jobs.append(
            {
                "title": item.get("title", ""),
                "company": source.label or _company_from_url(source.base_url),
                "location": item.get("location", {}).get("name", ""),
                "application_url": item.get("absolute_url", ""),
                "description": item.get("metadata", [{}])[0].get("value", "") or item.get("title", ""),
                "source": "greenhouse",
                "source_metadata": {"source_label": source.label, "source_kind": source.kind},
            }
        )
    return jobs


def _fetch_lever_jobs(source: TargetRoleSource) -> list[dict]:
    site_token = source.config.get("site_token") or _board_slug_from_url(source.base_url)
    if not site_token:
        return []
    response = httpx.get(f"https://api.lever.co/v0/postings/{site_token}?mode=json", timeout=10.0)
    response.raise_for_status()
    jobs = []
    for item in response.json():
        jobs.append(
            {
                "title": item.get("text", ""),
                "company": source.label or _company_from_url(source.base_url),
                "location": item.get("categories", {}).get("location", ""),
                "application_url": item.get("hostedUrl", ""),
                "description": item.get("descriptionPlain", "") or item.get("text", ""),
                "source": "lever",
                "source_metadata": {"source_label": source.label, "source_kind": source.kind},
            }
        )
    return jobs


def _fetch_direct_jobs(source: TargetRoleSource) -> list[dict]:
    response = httpx.get(source.base_url, timeout=10.0)
    response.raise_for_status()
    title = response.text.split("<title>")[1].split("</title>")[0] if "<title>" in response.text else "Career Opportunity"
    return [
        {
            "title": title.strip(),
            "company": source.label or _company_from_url(source.base_url),
            "location": source.config.get("location", ""),
            "application_url": source.base_url,
            "description": response.text[:1000],
            "source": "direct_url",
            "source_metadata": {"source_label": source.label, "source_kind": source.kind},
        }
    ]


def fetch_jobs_for_source(source: TargetRoleSource) -> list[dict]:
    if source.kind == "greenhouse_board":
        return _fetch_greenhouse_jobs(source)
    if source.kind == "lever_board":
        return _fetch_lever_jobs(source)
    if source.kind == "direct_url":
        return _fetch_direct_jobs(source)
    return []


def _log_feed_event(
    db: Session,
    *,
    role_id: int,
    job_id: int,
    run_id: int,
    event_type: str,
    event_metadata: dict,
) -> None:
    db.add(
        JobFeedEvent(
            role_id=role_id,
            job_id=job_id,
            run_id=run_id,
            event_type=event_type,
            event_metadata=event_metadata,
        )
    )


def _score_and_attach_job(db: Session, job: Job, profile: CandidateProfile | None, role: TargetRole) -> JobScore | None:
    if not profile:
        return None
    score_payload = score_job(
        {
            "basics": profile.basics,
            "skills": profile.skills,
            "summary": profile.summary,
            "preferences": profile.preferences,
        },
        {
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "remote_type": job.remote_type,
            "seniority": job.seniority,
            "salary": job.salary,
            "tags": job.tags,
            "application_url": job.application_url,
            "normalized_description": job.normalized_description,
            "enrichment_status": job.enrichment_status,
            "enrichment_revision": job.enrichment_revision,
        },
        {
            "name": role.name,
            "aliases": role.aliases,
            "keywords": role.keywords,
            "preferred_locations": role.preferred_locations,
            "remote_preference": role.remote_preference,
            "salary_target": role.salary_target,
            "visa_preference": role.visa_preference,
            "seniority": role.seniority,
        },
    )
    job.latest_score = score_payload["overall_score"]
    job.latest_score_revision = score_payload["enrichment_revision"]
    job.latest_recommendation = score_payload["recommendation"]
    job.last_scored_at = utcnow()
    score_row = JobScore(job_id=job.id, role_id=role.id, **score_payload)
    db.add(score_row)
    db.flush()
    return score_row


def _maybe_finalize_run(run: JobIngestionRun) -> None:
    processed = run.enriched_count + run.failed_count
    if processed < run.discovered_count:
        run.status = "running"
        run.finished_at = None
        return
    run.status = "failed" if run.failed_count else "completed"
    run.finished_at = utcnow()


def process_job_enrichment(
    db: Session,
    *,
    run: JobIngestionRun,
    user_id: int,
    role: TargetRole,
    job: Job,
    source_context: dict | None = None,
) -> None:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    enrichment = enrich_job_record(
        db,
        user_id=user_id,
        job=job,
        raw_payload={
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "remote_type": job.remote_type,
            "salary": job.salary,
            "source": job.source,
            "application_url": job.application_url,
            "description": job.description,
            "seniority": job.seniority,
            "employment_type": job.employment_type,
            "visa_support": job.visa_support,
            "tags": job.tags,
            "source_metadata": job.source_metadata,
        },
        source_kind=(source_context or {}).get("source_kind", ""),
        source_url=(source_context or {}).get("source_url", ""),
    )
    run.enriched_count += 1
    _log_feed_event(
        db,
        role_id=role.id,
        job_id=job.id,
        run_id=run.id,
        event_type="enriched",
        event_metadata={
            "confidence": job.enrichment_metadata.get("extraction_confidence", 0.0),
            "must_have_count": len(enrichment.get("must_have_skills", [])),
        },
    )
    score_row = _score_and_attach_job(db, job, profile, role)
    if score_row:
        _log_feed_event(
            db,
            role_id=role.id,
            job_id=job.id,
            run_id=run.id,
            event_type="score_changed",
            event_metadata={
                "overall_score": score_row.overall_score,
                "recommendation": score_row.recommendation,
                "enrichment_revision": score_row.enrichment_revision,
            },
        )
    _maybe_finalize_run(run)


def record_enrichment_failure(db: Session, *, run: JobIngestionRun, role_id: int, job: Job, error_message: str) -> None:
    job.enrichment_status = "failed"
    job.enrichment_error = error_message
    run.failed_count += 1
    run.error_message = "\n".join(filter(None, [run.error_message, error_message]))
    _log_feed_event(
        db,
        role_id=role_id,
        job_id=job.id,
        run_id=run.id,
        event_type="enrichment_failed",
        event_metadata={"error": error_message},
    )
    _maybe_finalize_run(run)


def _expire_missing_jobs(db: Session, *, user_id: int, role: TargetRole, seen_dedupe_keys: set[str], run: JobIngestionRun) -> int:
    expired_count = 0
    active_jobs = db.query(Job).filter(Job.user_id == user_id, Job.role_id == role.id, Job.active.is_(True)).all()
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
            event_metadata={"company": job.company, "title": job.title},
        )
    return expired_count


def ingest_target_role(db: Session, user_id: int, role: TargetRole) -> JobIngestionRun:
    run = JobIngestionRun(role_id=role.id, status="running")
    db.add(run)
    db.flush()
    sources = db.query(TargetRoleSource).filter(TargetRoleSource.role_id == role.id, TargetRoleSource.enabled.is_(True)).all()
    run.source_count = len(sources)
    discovered_count = 0
    inserted_count = 0
    updated_count = 0
    seen_dedupe_keys: set[str] = set()

    for source in sources:
        try:
            payloads = fetch_jobs_for_source(source)
        except Exception as exc:
            run.failed_count += 1
            run.error_message = "\n".join(filter(None, [run.error_message, f"{source.label or source.base_url}: {exc}"]))
            source.last_checked_at = utcnow()
            continue

        for payload in payloads:
            discovered_count += 1
            run.discovered_count = discovered_count
            normalized = normalize_job_payload({**payload, "role_id": role.id})
            seen_dedupe_keys.add(normalized["dedupe_key"])
            resolved_company = resolve_company_for_job(
                db,
                user_id=user_id,
                company_name=normalized.get("company", ""),
                application_url=normalized.get("application_url", ""),
                source_url=source.base_url,
            )
            normalized["company_id"] = resolved_company.id if resolved_company else None
            existing = db.query(Job).filter(Job.dedupe_key == normalized["dedupe_key"]).first()
            event_type = "discovered"
            if existing:
                existing.role_id = role.id
                existing.company_id = normalized.get("company_id")
                existing.last_seen_at = utcnow()
                existing.active = True
                existing.expired_at = None
                existing.source_metadata = normalized.get("source_metadata", {})
                existing.description = normalized["description"]
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
                event_metadata={"source": normalized.get("source"), "company": job.company},
            )

            try:
                dispatch_job_enrichment(
                    run_id=run.id,
                    job_id=job.id,
                    role_id=role.id,
                    user_id=user_id,
                    source_context={"source_kind": source.kind, "source_url": source.base_url},
                )
            except Exception as exc:
                process_error = f"{job.company} / {job.title}: dispatch failed: {exc}"
                record_enrichment_failure(db, run=run, role_id=role.id, job=job, error_message=process_error)
            if event_type == "updated":
                run.updated_count = updated_count
        source.last_checked_at = utcnow()

    run.discovered_count = discovered_count
    run.inserted_count = inserted_count
    run.updated_count = updated_count
    run.expired_count = _expire_missing_jobs(db, user_id=user_id, role=role, seen_dedupe_keys=seen_dedupe_keys, run=run)
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
