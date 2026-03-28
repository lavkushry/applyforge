from app.services.scoring import score_job


def test_score_job_returns_priority_and_explanations() -> None:
    profile = {
        "basics": {"target_role": "Senior Full Stack Engineer", "preferred_locations": ["Remote"]},
        "skills": ["Python", "FastAPI", "React", "TypeScript", "Docker"],
        "summary": "Engineer shipping AI workflow systems.",
        "links": [],
    }
    job = {
        "title": "Senior Full Stack Engineer",
        "location": "Remote, US",
        "description": (
            "We need a senior full stack engineer with Python, FastAPI, React, "
            "TypeScript, Docker, and cloud systems experience."
        ),
        "remote_type": "remote",
        "seniority": "senior",
    }

    result = score_job(profile, job)

    assert result["overall_score"] >= 80
    assert result["recommendation"] == "high priority"
    assert "Python" in result["strengths"]
    assert result["reasons"]
    assert "cloud systems" in " ".join(result["missing_skills"]).lower()


def test_score_job_uses_role_strategy_preferences_when_present() -> None:
    profile = {
        "basics": {"target_role": "Engineer", "preferred_locations": ["Remote"]},
        "skills": ["Python", "FastAPI", "React"],
        "summary": "Engineer shipping AI workflow systems.",
        "preferences": {},
    }
    job = {
        "title": "Founding AI Engineer",
        "location": "Remote, India",
        "description": "Need Python, FastAPI, React, and AI systems experience.",
        "remote_type": "remote",
        "seniority": "senior",
        "salary": "$160k",
        "tags": ["ai"],
    }
    role = {
        "name": "Founding AI Engineer",
        "aliases": ["AI Engineer"],
        "keywords": ["founding", "ai"],
        "preferred_locations": ["india"],
        "remote_preference": "remote",
        "salary_target": "$150k+",
        "visa_preference": "unknown",
        "seniority": "senior",
    }

    result = score_job(profile, job, role)

    assert result["score_breakdown"]["role_match"] >= 20
    assert result["score_breakdown"]["location_match"] >= 10
    assert result["score_breakdown"]["compensation_fit"] >= 6
