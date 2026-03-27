from typing import Any


COMMON_QUESTION_RULES = {
    "work authorization": lambda profile: profile.get("saved_answers", {}).get("work_authorization")
    or profile.get("preferences", {}).get("work_authorization")
    or "Requires candidate review",
    "years of experience": lambda profile: profile.get("saved_answers", {}).get("years_of_experience")
    or "Requires candidate review",
    "notice period": lambda profile: profile.get("saved_answers", {}).get("notice_period")
    or "Requires candidate review",
    "relocation": lambda profile: profile.get("saved_answers", {}).get("relocation")
    or "Requires candidate review",
    "salary": lambda profile: profile.get("saved_answers", {}).get("salary_expectation") or "Requires candidate review",
    "linkedin": lambda profile: next(
        (link.get("url") for link in profile.get("links", []) if link.get("label", "").lower() == "linkedin"),
        "Requires candidate review",
    ),
    "github": lambda profile: next(
        (link.get("url") for link in profile.get("links", []) if link.get("label", "").lower() == "github"),
        "Requires candidate review",
    ),
    "portfolio": lambda profile: next(
        (link.get("url") for link in profile.get("links", []) if link.get("label", "").lower() == "portfolio"),
        "Requires candidate review",
    ),
}

HIGH_RISK_KEYWORDS = {"salary", "compensation", "visa", "sponsorship", "disability", "gender", "ethnicity", "age"}


def rank_skills_for_job(skills: list[str], description: str) -> list[str]:
    lowered = description.lower()
    return sorted(skills, key=lambda skill: (0 if skill.lower() in lowered else 1, skill.lower()))


def tailor_resume(profile: dict, job: dict) -> dict:
    ranked_skills = rank_skills_for_job(profile.get("skills", []), job.get("description", ""))
    target_summary = (
        f"{profile.get('summary', '').strip()} "
        f"Positioned for {job.get('title', 'this role')} at {job.get('company', 'the company')}."
    ).strip()
    tailoring_notes = [
        "Reordered skills to emphasize job-relevant capabilities.",
        "Preserved experience bullets without inventing facts.",
        "Kept fact-locked profile sections intact.",
    ]

    return {
        "basics": dict(profile.get("basics", {})),
        "summary": target_summary,
        "skills": ranked_skills,
        "experience": list(profile.get("experience", [])),
        "projects": list(profile.get("projects", [])),
        "education": list(profile.get("education", [])),
        "certifications": list(profile.get("certifications", [])),
        "links": list(profile.get("links", [])),
        "preferences": dict(profile.get("preferences", {})),
        "saved_answers": dict(profile.get("saved_answers", {})),
        "tailoring_notes": tailoring_notes,
        "fact_locked": True,
    }


def generate_cover_letter(profile: dict, job: dict) -> str:
    top_skills = ", ".join(rank_skills_for_job(profile.get("skills", []), job.get("description", ""))[:3])
    return (
        f"Dear Hiring Team at {job.get('company', 'the company')},\n\n"
        f"I am applying for the {job.get('title', 'role')} opportunity. "
        f"My experience building production systems with {top_skills} maps closely to the needs described in the role.\n\n"
        f"In previous work I focused on {profile.get('summary', 'shipping reliable software')}. "
        "I would welcome the opportunity to bring that same execution focus to your team.\n\n"
        "Thank you for your time and consideration.\n\n"
        f"Sincerely,\n{profile.get('basics', {}).get('full_name', 'Candidate')}"
    )


def detect_risky_question(question: str) -> dict[str, Any]:
    lowered = question.lower()
    matched = sorted(keyword for keyword in HIGH_RISK_KEYWORDS if keyword in lowered)
    risk_level = "high" if matched else "low"
    return {
        "risk_level": risk_level,
        "matched_keywords": matched,
        "requires_approval": bool(matched),
    }


def generate_application_answer(question: str, profile: dict) -> dict[str, Any]:
    lowered = question.lower()
    for keyword, resolver in COMMON_QUESTION_RULES.items():
        if keyword in lowered:
            value = resolver(profile)
            requires_review = value == "Requires candidate review"
            return {
                "value": value,
                "confidence": "high" if not requires_review else "low",
                "requires_review": requires_review,
            }
    return {
        "value": "Requires candidate review",
        "confidence": "low",
        "requires_review": True,
    }
