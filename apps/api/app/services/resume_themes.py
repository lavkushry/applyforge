from copy import deepcopy

from sqlalchemy.orm import Session

from app.models.entities import ResumeTheme

DEFAULT_RESUME_THEMES = [
    {
        "slug": "classic-ats-light",
        "label": "Classic ATS Light",
        "description": "Single-column, high-contrast, highly extractable layout for ATS pipelines.",
        "accent_color": "#0f172a",
        "layout_mode": "single-column",
        "is_ats_safe": True,
        "metadata_json": {"heading_case": "uppercase", "density": "comfortable"},
    },
    {
        "slug": "modern-minimal-light",
        "label": "Modern Minimal Light",
        "description": "Lightweight modern layout with subtle accents and ATS-safe section rhythm.",
        "accent_color": "#1d4ed8",
        "layout_mode": "single-column",
        "is_ats_safe": True,
        "metadata_json": {"heading_case": "title", "density": "balanced"},
    },
    {
        "slug": "compact-technical-light",
        "label": "Compact Technical Light",
        "description": "Space-efficient technical resume layout for engineering-heavy profiles.",
        "accent_color": "#0f766e",
        "layout_mode": "single-column",
        "is_ats_safe": True,
        "metadata_json": {"heading_case": "uppercase", "density": "compact"},
    },
]

RENDERCV_THEME_MAP = {
    "classic-ats-light": "classic",
    "modern-minimal-light": "moderncv",
    "compact-technical-light": "engineeringclassic",
}


def seed_resume_themes(db: Session) -> None:
    for theme in DEFAULT_RESUME_THEMES:
        existing = db.query(ResumeTheme).filter(ResumeTheme.slug == theme["slug"]).first()
        if existing:
            existing.label = theme["label"]
            existing.description = theme["description"]
            existing.accent_color = theme["accent_color"]
            existing.layout_mode = theme["layout_mode"]
            existing.is_ats_safe = theme["is_ats_safe"]
            existing.metadata_json = theme["metadata_json"]
            existing.active = True
        else:
            db.add(ResumeTheme(**theme))
    db.commit()


def get_theme_by_id(db: Session, theme_id: int | None) -> ResumeTheme:
    if theme_id:
        theme = db.query(ResumeTheme).filter(ResumeTheme.id == theme_id, ResumeTheme.active.is_(True)).first()
        if theme:
            return theme
    theme = db.query(ResumeTheme).filter(ResumeTheme.slug == "classic-ats-light").first()
    if theme:
        return theme
    seed_resume_themes(db)
    return db.query(ResumeTheme).filter(ResumeTheme.slug == "classic-ats-light").first()


def build_rendercv_payload(content: dict, theme: ResumeTheme) -> dict:
    basics = content.get("basics", {})
    return {
        "cv": {
            "name": basics.get("full_name", "Candidate"),
            "location": basics.get("location", ""),
            "email": basics.get("email", ""),
            "phone": basics.get("phone", ""),
            "summary": content.get("summary", ""),
            "sections": {
                "skills": deepcopy(content.get("skills", [])),
                "experience": deepcopy(content.get("experience", [])),
                "projects": deepcopy(content.get("projects", [])),
                "education": deepcopy(content.get("education", [])),
                "certifications": deepcopy(content.get("certifications", [])),
                "links": deepcopy(content.get("links", [])),
            },
        },
        "theme": {
            "slug": theme.slug,
            "label": theme.label,
            "layout_mode": theme.layout_mode,
            "accent_color": theme.accent_color,
            "ats_safe": theme.is_ats_safe,
        },
    }


def _rendercv_social_links(links: list[dict]) -> tuple[list[dict], str | None]:
    socials: list[dict] = []
    website: str | None = None
    for link in links:
        label = str(link.get("label", "")).strip().lower()
        url = str(link.get("url", "")).strip()
        if not url:
            continue
        if label == "linkedin":
            username = url.rstrip("/").split("/")[-1]
            socials.append({"network": "LinkedIn", "username": username})
        elif label == "github":
            username = url.rstrip("/").split("/")[-1]
            socials.append({"network": "GitHub", "username": username})
        elif website is None:
            website = url
    return socials, website


def build_rendercv_input(content: dict, theme: ResumeTheme) -> dict:
    basics = content.get("basics", {})
    experience = [
        {
            "company": item.get("company", ""),
            "position": item.get("title", ""),
            "date": " - ".join(
                [part for part in [item.get("start_date", ""), item.get("end_date", "")] if part]
            ),
            "location": item.get("location", ""),
            "summary": item.get("summary", ""),
            "highlights": item.get("highlights", []),
        }
        for item in content.get("experience", [])
    ]
    education = [
        {
            "institution": item.get("institution", ""),
            "area": item.get("area", ""),
            "degree": item.get("degree", ""),
            "date": item.get("date", ""),
            "location": item.get("location", ""),
            "highlights": item.get("highlights", []),
        }
        for item in content.get("education", [])
    ]
    projects = [
        {
            "name": item.get("name", ""),
            "summary": item.get("summary", ""),
            "date": item.get("date", ""),
            "highlights": item.get("highlights", []),
        }
        for item in content.get("projects", [])
    ]
    skills = [{"label": "Core Skills", "details": ", ".join(content.get("skills", []))}] if content.get("skills") else []
    certifications = [{"bullet": cert.get("name", "")} for cert in content.get("certifications", []) if cert.get("name")]
    socials, website = _rendercv_social_links(content.get("links", []))
    return {
        "cv": {
            "name": basics.get("full_name", "Candidate"),
            "location": basics.get("location", ""),
            "email": basics.get("email", ""),
            "phone": basics.get("phone", ""),
            "website": website,
            "social_networks": socials,
            "sections": {
                "summary": [content.get("summary", "")] if content.get("summary") else [],
                "experience": experience,
                "projects": projects,
                "education": education,
                "skills": skills,
                "certifications": certifications,
            },
        },
        "design": {"theme": RENDERCV_THEME_MAP.get(theme.slug, "classic")},
    }


def build_preview_blocks(content: dict) -> list[dict]:
    basics = content.get("basics", {})
    blocks = [
        {"title": "Header", "lines": [basics.get("full_name", "Candidate"), basics.get("headline", "")]},
        {"title": "Summary", "lines": [content.get("summary", "")]},
        {"title": "Skills", "lines": [", ".join(content.get("skills", []))]},
        {
            "title": "Experience",
            "lines": [
                f"{item.get('title', '')} at {item.get('company', '')}".strip()
                for item in content.get("experience", [])
            ]
            or ["No experience entries yet."],
        },
    ]
    return blocks
