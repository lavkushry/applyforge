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


def _score_profile_item(item: dict, keywords: list[str]) -> int:
    item_text = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("company", "")),
            str(item.get("name", "")),
            str(item.get("summary", "")),
            " ".join(str(entry) for entry in item.get("highlights", [])),
        ]
    ).lower()
    return sum(1 for keyword in keywords if keyword and keyword.lower() in item_text)


def _rank_profile_items(items: list[dict], keywords: list[str]) -> tuple[list[dict], list[int]]:
    indexed = list(enumerate(items))
    ranked = sorted(indexed, key=lambda indexed_item: (-_score_profile_item(indexed_item[1], keywords), indexed_item[0]))
    emphasized_indices = [index for index, item in ranked if _score_profile_item(item, keywords) > 0]
    return [item for _, item in ranked], emphasized_indices


def build_tailoring_diff(
    original_skills: list[str],
    ranked_skills: list[str],
    role: dict | None,
    *,
    matched_requirements: list[str],
    missing_requirements: list[str],
    emphasized_experience_indices: list[int],
    emphasized_project_indices: list[int],
    enrichment_revision: int,
) -> dict:
    role_keywords = role.get("keywords", []) if role else []
    return {
        "skills_reordered": original_skills != ranked_skills,
        "role_keywords": role_keywords,
        "focused_on_role": role.get("name") if role else "",
        "matched_requirements": matched_requirements,
        "missing_requirements": missing_requirements,
        "emphasized_experience_indices": emphasized_experience_indices,
        "emphasized_project_indices": emphasized_project_indices,
        "enrichment_revision": enrichment_revision,
    }


def tailor_resume(profile: dict, job: dict, role: dict | None = None) -> dict:
    normalized_description = job.get("normalized_description", {}) or {}
    ranked_skills = rank_skills_for_job(profile.get("skills", []), job.get("description", ""))
    keywords = list(
        dict.fromkeys(
            normalized_description.get("must_have_skills", [])
            + normalized_description.get("nice_to_have_skills", [])
            + (role.get("keywords", []) if role else [])
        )
    )
    ranked_experience, emphasized_experience_indices = _rank_profile_items(profile.get("experience", []), keywords)
    ranked_projects, emphasized_project_indices = _rank_profile_items(profile.get("projects", []), keywords)
    profile_skill_lookup = {skill.lower() for skill in profile.get("skills", [])}
    project_text = " ".join(
        " ".join(
            [
                str(item.get("name", "")),
                str(item.get("summary", "")),
                " ".join(str(entry) for entry in item.get("highlights", [])),
            ]
        )
        for item in profile.get("projects", [])
    ).lower()
    matched_requirements = [
        keyword
        for keyword in keywords
        if keyword.lower() in profile_skill_lookup or keyword.lower() in project_text
    ]
    missing_requirements = [
        keyword
        for keyword in normalized_description.get("nice_to_have_skills", [])
        if keyword.lower() not in profile_skill_lookup and keyword.lower() not in project_text
    ]
    original_summary = profile.get("summary", "").strip()
    role_name = (role or {}).get("name") or profile.get("basics", {}).get("target_role") or job.get("title", "this role")
    target_summary = (
        f"{original_summary} "
        f"Positioned for {role_name} work aligned with {job.get('title', 'this role')} at {job.get('company', 'the company')}."
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
        "experience": ranked_experience,
        "projects": ranked_projects,
        "education": list(profile.get("education", [])),
        "certifications": list(profile.get("certifications", [])),
        "links": list(profile.get("links", [])),
        "preferences": dict(profile.get("preferences", {})),
        "saved_answers": dict(profile.get("saved_answers", {})),
        "tailoring_notes": tailoring_notes,
        "diff_metadata": build_tailoring_diff(
            profile.get("skills", []),
            ranked_skills,
            role,
            matched_requirements=matched_requirements,
            missing_requirements=missing_requirements,
            emphasized_experience_indices=emphasized_experience_indices,
            emphasized_project_indices=emphasized_project_indices,
            enrichment_revision=int(job.get("enrichment_revision") or 1),
        ),
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
