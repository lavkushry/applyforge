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


def _normalize_tokens(values: list[str]) -> list[str]:
    return [value.strip().lower() for value in values if value and value.strip()]


def extract_job_skills(job_text: str) -> list[str]:
    lowered = job_text.lower()
    return [skill for skill, variants in CANONICAL_SKILLS.items() if any(keyword in lowered for keyword in variants)]


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def _match_ratio(required: list[str], available: set[str]) -> tuple[list[str], list[str], float]:
    if not required:
        return [], [], 1.0
    matched = [skill for skill in required if skill.lower() in available]
    missing = [skill for skill in required if skill.lower() not in available]
    return matched, missing, len(matched) / len(required)


def score_job(candidate: dict, job: dict, role: dict | None = None) -> dict:
    normalized_description = job.get("normalized_description", {}) or {}
    job_text = " ".join(
        [
            job.get("title", ""),
            job.get("description", ""),
            job.get("location", ""),
            " ".join(job.get("tags", [])),
        ]
    )
    candidate_skills = list(dict.fromkeys(candidate.get("skills", [])))
    candidate_skill_lookup = {skill.lower(): skill for skill in candidate_skills}
    required_skills = normalized_description.get("must_have_skills") or extract_job_skills(job_text)
    nice_to_have_skills = normalized_description.get("nice_to_have_skills") or []
    matched_required, missing_required, must_have_ratio = _match_ratio(required_skills, set(candidate_skill_lookup))
    matched_bonus, missing_bonus, nice_to_have_ratio = _match_ratio(nice_to_have_skills, set(candidate_skill_lookup))

    role_keywords = _normalize_tokens(
        [role.get("name", "")] if role else []
        + (role.get("aliases", []) if role else [])
        + (role.get("keywords", []) if role else [])
    )
    target_role = candidate.get("basics", {}).get("target_role", "").lower()
    title = job.get("title", "").lower()
    if role_keywords:
        title_fit = 20 if any(keyword in title for keyword in role_keywords) else 12
    else:
        title_fit = 18 if target_role and target_role in title else 12 if any(token in title for token in target_role.split()) else 8

    must_have_fit = 28 * must_have_ratio
    nice_to_have_fit = 12 * nice_to_have_ratio

    preferred_locations = _normalize_tokens((role or {}).get("preferred_locations", []))
    candidate_locations = _normalize_tokens(candidate.get("basics", {}).get("preferred_locations", []))
    remote_preference = (role or {}).get("remote_preference") or candidate.get("preferences", {}).get("remote_preference", "")
    location_blob = " ".join([job.get("location", ""), job.get("remote_type", "")]).lower()
    location_fit = 6.0
    if "remote" in location_blob:
        location_fit = 8.0
    if preferred_locations and any(location in location_blob for location in preferred_locations):
        location_fit = 10.0
    elif candidate_locations and any(location in location_blob for location in candidate_locations):
        location_fit = 10.0
    if remote_preference == "remote" and "remote" in location_blob:
        location_fit = max(location_fit, 10.0)

    seniority = job.get("seniority", "").lower()
    desired_seniority = ((role or {}).get("seniority") or "").lower()
    seniority_fit = 8.0
    if desired_seniority and seniority:
        seniority_fit = 10.0 if desired_seniority == seniority else 5.0
    elif seniority in {"staff", "principal", "lead", "senior"}:
        seniority_fit = 9.0

    domain_fit = 8.0 if "ai" in job_text.lower() and "ai" in candidate.get("summary", "").lower() else 5.0

    compensation_fit = 4.0
    if (role or {}).get("salary_target") and job.get("salary"):
        compensation_fit = 8.0
    elif job.get("salary"):
        compensation_fit = 6.0

    visa_preference = (role or {}).get("visa_preference")
    visa_hints = " ".join(normalized_description.get("visa_hints", [])).lower()
    visa_fit = 4.0
    if visa_preference in {"not_required", "no_sponsorship_needed"} and "sponsorship" in visa_hints:
        visa_fit = 6.0 if "no sponsorship" in visa_hints or "not available" in visa_hints else 2.0
    elif visa_preference in {"sponsorship_ok", "unknown"}:
        visa_fit = 5.0

    extraction_confidence = float(normalized_description.get("extraction_confidence") or 0.0)
    application_readiness = 4.0
    if job.get("application_url"):
        application_readiness += 2.0
    if job.get("enrichment_status") == "completed":
        application_readiness += 2.0
    if extraction_confidence >= 0.75:
        application_readiness += 2.0
    application_readiness = min(application_readiness, 8.0)

    overall_score = clamp_score(
        title_fit
        + must_have_fit
        + nice_to_have_fit
        + location_fit
        + seniority_fit
        + domain_fit
        + compensation_fit
        + visa_fit
        + application_readiness
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
        "enrichment_revision": int(job.get("enrichment_revision") or 1),
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
