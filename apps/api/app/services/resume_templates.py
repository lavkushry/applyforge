import json
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.models.entities import CandidateProfile

RESUME_TEMPLATE_CATALOG = [
    {
        "key": "ats-markdown-starter",
        "label": "ATS Markdown Starter",
        "description": "Structured markdown resume source with ATS-safe section ordering for editing and export pipelines.",
        "format": "markdown",
        "asset_name": "resume_template.md",
        "recommended_theme_slugs": [
            "classic-ats-light",
            "modern-minimal-light",
            "compact-technical-light",
        ],
        "section_keys": [
            "header",
            "summary",
            "skills",
            "experience",
            "projects",
            "education",
            "certifications",
            "links",
        ],
    },
    {
        "key": "ats-light-latex",
        "label": "ATS Light LaTeX",
        "description": "Light single-column LaTeX source template for highly readable, extractable resume generation.",
        "format": "latex",
        "asset_name": "resume_template.tex",
        "recommended_theme_slugs": [
            "classic-ats-light",
            "modern-minimal-light",
        ],
        "section_keys": [
            "header",
            "summary",
            "skills",
            "experience",
            "projects",
            "education",
            "certifications",
            "links",
        ],
    },
]


def _resume_assets_root() -> Path:
    return settings.resolved_config_root / "resume"


def list_resume_templates() -> list[dict[str, Any]]:
    return [dict(template) for template in RESUME_TEMPLATE_CATALOG]


def get_resume_template(template_key: str) -> dict[str, Any]:
    for template in RESUME_TEMPLATE_CATALOG:
        if template["key"] == template_key:
            return dict(template)
    raise KeyError(f"Unknown resume template: {template_key}")


def load_resume_sections() -> list[dict[str, Any]]:
    path = _resume_assets_root() / "sections.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_resume_template_asset(template_key: str) -> str:
    template = get_resume_template(template_key)
    path = _resume_assets_root() / template["asset_name"]
    return path.read_text(encoding="utf-8")


def profile_to_resume_content(profile: CandidateProfile) -> dict[str, Any]:
    return {
        "basics": dict(profile.basics or {}),
        "summary": profile.summary,
        "skills": list(profile.skills or []),
        "experience": list(profile.experience or []),
        "projects": list(profile.projects or []),
        "education": list(profile.education or []),
        "certifications": list(profile.certifications or []),
        "links": list(profile.links or []),
    }


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _join_non_empty(parts: list[str], separator: str = " | ") -> str:
    return separator.join(part for part in parts if part)


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    escaped = value
    for original, replacement in replacements.items():
        escaped = escaped.replace(original, replacement)
    return escaped


def _render_header_lines(content: dict[str, Any]) -> tuple[str, str, str, str]:
    basics = content.get("basics", {})
    full_name = _clean_text(basics.get("full_name")) or "Candidate"
    headline = _clean_text(basics.get("headline"))
    contact_line = _join_non_empty(
        [
            _clean_text(basics.get("email")),
            _clean_text(basics.get("phone")),
            _clean_text(basics.get("location")),
        ]
    )
    links = content.get("links", [])
    links_inline = " | ".join(
        _join_non_empty([_clean_text(link.get("label")), _clean_text(link.get("url"))], ": ")
        for link in links
        if _clean_text(link.get("url"))
    )
    return full_name, headline, contact_line, links_inline


def _markdown_block_lines(items: list[dict[str, Any]], title_keys: tuple[str, ...], fallback: str) -> str:
    if not items:
        return fallback
    blocks: list[str] = []
    for item in items:
        heading = " - ".join(_clean_text(item.get(key)) for key in title_keys if _clean_text(item.get(key)))
        if heading:
            blocks.append(f"### {heading}")
        meta = _join_non_empty(
            [
                _clean_text(item.get("start_date")),
                _clean_text(item.get("end_date")),
                _clean_text(item.get("location")),
                _clean_text(item.get("date")),
            ]
        )
        if meta:
            blocks.append(meta)
        summary = _clean_text(item.get("summary"))
        if summary:
            blocks.append(summary)
        for highlight in item.get("highlights", []):
            highlight_text = _clean_text(highlight)
            if highlight_text:
                blocks.append(f"- {highlight_text}")
        blocks.append("")
    return "\n".join(blocks).strip() or fallback


def _latex_entry_blocks(items: list[dict[str, Any]], title_keys: tuple[str, ...], fallback: str) -> str:
    if not items:
        return fallback
    blocks: list[str] = []
    for item in items:
        heading = " - ".join(_clean_text(item.get(key)) for key in title_keys if _clean_text(item.get(key)))
        if heading:
            blocks.append(f"\\textbf{{{_latex_escape(heading)}}}\\\\")
        meta = _join_non_empty(
            [
                _clean_text(item.get("start_date")),
                _clean_text(item.get("end_date")),
                _clean_text(item.get("location")),
                _clean_text(item.get("date")),
            ]
        )
        if meta:
            blocks.append(f"{_latex_escape(meta)}\\\\")
        summary = _clean_text(item.get("summary"))
        if summary:
            blocks.append(f"{_latex_escape(summary)}\\\\")
        highlights = [f"\\item {_latex_escape(_clean_text(highlight))}" for highlight in item.get("highlights", []) if _clean_text(highlight)]
        if highlights:
            blocks.append("\\begin{itemize}")
            blocks.extend(highlights)
            blocks.append("\\end{itemize}")
        blocks.append("")
    return "\n".join(blocks).strip() or fallback


def build_resume_markdown(content: dict[str, Any]) -> str:
    return render_resume_template(content, "ats-markdown-starter")


def build_resume_latex(content: dict[str, Any]) -> str:
    return render_resume_template(content, "ats-light-latex")


def render_resume_template(content: dict[str, Any], template_key: str) -> str:
    template = get_resume_template(template_key)
    asset = load_resume_template_asset(template_key)
    full_name, headline, contact_line, links_inline = _render_header_lines(content)
    skills = ", ".join(_clean_text(skill) for skill in content.get("skills", []) if _clean_text(skill)) or "No skills added yet."
    projects_markdown = _markdown_block_lines(
        content.get("projects", []),
        ("name",),
        "No projects added yet.",
    )
    experience_markdown = _markdown_block_lines(
        content.get("experience", []),
        ("title", "company"),
        "No experience entries yet.",
    )
    education_markdown = _markdown_block_lines(
        content.get("education", []),
        ("degree", "institution"),
        "No education entries yet.",
    )
    certifications_markdown = "\n".join(
        f"- {_clean_text(certification.get('name'))}"
        for certification in content.get("certifications", [])
        if _clean_text(certification.get("name"))
    ) or "No certifications added yet."
    links_markdown = "\n".join(
        f"- {_join_non_empty([_clean_text(link.get('label')), _clean_text(link.get('url'))], ': ')}"
        for link in content.get("links", [])
        if _clean_text(link.get("url"))
    ) or "No links added yet."

    replacements = {
        "full_name": full_name,
        "headline": headline or "Professional headline pending review",
        "contact_line": contact_line or "Contact details pending review",
        "links_inline": links_inline or "Add LinkedIn, GitHub, and portfolio links here.",
        "summary": _clean_text(content.get("summary")) or "Add a concise role-targeted summary here.",
        "skills_markdown": skills,
        "experience_markdown": experience_markdown,
        "projects_markdown": projects_markdown,
        "education_markdown": education_markdown,
        "certifications_markdown": certifications_markdown,
        "links_markdown": links_markdown,
        "summary_latex": _latex_escape(_clean_text(content.get("summary")) or "Add a concise role-targeted summary here."),
        "skills_latex": _latex_escape(skills),
        "experience_latex": _latex_entry_blocks(
            content.get("experience", []),
            ("title", "company"),
            "No experience entries yet.",
        ),
        "projects_latex": _latex_entry_blocks(
            content.get("projects", []),
            ("name",),
            "No projects added yet.",
        ),
        "education_latex": _latex_entry_blocks(
            content.get("education", []),
            ("degree", "institution"),
            "No education entries yet.",
        ),
        "certifications_latex": "\\begin{itemize}\n"
        + "\n".join(
            f"\\item {_latex_escape(_clean_text(certification.get('name')))}"
            for certification in content.get("certifications", [])
            if _clean_text(certification.get("name"))
        )
        + "\n\\end{itemize}"
        if any(_clean_text(certification.get("name")) for certification in content.get("certifications", []))
        else "No certifications added yet.",
        "links_latex": "\\\\\n".join(
            _latex_escape(_join_non_empty([_clean_text(link.get("label")), _clean_text(link.get("url"))], ": "))
            for link in content.get("links", [])
            if _clean_text(link.get("url"))
        )
        or "No links added yet.",
    }

    if template["format"] == "latex":
        replacements["full_name"] = _latex_escape(full_name)
        replacements["headline"] = _latex_escape(headline or "Professional headline pending review")
        replacements["contact_line"] = _latex_escape(contact_line or "Contact details pending review")
        replacements["links_inline"] = _latex_escape(links_inline or "Add LinkedIn, GitHub, and portfolio links here.")

    rendered = asset
    for key, value in replacements.items():
        rendered = rendered.replace(f"[[{key}]]", value)
    return rendered
