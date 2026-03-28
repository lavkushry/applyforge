from pathlib import Path

from sqlalchemy.orm import Session

from app.api.routes import resume_templates as resume_template_routes
from app.cli.main import main as resume_cli_main
from app.services.resume_templates import (
    build_resume_markdown,
    list_resume_templates,
    load_resume_sections,
    profile_to_resume_content,
)


def test_list_resume_templates_exposes_markdown_and_latex_assets() -> None:
    templates = list_resume_templates()
    sections = load_resume_sections()

    assert any(template["key"] == "ats-markdown-starter" for template in templates)
    assert any(template["key"] == "ats-light-latex" for template in templates)
    assert any(section["key"] == "experience" for section in sections)
    assert any(section["key"] == "education" for section in sections)


def test_build_resume_markdown_renders_sections_from_profile(profile) -> None:
    content = profile_to_resume_content(profile)

    rendered = build_resume_markdown(content)

    assert "# Alex Builder" in rendered
    assert "## Summary" in rendered
    assert "## Skills" in rendered
    assert "## Experience" in rendered
    assert "Built workflow automation" in rendered


def test_resume_templates_render_uses_current_profile_when_content_not_supplied(
    db_session: Session, user, profile
) -> None:
    response = resume_template_routes.render_resume_template(
        resume_template_routes.ResumeTemplateRenderRequest(template_key="ats-markdown-starter"),
        user,
        db_session,
    )

    assert response.template.key == "ats-markdown-starter"
    assert "Alex Builder" in response.rendered_content
    assert any(section.key == "skills" for section in response.sections)


def test_resume_cli_lists_templates(capsys) -> None:
    exit_code = resume_cli_main(["list-templates"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "ats-markdown-starter" in captured.out
    assert "ats-light-latex" in captured.out


def test_resume_cli_renders_markdown_template_from_json(tmp_path: Path, capsys) -> None:
    source = tmp_path / "resume.json"
    source.write_text(
        """
        {
          "basics": {
            "full_name": "Alex Builder",
            "headline": "Staff Full-Stack Engineer",
            "email": "alex@example.com",
            "location": "Remote"
          },
          "summary": "Builds reliable hiring automation systems.",
          "skills": ["Python", "FastAPI"],
          "experience": [
            {
              "title": "Staff Engineer",
              "company": "Forge Labs",
              "highlights": ["Owned platform reliability"]
            }
          ],
          "projects": [],
          "education": [],
          "certifications": [],
          "links": []
        }
        """.strip(),
        encoding="utf-8",
    )

    exit_code = resume_cli_main(["render-template", "--input", str(source), "--template-key", "ats-markdown-starter"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Alex Builder" in captured.out
    assert "Owned platform reliability" in captured.out
