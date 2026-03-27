from app.services.resume_parser import parse_resume_text


def test_parse_resume_text_extracts_structured_sections() -> None:
    content = """
    Alex Builder
    alex@example.com | Bengaluru, India | https://github.com/alex

    SUMMARY
    Full-stack engineer building AI-assisted products.

    SKILLS
    Python, FastAPI, TypeScript, React, Docker

    EXPERIENCE
    Senior Engineer at Forge Labs
    Built job automation systems with FastAPI and React.

    EDUCATION
    B.Tech Computer Science
    """

    parsed = parse_resume_text(content)

    assert parsed["basics"]["full_name"] == "Alex Builder"
    assert "Python" in parsed["skills"]
    assert parsed["summary"].startswith("Full-stack engineer")
    assert parsed["experience"]
    assert parsed["education"]
    assert parsed["fact_locked"] is True
