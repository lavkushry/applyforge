from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from sqlalchemy.orm import Session

from app.models.entities import CandidateProfile, Job, JobFeedEvent, JobIngestionRun, JobScore, TargetRole, TargetRoleSource
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


def score_and_attach_job(db: Session, job: Job, profile: CandidateProfile | None, role: TargetRole) -> None:
    if not profile:
        return
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
    job.latest_recommendation = score_payload["recommendation"]
    db.add(JobScore(job_id=job.id, role_id=role.id, **score_payload))


def ingest_target_role(db: Session, user_id: int, role: TargetRole) -> JobIngestionRun:
    run = JobIngestionRun(role_id=role.id, status="running")
    db.add(run)
    db.flush()
    sources = db.query(TargetRoleSource).filter(TargetRoleSource.role_id == role.id, TargetRoleSource.enabled.is_(True)).all()
    run.source_count = len(sources)
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    discovered_count = 0
    inserted_count = 0
    updated_count = 0
    try:
        for source in sources:
            for payload in fetch_jobs_for_source(source):
                discovered_count += 1
                normalized = normalize_job_payload({**payload, "role_id": role.id})
                existing = db.query(Job).filter(Job.dedupe_key == normalized["dedupe_key"]).first()
                event_type = "discovered"
                if existing:
                    existing.role_id = role.id
                    existing.last_seen_at = utcnow()
                    existing.active = True
                    existing.expired_at = None
                    existing.source_metadata = normalized.get("source_metadata", {})
                    existing.description = normalized["description"]
                    existing.normalized_description = normalized["normalized_description"]
                    job = existing
                    updated_count += 1
                    event_type = "updated"
                else:
                    job = Job(
                        user_id=user_id,
                        first_seen_at=utcnow(),
                        last_seen_at=utcnow(),
                        **normalized,
                    )
                    db.add(job)
                    db.flush()
                    inserted_count += 1
                score_and_attach_job(db, job, profile, role)
                db.add(
                    JobFeedEvent(
                        role_id=role.id,
                        job_id=job.id,
                        run_id=run.id,
                        event_type=event_type,
                        event_metadata={"source": normalized.get("source"), "company": job.company},
                    )
                )
            source.last_checked_at = utcnow()
        run.status = "completed"
    except Exception as exc:
        run.status = "failed"
        run.error_message = str(exc)
    run.discovered_count = discovered_count
    run.inserted_count = inserted_count
    run.updated_count = updated_count
    run.finished_at = utcnow()
    db.commit()
    db.refresh(run)
    return run
