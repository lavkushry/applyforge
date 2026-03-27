CANONICAL_SKILLS = {
    "Python": ("python",),
    "FastAPI": ("fastapi",),
    "React": ("react",),
    "TypeScript": ("typescript",),
    "SQL": ("sql", "postgres", "postgresql"),
    "Docker": ("docker", "container"),
    "Kubernetes": ("kubernetes", "k8s"),
    "Cloud Systems": ("aws", "gcp", "azure", "cloud"),
}


def extract_job_skills(job_text: str) -> list[str]:
    lowered = job_text.lower()
    return [skill for skill, variants in CANONICAL_SKILLS.items() if any(keyword in lowered for keyword in variants)]


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def score_job(candidate: dict, job: dict) -> dict:
    job_text = " ".join(
        [
            job.get("title", ""),
            job.get("description", ""),
            job.get("location", ""),
            " ".join(job.get("tags", [])),
        ]
    )
    required_skills = extract_job_skills(job_text)
    candidate_skills = list(dict.fromkeys(candidate.get("skills", [])))
    candidate_skill_lookup = {skill.lower(): skill for skill in candidate_skills}
    strengths = [skill for skill in required_skills if skill.lower() in candidate_skill_lookup]
    missing_skills = [skill for skill in required_skills if skill.lower() not in candidate_skill_lookup]

    target_role = candidate.get("basics", {}).get("target_role", "").lower()
    title = job.get("title", "").lower()
    role_match = 20 if target_role and target_role in title else 12 if any(token in title for token in target_role.split()) else 6
    skills_match = min(30, len(strengths) * 7.5)
    must_have_penalty = min(18, len(missing_skills) * 6)

    candidate_locations = [item.lower() for item in candidate.get("basics", {}).get("preferred_locations", [])]
    location_match = 10 if "remote" in job.get("location", "").lower() or "remote" == job.get("remote_type", "").lower() else 6
    if candidate_locations and any(location in job.get("location", "").lower() for location in candidate_locations):
        location_match = 10

    seniority = job.get("seniority", "").lower()
    seniority_match = 10 if not seniority or seniority in {"senior", "lead"} else 7

    domain_match = 10 if "ai" in job_text.lower() and "ai" in candidate.get("summary", "").lower() else 6
    bonus_match = 5 if "visa" in job_text.lower() and candidate.get("preferences", {}).get("visa_required") is False else 3

    raw_score = role_match + skills_match + location_match + seniority_match + domain_match + bonus_match - must_have_penalty
    overall_score = clamp_score(raw_score + 28)
    recommendation = "high priority" if overall_score >= 75 else "maybe" if overall_score >= 55 else "skip"

    reasons = [
        f"Role alignment contributed {role_match:.0f} points based on target role matching.",
        f"Skills overlap contributed {skills_match:.0f} points across {len(strengths)} matching capabilities.",
        f"Location and remote preferences contributed {location_match:.0f} points.",
    ]
    if missing_skills:
        reasons.append(f"Missing must-have skills reduced the score: {', '.join(missing_skills)}.")

    return {
        "overall_score": float(overall_score),
        "score_breakdown": {
            "role_match": role_match,
            "skills_match": skills_match,
            "seniority_alignment": seniority_match,
            "domain_relevance": domain_match,
            "location_match": location_match,
            "bonus_qualifications": bonus_match,
            "must_have_penalty": must_have_penalty,
        },
        "missing_skills": missing_skills,
        "strengths": strengths,
        "reasons": reasons,
        "recommendation": recommendation,
    }
