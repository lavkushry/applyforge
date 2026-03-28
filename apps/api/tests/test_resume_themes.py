from app.models.entities import ResumeTheme
from app.services.resume_themes import build_preview_blocks, build_rendercv_payload


def test_build_rendercv_payload_preserves_structured_resume_content() -> None:
    theme = ResumeTheme(
        slug="classic-ats-light",
        label="Classic ATS Light",
        description="",
        accent_color="#0f172a",
        layout_mode="single-column",
        is_ats_safe=True,
        metadata_json={},
        active=True,
    )
    content = {
        "basics": {"full_name": "Alex Builder", "email": "alex@example.com"},
        "summary": "Staff-level engineer building AI systems.",
        "skills": ["Python", "FastAPI"],
        "experience": [{"title": "Staff Engineer", "company": "Forge Labs"}],
        "projects": [],
        "education": [],
        "certifications": [],
        "links": [],
    }

    payload = build_rendercv_payload(content, theme)

    assert payload["cv"]["name"] == "Alex Builder"
    assert payload["cv"]["sections"]["skills"] == ["Python", "FastAPI"]
    assert payload["theme"]["slug"] == "classic-ats-light"


def test_build_preview_blocks_returns_header_summary_and_skills() -> None:
    blocks = build_preview_blocks(
        {
            "basics": {"full_name": "Alex Builder", "headline": "Staff Engineer"},
            "summary": "Builds reliable hiring automation.",
            "skills": ["Python", "React"],
            "experience": [{"title": "Staff Engineer", "company": "Forge Labs"}],
        }
    )

    assert blocks[0]["title"] == "Header"
    assert "Alex Builder" in blocks[0]["lines"]
    assert blocks[1]["title"] == "Summary"
    assert "Python, React" in blocks[2]["lines"][0]
