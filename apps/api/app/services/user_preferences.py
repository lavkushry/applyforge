from sqlalchemy.orm import Session

from app.models.entities import CandidateProfile, Setting, TargetRole
from app.services.runtime_utils import compact_list, compact_mapping, dedupe_preserve_order


def _get_profile(db: Session, user_id: int) -> CandidateProfile | None:
    return db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()


def _get_settings(db: Session, user_id: int) -> dict[str, dict]:
    rows = db.query(Setting).filter(Setting.user_id == user_id).all()
    return {row.key: row.value for row in rows}


def _get_roles(db: Session, user_id: int) -> list[TargetRole]:
    return (
        db.query(TargetRole)
        .filter(TargetRole.user_id == user_id, TargetRole.active.is_(True))
        .order_by(TargetRole.updated_at.desc(), TargetRole.id.desc())
        .all()
    )


def build_user_preferences_snapshot(db: Session, user_id: int) -> dict:
    profile = _get_profile(db, user_id)
    settings = _get_settings(db, user_id)
    roles = _get_roles(db, user_id)

    basics = profile.basics if profile else {}
    preferences = profile.preferences if profile else {}
    saved_answers = profile.saved_answers if profile else {}
    links = profile.links if profile else []

    company_include = dedupe_preserve_order(
        company for role in roles for company in role.companies_include
    )
    company_exclude = dedupe_preserve_order(
        company for role in roles for company in role.companies_exclude
    )

    return {
        "candidate": {
            "full_name": basics.get("full_name", ""),
            "headline": basics.get("headline", ""),
            "email": basics.get("email", ""),
            "phone": basics.get("phone", ""),
            "location": basics.get("location", ""),
            "target_role": basics.get("target_role", ""),
            "preferred_locations": list(basics.get("preferred_locations", []) or []),
            "summary": profile.summary if profile else "",
            "skills": list(profile.skills if profile else []),
            "links": list(links),
        },
        "automation": {
            "mode": settings.get("automation_preferences", {}).get("mode", "assisted"),
            "pause_on_risk": bool(settings.get("automation_preferences", {}).get("pause_on_risk", True)),
        },
        "job_filters": {
            "keyword_focus": list(settings.get("job_filters", {}).get("keyword_focus", []) or []),
        },
        "resume": {
            "default_theme": settings.get("resume_preferences", {}).get("default_theme", "classic-ats-light"),
            "ats_mode": bool(settings.get("resume_preferences", {}).get("ats_mode", True)),
        },
        "work_preferences": compact_mapping(
            {
                "work_authorization": preferences.get("work_authorization"),
                "salary_expectation": saved_answers.get("salary_expectation"),
                "notice_period": saved_answers.get("notice_period"),
            }
        ),
        "saved_answers": compact_mapping(saved_answers),
        "company_preferences": {
            "include": company_include,
            "exclude": company_exclude,
        },
        "target_roles": [
            {
                "name": role.name,
                "aliases": list(role.aliases or []),
                "keywords": list(role.keywords or []),
                "preferred_locations": list(role.preferred_locations or []),
                "remote_preference": role.remote_preference,
                "salary_target": role.salary_target,
                "visa_preference": role.visa_preference,
                "seniority": role.seniority,
                "automation_enabled": role.automation_enabled,
                "min_auto_apply_score": role.min_auto_apply_score,
            }
            for role in roles
        ],
    }


def render_user_preferences_text(snapshot: dict) -> str:
    candidate = snapshot.get("candidate", {})
    automation = snapshot.get("automation", {})
    job_filters = snapshot.get("job_filters", {})
    resume = snapshot.get("resume", {})
    work_preferences = snapshot.get("work_preferences", {})
    company_preferences = snapshot.get("company_preferences", {})
    target_roles = snapshot.get("target_roles", [])
    saved_answers = snapshot.get("saved_answers", {})

    lines = [
        "# ApplyForge User Preferences",
        "",
        "## Candidate",
        f"Candidate: {candidate.get('full_name', '') or 'Unknown candidate'}",
        f"Headline: {candidate.get('headline', '') or 'Not set'}",
        f"Email: {candidate.get('email', '') or 'Not set'}",
        f"Phone: {candidate.get('phone', '') or 'Not set'}",
        f"Location: {candidate.get('location', '') or 'Not set'}",
        f"Target role: {candidate.get('target_role', '') or 'Not set'}",
        f"Preferred locations: {', '.join(candidate.get('preferred_locations', [])) or 'Not set'}",
        "",
        "## Automation",
        f"Default apply mode: {automation.get('mode', 'assisted')}",
        f"Pause on risk: {'yes' if automation.get('pause_on_risk', True) else 'no'}",
        f"Keyword focus: {', '.join(job_filters.get('keyword_focus', [])) or 'Not set'}",
        "",
        "## Resume",
        f"Default theme: {resume.get('default_theme', 'classic-ats-light')}",
        f"ATS mode: {'enabled' if resume.get('ats_mode', True) else 'disabled'}",
        "",
        "## Work Preferences",
    ]

    for key, value in work_preferences.items():
        lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    if not work_preferences:
        lines.append("- None recorded")

    lines.extend(["", "## Company Preferences"])
    lines.append(f"- Prioritize: {', '.join(company_preferences.get('include', [])) or 'None'}")
    lines.append(f"- Avoid: {', '.join(company_preferences.get('exclude', [])) or 'None'}")

    lines.extend(["", "## Target Roles"])
    if target_roles:
        for role in target_roles:
            lines.append(
                f"- {role['name']} | seniority={role['seniority']} | remote={role['remote_preference']} | auto={'yes' if role['automation_enabled'] else 'no'} | min_auto_apply_score={role['min_auto_apply_score']:.0f}"
            )
    else:
        lines.append("- No active target roles")

    lines.extend(["", "## Saved answers"])
    if saved_answers:
        for key, value in saved_answers.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- None recorded")

    candidate_links = compact_list(
        f"{link.get('label', '')}: {link.get('url', '')}"
        for link in candidate.get("links", [])
    )
    lines.extend(["", "## Links"])
    if candidate_links:
        lines.extend(f"- {link}" for link in candidate_links)
    else:
        lines.append("- None recorded")

    return "\n".join(lines)
