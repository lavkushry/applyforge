from sqlalchemy.orm import Session

from app.models.entities import Application, CandidateProfile, CoverLetter, Job, Resume, ResumeVersion, TargetRole, UploadedFile, User

REQUIRED_ANSWER_KEYS = ("full_name", "email", "phone", "work_authorization")


def _link_value(links: list[dict], *match_terms: str) -> str:
    for link in links:
        label = str(link.get("label", "")).lower()
        url = str(link.get("url", ""))
        if any(term in label for term in match_terms) and url:
            return url
    return ""


def _resolve_resume_file(db: Session, user_id: int, job_id: int) -> UploadedFile | None:
    tailored = (
        db.query(UploadedFile)
        .join(ResumeVersion, ResumeVersion.pdf_file_id == UploadedFile.id)
        .join(Resume, Resume.id == ResumeVersion.resume_id)
        .filter(Resume.user_id == user_id, ResumeVersion.job_id == job_id)
        .order_by(ResumeVersion.created_at.desc(), ResumeVersion.id.desc())
        .first()
    )
    if tailored:
        return tailored

    latest_exported = (
        db.query(UploadedFile)
        .join(ResumeVersion, ResumeVersion.pdf_file_id == UploadedFile.id)
        .join(Resume, Resume.id == ResumeVersion.resume_id)
        .filter(Resume.user_id == user_id)
        .order_by(ResumeVersion.created_at.desc(), ResumeVersion.id.desc())
        .first()
    )
    if latest_exported:
        return latest_exported

    fallback_resume = (
        db.query(UploadedFile)
        .join(Resume, Resume.uploaded_file_id == UploadedFile.id)
        .filter(Resume.user_id == user_id, Resume.active.is_(True))
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .first()
    )
    return fallback_resume


def _resolve_cover_letter(db: Session, job_id: int) -> CoverLetter | None:
    return (
        db.query(CoverLetter)
        .filter(CoverLetter.job_id == job_id)
        .order_by(CoverLetter.created_at.desc(), CoverLetter.id.desc())
        .first()
    )


def _resolve_answers(profile: CandidateProfile | None, user: User, extra_answers: dict | None = None) -> tuple[dict, dict]:
    basics = profile.basics if profile else {}
    preferences = profile.preferences if profile else {}
    saved_answers = profile.saved_answers if profile else {}
    links = profile.links if profile else []
    answers = {
        "full_name": basics.get("full_name", ""),
        "email": basics.get("email", "") or user.email,
        "phone": basics.get("phone", ""),
        "location": basics.get("location", ""),
        "work_authorization": preferences.get("work_authorization", ""),
        "notice_period": saved_answers.get("notice_period", ""),
        "salary_expectation": saved_answers.get("salary_expectation", ""),
        "linkedin_url": _link_value(links, "linkedin"),
        "github_url": _link_value(links, "github"),
        "portfolio_url": _link_value(links, "portfolio", "website"),
    }
    provenance = {
        "full_name": "profile.basics",
        "email": "profile.basics" if basics.get("email") else "user.email",
        "phone": "profile.basics",
        "location": "profile.basics",
        "work_authorization": "profile.preferences",
        "notice_period": "profile.saved_answers",
        "salary_expectation": "profile.saved_answers",
        "linkedin_url": "profile.links",
        "github_url": "profile.links",
        "portfolio_url": "profile.links",
    }
    for key, value in (extra_answers or {}).items():
        if value not in (None, ""):
            answers[key] = value
            provenance[key] = "request.override"
    return answers, provenance


def build_application_packet(
    db: Session,
    *,
    application: Application,
    job: Job,
    user: User,
    profile: CandidateProfile | None,
    role: TargetRole | None,
    mode: str,
    extra_answers: dict | None = None,
) -> dict:
    answers, provenance = _resolve_answers(profile, user, extra_answers)
    resume_file = _resolve_resume_file(db, user.id, job.id)
    cover_letter = _resolve_cover_letter(db, job.id)
    missing_answers = [key for key in REQUIRED_ANSWER_KEYS if not answers.get(key)]
    blocking_issues = []
    if not job.application_url:
        blocking_issues.append("Missing application URL")
    if not resume_file:
        blocking_issues.append("Missing resume upload")
    if job.enrichment_status != "completed":
        blocking_issues.append("Job enrichment is incomplete")
    if job.latest_score_revision < job.enrichment_revision:
        blocking_issues.append("Job score is stale against the latest enrichment revision")

    threshold = role.min_auto_apply_score if role else 85.0
    auto_policy_reasons = []
    if mode == "auto":
        if not role or not role.automation_enabled:
            auto_policy_reasons.append("Role automation is disabled")
        if job.latest_score < threshold:
            auto_policy_reasons.append(f"Score {job.latest_score:.0f} is below threshold {threshold:.0f}")
        if missing_answers:
            auto_policy_reasons.append("Required answers are missing")
        if blocking_issues:
            auto_policy_reasons.extend(blocking_issues)

    risk_summary: list[str] = []
    extraction_confidence = float(job.enrichment_metadata.get("extraction_confidence", 0.0) or 0.0)
    if job.enrichment_status == "completed" and extraction_confidence and extraction_confidence < 0.55:
        risk_summary.append("Job extraction confidence is low")
    ready = not blocking_issues and not missing_answers
    auto_submit_allowed = mode == "auto" and not auto_policy_reasons and ready and not risk_summary

    return {
        "mode": mode,
        "user_id": user.id,
        "application_id": application.id,
        "job_id": job.id,
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "application_url": job.application_url,
        },
        "role": {
            "id": role.id if role else None,
            "name": role.name if role else "",
            "automation_enabled": role.automation_enabled if role else False,
            "min_auto_apply_score": threshold,
        },
        "answers": answers,
        "answer_provenance": provenance,
        "resume_file_id": resume_file.id if resume_file else None,
        "cover_letter_id": cover_letter.id if cover_letter else None,
        "upload_ready": bool(resume_file),
        "missing_answers": missing_answers,
        "risk_summary": risk_summary,
        "blocking_issues": blocking_issues,
        "auto_submit_allowed": auto_submit_allowed,
        "auto_policy_reasons": auto_policy_reasons,
        "ready": ready,
    }


def summarize_application_packet(packet: dict) -> dict:
    return {
        "ready": packet["ready"],
        "auto_submit_allowed": packet["auto_submit_allowed"],
        "resume_file_id": packet["resume_file_id"],
        "cover_letter_id": packet["cover_letter_id"],
        "missing_answers": packet["missing_answers"],
        "risk_summary": packet["risk_summary"],
        "blocking_issues": packet["blocking_issues"] + packet.get("auto_policy_reasons", []),
        "answer_keys": sorted(packet["answers"].keys()),
    }
