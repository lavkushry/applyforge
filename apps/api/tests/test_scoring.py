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


def test_score_job_uses_enrichment_requirements_and_revision_readiness() -> None:
    profile = {
        "basics": {"target_role": "Staff Platform Engineer", "preferred_locations": ["Remote"]},
        "skills": ["Python", "Kubernetes", "Docker", "FastAPI"],
        "summary": "Platform engineer shipping reliable internal tooling for AI teams.",
        "preferences": {"work_authorization": "Authorized"},
    }
    job = {
        "title": "Staff Platform Engineer",
        "location": "Remote, US",
        "description": "Own platform systems and developer experience.",
        "remote_type": "remote",
        "seniority": "staff",
        "salary": "$210k",
        "application_url": "https://careers.example.com/jobs/1",
        "enrichment_status": "completed",
        "enrichment_revision": 3,
        "normalized_description": {
            "must_have_skills": ["Python", "Kubernetes"],
            "nice_to_have_skills": ["Docker", "Terraform"],
            "extraction_confidence": 0.84,
            "visa_hints": ["no sponsorship required"],
        },
    }
    role = {
        "name": "Staff Platform Engineer",
        "aliases": ["Platform Engineer"],
        "keywords": ["platform", "developer experience"],
        "preferred_locations": ["remote"],
        "remote_preference": "remote",
        "salary_target": "$200k+",
        "visa_preference": "not_required",
        "seniority": "staff",
    }

    result = score_job(profile, job, role)

    assert result["enrichment_revision"] == 3
    assert result["score_breakdown"]["title_fit"] >= 18
    assert result["score_breakdown"]["must_have_fit"] >= 20
    assert result["score_breakdown"]["nice_to_have_fit"] >= 6
    assert result["score_breakdown"]["application_readiness"] >= 7
    assert result["recommendation"] in {"high priority", "maybe"}
