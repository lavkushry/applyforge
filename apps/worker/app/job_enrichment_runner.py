import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.db import SessionLocal
from app.models import CandidateProfile, Job, JobFeedEvent, JobIngestionRun, JobScore, TargetRole
from app.persistence import persist_uploaded_file

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
MUST_HAVE_HINTS = ("must", "required", "need", "experience with", "strong")
NICE_TO_HAVE_HINTS = ("nice to have", "preferred", "bonus", "plus", "ideally")
RESPONSIBILITY_HINTS = ("you will", "responsibil", "build", "design", "lead", "own", "develop", "deliver", "maintain")
VISA_HINTS = ("visa", "sponsorship", "work authorization", "authorized to work")
SALARY_HINTS = ("salary", "compensation", "$", "per year", "base pay")
CANONICAL_SKILLS = {
    "Python": ("python",),
    "FastAPI": ("fastapi",),
    "React": ("react",),
    "TypeScript": ("typescript",),
    "SQL": ("sql", "postgres", "postgresql"),
    "Docker": ("docker", "container"),
    "Kubernetes": ("kubernetes", "k8s"),
    "Terraform": ("terraform",),
    "Cloud Systems": ("aws", "gcp", "azure", "cloud"),
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _split_sentences(text: str) -> list[str]:
    return [chunk.strip(" \t-•") for chunk in SENTENCE_SPLIT_RE.split(text) if chunk and chunk.strip(" \t-•")]


def _filter_sentences(sentences: list[str], hints: tuple[str, ...]) -> list[str]:
    return [sentence for sentence in sentences if any(hint in sentence.lower() for hint in hints)]


def _extract_job_skills(job_text: str) -> list[str]:
    lowered = job_text.lower()
    return [skill for skill, variants in CANONICAL_SKILLS.items() if any(keyword in lowered for keyword in variants)]


def _extract_requirement_skills(sentences: list[str]) -> list[str]:
    skills: list[str] = []
    for sentence in sentences:
        skills.extend(_extract_job_skills(sentence))
    return sorted(set(skills))


def _infer_remote_type(location: str, description: str) -> str:
    combined = f"{location} {description}".lower()
    if "hybrid" in combined:
        return "hybrid"
    if "remote" in combined:
        return "remote"
    if "onsite" in combined or "on-site" in combined:
        return "onsite"
    return "unknown"


def _infer_seniority(title: str, description: str) -> str:
    combined = f"{title} {description}".lower()
    for seniority in ("staff", "principal", "lead", "senior", "mid", "junior", "intern"):
        if seniority in combined:
            return seniority
    return "unknown"


def _infer_employment_type(description: str) -> str:
    lowered = description.lower()
    if "contract" in lowered:
        return "contract"
    if "part-time" in lowered:
        return "part-time"
    if "intern" in lowered:
        return "internship"
    return "full-time"


def _infer_tags(title: str, description: str) -> tuple[list[str], list[str]]:
    lowered = f"{title} {description}".lower()
    stack_tags = [
        tag
        for tag in ("python", "fastapi", "react", "typescript", "docker", "kubernetes", "postgresql", "ai", "terraform")
        if tag in lowered
    ]
    domain_tags = [tag for tag in ("saas", "ai", "fintech", "healthcare", "data", "platform") if tag in lowered]
    return sorted(set(stack_tags)), sorted(set(domain_tags))


def _normalize_job(job: Job) -> dict:
    stack_tags, domain_tags = _infer_tags(job.title, job.description)
    return {
        "remote_type": job.remote_type or _infer_remote_type(job.location, job.description),
        "seniority": job.seniority or _infer_seniority(job.title, job.description),
        "employment_type": job.employment_type or _infer_employment_type(job.description),
        "stack_tags": stack_tags,
        "domain_tags": domain_tags,
        "tags": sorted(set((job.tags or []) + stack_tags + domain_tags)),
    }


def _normalize_tokens(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value and value.strip()]


def _match_ratio(required: list[str], available: set[str]) -> tuple[list[str], list[str], float]:
    if not required:
        return [], [], 1.0
    matched = [skill for skill in required if skill.lower() in available]
    missing = [skill for skill in required if skill.lower() not in available]
    return matched, missing, len(matched) / len(required)


def _score_job(profile: CandidateProfile | None, job: Job, role: TargetRole) -> dict | None:
    if not profile:
        return None
    normalized_description = job.normalized_description or {}
    job_text = " ".join([job.title, job.description, job.location, " ".join(job.tags or [])])
    candidate_skills = list(dict.fromkeys(profile.skills or []))
    candidate_skill_lookup = {skill.lower(): skill for skill in candidate_skills}
    required_skills = normalized_description.get("must_have_skills") or _extract_job_skills(job_text)
    nice_to_have_skills = normalized_description.get("nice_to_have_skills") or []
    matched_required, missing_required, must_have_ratio = _match_ratio(required_skills, set(candidate_skill_lookup))
    matched_bonus, missing_bonus, nice_to_have_ratio = _match_ratio(nice_to_have_skills, set(candidate_skill_lookup))

    role_keywords = _normalize_tokens([role.name] + (role.aliases or []) + (role.keywords or []))
    target_role = (profile.basics or {}).get("target_role", "").lower()
    title = job.title.lower()
    if role_keywords:
        title_fit = 20 if any(keyword in title for keyword in role_keywords) else 12
    else:
        title_fit = 18 if target_role and target_role in title else 8

    must_have_fit = 28 * must_have_ratio
    nice_to_have_fit = 12 * nice_to_have_ratio
    preferred_locations = _normalize_tokens(role.preferred_locations or [])
    candidate_locations = _normalize_tokens((profile.basics or {}).get("preferred_locations", []))
    remote_preference = role.remote_preference or (profile.preferences or {}).get("remote_preference", "")
    location_blob = " ".join([job.location or "", job.remote_type or ""]).lower()
    location_fit = 6.0
    if "remote" in location_blob:
        location_fit = 8.0
    if preferred_locations and any(location in location_blob for location in preferred_locations):
        location_fit = 10.0
    elif candidate_locations and any(location in location_blob for location in candidate_locations):
        location_fit = 10.0
    if remote_preference == "remote" and "remote" in location_blob:
        location_fit = max(location_fit, 10.0)

    seniority_fit = 8.0
    if role.seniority and job.seniority:
        seniority_fit = 10.0 if role.seniority.lower() == job.seniority.lower() else 5.0

    domain_fit = 8.0 if "ai" in job_text.lower() and "ai" in (profile.summary or "").lower() else 5.0
    compensation_fit = 8.0 if role.salary_target and job.salary else 4.0
    visa_hints = " ".join(normalized_description.get("visa_hints", [])).lower()
    if role.visa_preference in {"not_required", "no_sponsorship_needed"} and "sponsorship" in visa_hints:
        visa_fit = 6.0 if "no sponsorship" in visa_hints or "not available" in visa_hints else 2.0
    else:
        visa_fit = 5.0
    extraction_confidence = float(normalized_description.get("extraction_confidence") or 0.0)
    application_readiness = 4.0
    if job.application_url:
        application_readiness += 2.0
    if job.enrichment_status == "completed":
        application_readiness += 2.0
    if extraction_confidence >= 0.75:
        application_readiness += 2.0
    application_readiness = min(application_readiness, 8.0)

    overall_score = max(
        0.0,
        min(
            100.0,
            title_fit
            + must_have_fit
            + nice_to_have_fit
            + location_fit
            + seniority_fit
            + domain_fit
            + compensation_fit
            + visa_fit
            + application_readiness,
        ),
    )
    recommendation = "high priority" if overall_score >= 78 else "maybe" if overall_score >= 58 else "skip"
    strengths = matched_required + [skill for skill in matched_bonus if skill not in matched_required]
    missing_skills = missing_required + [skill for skill in missing_bonus if skill not in missing_required]
    reasons = [
        f"Title fit contributed {title_fit:.0f} points based on role-title alignment.",
        f"Must-have coverage contributed {must_have_fit:.0f} points across {len(matched_required)} matched requirements.",
        f"Application readiness contributed {application_readiness:.0f} points using enrichment completeness and apply-link availability.",
    ]
    if missing_required:
        reasons.append(f"Missing must-have requirements: {', '.join(missing_required)}.")
    if missing_bonus:
        reasons.append(f"Uncovered bonus signals: {', '.join(missing_bonus)}.")

    return {
        "enrichment_revision": job.enrichment_revision,
        "overall_score": float(overall_score),
        "score_breakdown": {
            "title_fit": title_fit,
            "must_have_fit": must_have_fit,
            "nice_to_have_fit": nice_to_have_fit,
            "seniority_fit": seniority_fit,
            "domain_fit": domain_fit,
            "location_fit": location_fit,
            "compensation_fit": compensation_fit,
            "visa_fit": visa_fit,
            "application_readiness": application_readiness,
            "extraction_confidence": extraction_confidence,
            "role_match": title_fit,
            "skills_match": must_have_fit + nice_to_have_fit,
            "seniority_alignment": seniority_fit,
            "domain_relevance": domain_fit,
            "location_match": location_fit,
            "bonus_qualifications": visa_fit,
            "must_have_penalty": float(len(missing_required) * 4),
        },
        "missing_skills": missing_skills,
        "strengths": strengths,
        "reasons": reasons,
        "recommendation": recommendation,
    }


def _log_event(db, *, role_id: int, job_id: int, run_id: int, event_type: str, event_metadata: dict) -> None:
    db.add(
        JobFeedEvent(
            role_id=role_id,
            job_id=job_id,
            run_id=run_id,
            event_type=event_type,
            event_metadata=event_metadata,
        )
    )


def _finalize_run(run: JobIngestionRun) -> None:
    processed = run.enriched_count + run.failed_count
    if processed < run.discovered_count:
        run.status = "running"
        run.finished_at = None
        return
    run.status = "failed" if run.failed_count else "completed"
    run.finished_at = utcnow()


def _persist_snapshot(job: Job, source_context: dict) -> int:
    directory = _ensure_directory(Path(settings.artifacts_path) / "job-enrichment")
    filename = f"job-{job.id}-enrichment-{uuid4().hex}.json"
    path = directory / filename
    payload = json.dumps(
        {
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "application_url": job.application_url,
            "description": job.description,
            "normalized_description": job.normalized_description,
            "source_context": source_context,
        },
        indent=2,
        sort_keys=True,
    )
    path.write_text(payload, encoding="utf-8")
    return persist_uploaded_file(
        user_id=job.user_id,
        path=str(path),
        original_name=filename,
        mime_type="application/json",
    )


def run_job_enrichment(run_id: int, job_id: int, role_id: int, user_id: int, source_context: dict | None = None) -> dict:
    source_context = source_context or {}
    with SessionLocal() as db:
        run = db.query(JobIngestionRun).filter(JobIngestionRun.id == run_id).first()
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        role = db.query(TargetRole).filter(TargetRole.id == role_id, TargetRole.user_id == user_id).first()
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not run or not job or not role:
            raise ValueError("Missing enrichment context")

        try:
            normalized = _normalize_job(job)
            sentences = _split_sentences(job.description or "")
            must_have_sentences = _filter_sentences(sentences, MUST_HAVE_HINTS)
            nice_to_have_sentences = _filter_sentences(sentences, NICE_TO_HAVE_HINTS)
            responsibility_sentences = _filter_sentences(sentences, RESPONSIBILITY_HINTS)
            visa_sentences = _filter_sentences(sentences, VISA_HINTS)
            salary_sentences = _filter_sentences(sentences, SALARY_HINTS)
            must_have_skills = _extract_requirement_skills(must_have_sentences) or _extract_job_skills(job.description or "")
            nice_to_have_skills = _extract_requirement_skills(nice_to_have_sentences)
            sections = {
                "responsibilities": responsibility_sentences[:6],
                "requirements": must_have_sentences[:6],
                "nice_to_have": nice_to_have_sentences[:6],
                "visa_hints": visa_sentences[:3],
                "salary_hints": salary_sentences[:3],
            }
            populated_sections = [name for name, values in sections.items() if values]
            extraction_confidence = min(0.95, 0.35 + len(populated_sections) * 0.1 + min(len(must_have_skills), 4) * 0.05)

            job.remote_type = normalized["remote_type"]
            job.seniority = normalized["seniority"]
            job.employment_type = normalized["employment_type"]
            job.tags = normalized["tags"]
            job.stack_tags = normalized["stack_tags"]
            job.domain_tags = normalized["domain_tags"]
            job.enrichment_status = "completed"
            job.enrichment_error = ""
            job.enrichment_revision = max(job.enrichment_revision, 0) + 1
            job.normalized_description = {
                **(job.normalized_description or {}),
                "summary": (job.description or "")[:500],
                "remote_type": job.remote_type,
                "seniority": job.seniority,
                "employment_type": job.employment_type,
                "must_have_skills": must_have_skills,
                "nice_to_have_skills": nice_to_have_skills,
                "responsibilities": sections["responsibilities"],
                "requirements": sections["requirements"],
                "nice_to_have": sections["nice_to_have"],
                "visa_hints": sections["visa_hints"],
                "salary_hints": sections["salary_hints"],
                "extraction_confidence": extraction_confidence,
            }
            job.enrichment_metadata = {
                "extraction_confidence": extraction_confidence,
                "sections_found": populated_sections,
                "must_have_count": len(must_have_skills),
                "nice_to_have_count": len(nice_to_have_skills),
                "source_kind": source_context.get("source_kind", ""),
                "source_url": source_context.get("source_url", ""),
            }
            job.source_document_file_id = _persist_snapshot(job, source_context)
            _log_event(
                db,
                role_id=role.id,
                job_id=job.id,
                run_id=run.id,
                event_type="enriched",
                event_metadata={
                    "confidence": extraction_confidence,
                    "must_have_count": len(must_have_skills),
                },
            )

            score_payload = _score_job(profile, job, role)
            if score_payload:
                job.latest_score = score_payload["overall_score"]
                job.latest_score_revision = score_payload["enrichment_revision"]
                job.latest_recommendation = score_payload["recommendation"]
                job.last_scored_at = utcnow()
                db.add(JobScore(job_id=job.id, role_id=role.id, **score_payload))
                _log_event(
                    db,
                    role_id=role.id,
                    job_id=job.id,
                    run_id=run.id,
                    event_type="score_changed",
                    event_metadata={
                        "overall_score": score_payload["overall_score"],
                        "recommendation": score_payload["recommendation"],
                        "enrichment_revision": score_payload["enrichment_revision"],
                    },
                )

            run.enriched_count += 1
            _finalize_run(run)
            db.commit()
            return {"status": "completed", "job_id": job.id, "run_id": run.id}
        except Exception as exc:
            job.enrichment_status = "failed"
            job.enrichment_error = str(exc)
            run.failed_count += 1
            run.error_message = "\n".join(filter(None, [run.error_message, f"{job.company} / {job.title}: {exc}"]))
            _log_event(
                db,
                role_id=role.id,
                job_id=job.id,
                run_id=run.id,
                event_type="enrichment_failed",
                event_metadata={"error": str(exc)},
            )
            _finalize_run(run)
            db.commit()
            raise
