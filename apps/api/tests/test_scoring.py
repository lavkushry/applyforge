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
