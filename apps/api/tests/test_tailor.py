from app.services.tailor import detect_risky_question, generate_application_answer, tailor_resume


def test_tailor_resume_reorders_but_does_not_invent_facts() -> None:
    profile = {
        "basics": {"full_name": "Alex Builder", "target_role": "Platform Engineer"},
        "summary": "Platform engineer focused on reliable developer systems.",
        "skills": ["Python", "Kubernetes", "TypeScript"],
        "experience": [{"company": "Forge Labs", "highlights": ["Built deployment tooling"]}],
        "projects": [],
        "education": [],
        "certifications": [],
        "links": [],
        "fact_locked": True,
    }
    job = {
        "title": "Senior Platform Engineer",
        "company": "Atlas",
        "description": "Looking for Kubernetes, Python, and platform automation experience.",
    }

    tailored = tailor_resume(profile, job)

    assert tailored["fact_locked"] is True
    assert tailored["skills"][:2] == ["Kubernetes", "Python"]
    assert "Atlas" in tailored["summary"]
    assert tailored["experience"] == profile["experience"]


def test_tailor_resume_emphasizes_matching_experience_and_reports_requirement_gaps() -> None:
    profile = {
        "basics": {"full_name": "Alex Builder", "target_role": "Platform Engineer"},
        "summary": "Platform engineer focused on reliable developer systems.",
        "skills": ["Python", "Kubernetes", "TypeScript"],
        "experience": [
            {"company": "Forge Labs", "title": "Platform Engineer", "highlights": ["Built deployment tooling with Kubernetes"]},
            {"company": "Atlas Data", "title": "Frontend Engineer", "highlights": ["Built React dashboards"]},
        ],
        "projects": [{"name": "InfraBot", "summary": "Automated Terraform drift reviews"}],
        "education": [],
        "certifications": [],
        "links": [],
        "fact_locked": True,
    }
    job = {
        "title": "Senior Platform Engineer",
        "company": "Atlas",
        "description": "Looking for Kubernetes, Python, Terraform, and platform automation experience.",
        "normalized_description": {
            "must_have_skills": ["Kubernetes", "Python", "Terraform"],
            "nice_to_have_skills": ["AWS"],
        },
        "enrichment_revision": 2,
    }

    tailored = tailor_resume(profile, job)

    assert tailored["experience"][0]["company"] == "Forge Labs"
    assert tailored["projects"][0]["name"] == "InfraBot"
    assert tailored["diff_metadata"]["matched_requirements"] == ["Kubernetes", "Python", "Terraform"]
    assert tailored["diff_metadata"]["missing_requirements"] == ["AWS"]
    assert tailored["diff_metadata"]["enrichment_revision"] == 2


def test_generate_application_answer_marks_unknowns_for_review() -> None:
    profile = {
        "basics": {"full_name": "Alex Builder"},
        "settings": {},
        "links": [],
    }

    answer = generate_application_answer("What is your current salary?", profile)

    assert answer["value"] == "Requires candidate review"
    assert answer["confidence"] == "low"
    assert answer["requires_review"] is True


def test_detect_risky_question_flags_sensitive_prompts() -> None:
    result = detect_risky_question("What is your expected salary and current visa status?")

    assert result["risk_level"] == "high"
    assert result["requires_approval"] is True
