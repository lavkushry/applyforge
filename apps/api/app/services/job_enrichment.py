import json
import re
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Job, UploadedFile
from app.services.files import ensure_directory, sha256_bytes
from app.services.job_normalizer import normalize_job_payload
from app.services.scoring import extract_job_skills

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
MUST_HAVE_HINTS = ("must", "required", "need", "experience with", "strong")
NICE_TO_HAVE_HINTS = ("nice to have", "preferred", "bonus", "plus", "ideally")
RESPONSIBILITY_HINTS = ("you will", "responsibil", "build", "design", "lead", "own", "develop", "deliver", "maintain")
VISA_HINTS = ("visa", "sponsorship", "work authorization", "authorized to work")
SALARY_HINTS = ("salary", "compensation", "$", "per year", "base pay")


def _split_sentences(text: str) -> list[str]:
    return [chunk.strip(" \t-•") for chunk in SENTENCE_SPLIT_RE.split(text) if chunk and chunk.strip(" \t-•")]


def _filter_sentences(sentences: list[str], hints: tuple[str, ...]) -> list[str]:
    return [sentence for sentence in sentences if any(hint in sentence.lower() for hint in hints)]


def _extract_requirement_skills(sentences: list[str]) -> list[str]:
    skills: list[str] = []
    for sentence in sentences:
        skills.extend(extract_job_skills(sentence))
    return sorted(set(skills))


def _snapshot_payload(job: Job, raw_payload: dict, cleaned_description: str, extraction: dict) -> bytes:
    payload = {
        "job_id": job.id,
        "job_title": job.title,
        "company": job.company,
        "application_url": job.application_url,
        "raw_payload": raw_payload,
        "cleaned_description": cleaned_description,
        "extraction": extraction,
    }
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def _persist_snapshot(db: Session, user_id: int, job: Job, content: bytes) -> UploadedFile:
    directory = ensure_directory(Path(settings.artifacts_path) / "job-enrichment")
    filename = f"job-{job.id}-enrichment-{uuid4().hex}.json"
    path = directory / filename
    path.write_bytes(content)
    uploaded = UploadedFile(
        user_id=user_id,
        original_name=filename,
        path=str(path),
        mime_type="application/json",
        size_bytes=len(content),
        checksum=sha256_bytes(content),
    )
    db.add(uploaded)
    db.flush()
    return uploaded


def enrich_job_record(
    db: Session,
    *,
    user_id: int,
    job: Job,
    raw_payload: dict,
    source_kind: str = "",
    source_url: str = "",
) -> dict:
    description = str(raw_payload.get("description") or job.description or "").strip()
    sentences = _split_sentences(description)
    must_have_sentences = _filter_sentences(sentences, MUST_HAVE_HINTS)
    nice_to_have_sentences = _filter_sentences(sentences, NICE_TO_HAVE_HINTS)
    responsibility_sentences = _filter_sentences(sentences, RESPONSIBILITY_HINTS)
    visa_sentences = _filter_sentences(sentences, VISA_HINTS)
    salary_sentences = _filter_sentences(sentences, SALARY_HINTS)

    must_have_skills = _extract_requirement_skills(must_have_sentences) or extract_job_skills(description)
    nice_to_have_skills = _extract_requirement_skills(nice_to_have_sentences)
    required_sections = {
        "responsibilities": responsibility_sentences[:6],
        "requirements": must_have_sentences[:6],
        "nice_to_have": nice_to_have_sentences[:6],
        "visa_hints": visa_sentences[:3],
        "salary_hints": salary_sentences[:3],
    }
    populated_sections = [name for name, values in required_sections.items() if values]
    extraction_confidence = min(
        0.95,
        0.35 + len(populated_sections) * 0.1 + min(len(must_have_skills), 4) * 0.05,
    )

    normalized = normalize_job_payload(
        {
            "title": raw_payload.get("title", job.title),
            "company": raw_payload.get("company", job.company),
            "location": raw_payload.get("location", job.location),
            "remote_type": raw_payload.get("remote_type", job.remote_type),
            "salary": raw_payload.get("salary", job.salary),
            "source": raw_payload.get("source", job.source),
            "application_url": raw_payload.get("application_url", job.application_url),
            "description": description,
            "seniority": raw_payload.get("seniority", job.seniority),
            "employment_type": raw_payload.get("employment_type", job.employment_type),
            "visa_support": raw_payload.get("visa_support", job.visa_support),
            "tags": raw_payload.get("tags", job.tags),
            "role_id": raw_payload.get("role_id", job.role_id),
            "source_metadata": raw_payload.get("source_metadata", job.source_metadata),
        }
    )

    enrichment_payload = {
        **required_sections,
        "must_have_skills": must_have_skills,
        "nice_to_have_skills": nice_to_have_skills,
        "extraction_confidence": extraction_confidence,
        "source_kind": source_kind or raw_payload.get("source", job.source),
        "source_url": source_url,
    }
    snapshot = _persist_snapshot(
        db,
        user_id,
        job,
        _snapshot_payload(job, raw_payload, description, enrichment_payload),
    )

    job.title = normalized["title"]
    job.company = normalized["company"]
    job.location = normalized["location"]
    job.remote_type = normalized["remote_type"]
    job.salary = normalized["salary"]
    job.source = normalized["source"]
    job.application_url = normalized["application_url"]
    job.description = normalized["description"]
    job.normalized_description = {**normalized["normalized_description"], **enrichment_payload}
    job.seniority = normalized["seniority"]
    job.employment_type = normalized["employment_type"]
    job.visa_support = normalized["visa_support"]
    job.tags = normalized["tags"]
    job.stack_tags = normalized["stack_tags"]
    job.domain_tags = normalized["domain_tags"]
    job.source_metadata = normalized.get("source_metadata", {})
    job.enrichment_status = "completed"
    job.enrichment_error = ""
    job.enrichment_revision = max(job.enrichment_revision, 0) + 1
    job.source_document_file_id = snapshot.id
    job.enrichment_metadata = {
        "extraction_confidence": extraction_confidence,
        "sections_found": populated_sections,
        "must_have_count": len(must_have_skills),
        "nice_to_have_count": len(nice_to_have_skills),
        "snapshot_file_id": snapshot.id,
        "source_kind": enrichment_payload["source_kind"],
        "source_url": source_url,
    }
    return enrichment_payload
