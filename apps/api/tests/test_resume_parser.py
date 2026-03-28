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


def test_parse_resume_text_extracts_ats_style_header_and_links() -> None:
    content = """
    Alex Builder
    Staff Full-Stack Engineer
    Bengaluru, India | +91 98765 43210 | alex@example.com | https://linkedin.com/in/alexbuilder | https://github.com/alexbuilder

    SUMMARY
    Builder of hiring automation and developer platforms.

    SKILLS
    Python | FastAPI | TypeScript | React | PostgreSQL
    """

    parsed = parse_resume_text(content)

    assert parsed["basics"]["full_name"] == "Alex Builder"
    assert parsed["basics"]["headline"] == "Staff Full-Stack Engineer"
    assert parsed["basics"]["email"] == "alex@example.com"
    assert parsed["basics"]["phone"] == "+91 98765 43210"
    assert parsed["basics"]["location"] == "Bengaluru, India"
    assert {link["label"] for link in parsed["links"]} >= {"linkedin", "github"}


def test_parse_resume_text_extracts_experience_entries_with_dates_and_highlights() -> None:
    content = """
    Alex Builder
    alex@example.com

    EXPERIENCE
    Senior Software Engineer | Forge Labs | Jan 2022 - Present | Remote
    - Led ApplyForge automation systems
    - Improved ATS-safe resume exports

    Software Engineer, Orbit Systems
    Mar 2020 - Dec 2021
    - Built internal workflow tooling
    """

    parsed = parse_resume_text(content)

    assert parsed["experience"][0]["title"] == "Senior Software Engineer"
    assert parsed["experience"][0]["company"] == "Forge Labs"
    assert parsed["experience"][0]["start_date"] == "Jan 2022"
    assert parsed["experience"][0]["end_date"] == "Present"
    assert "Led ApplyForge automation systems" in parsed["experience"][0]["highlights"]
    assert parsed["experience"][1]["title"] == "Software Engineer"
    assert parsed["experience"][1]["company"] == "Orbit Systems"
    assert parsed["experience"][1]["start_date"] == "Mar 2020"
    assert parsed["experience"][1]["end_date"] == "Dec 2021"


def test_parse_resume_text_extracts_education_projects_and_certifications() -> None:
    content = """
    Alex Builder
    alex@example.com

    PROJECTS
    ApplyForge
    - Built AI-assisted job hunt automation

    EDUCATION
    B.Tech Computer Science, IIT Delhi

    CERTIFICATIONS
    AWS Certified Developer - Associate
    """

    parsed = parse_resume_text(content)

    assert parsed["projects"][0]["name"] == "ApplyForge"
    assert "Built AI-assisted job hunt automation" in parsed["projects"][0]["highlights"]
    assert parsed["education"][0]["degree"] == "B.Tech Computer Science"
    assert parsed["education"][0]["institution"] == "IIT Delhi"
    assert parsed["certifications"][0]["name"] == "AWS Certified Developer - Associate"


def test_parse_resume_text_handles_multiline_devops_experience_blocks() -> None:
    content = """
    LAVKUSH KUMAR
    DevOps & Platform Engineer — Site Reliability (SRE) — Backend Engineer
    Bangalore, India | +91-9122036484 | pelavkushry@gmail.com

    SUMMARY
    DevOps & Platform Engineer with 2+ years of experience building Kubernetes-based microservices.

    EXPERIENCE
    Software Engineer – DevOps / Platform (EMS)
    08/2025 – Present
    HFCL
    Bangalore, India
    • Designed and built a production-grade on-prem Kubernetes platform for the EMS product.
    • Implemented Infrastructure as Code (IaC) using Ansible playbooks and shell scripts.
    """

    parsed = parse_resume_text(content)

    assert parsed["experience"][0]["title"] == "Software Engineer – DevOps / Platform (EMS)"
    assert parsed["experience"][0]["company"] == "HFCL"
    assert parsed["experience"][0]["start_date"] == "08/2025"
    assert parsed["experience"][0]["end_date"] == "Present"
    assert parsed["experience"][0]["highlights"] == [
        "Designed and built a production-grade on-prem Kubernetes platform for the EMS product.",
        "Implemented Infrastructure as Code (IaC) using Ansible playbooks and shell scripts.",
    ]


def test_parse_resume_text_strips_skill_category_labels_without_breaking_parentheses() -> None:
    content = """
    LAVKUSH KUMAR
    pelavkushry@gmail.com

    SKILLS
    Programming Languages: Go, Python, Bash, JavaScript
    Kubernetes & Containers: Kubernetes (multi-master, HA), kubeadm, Docker, containerd
    Observability & SRE: Prometheus Operator, Alertmanager, Grafana
    """

    parsed = parse_resume_text(content)

    assert "Programming Languages: Go" not in parsed["skills"]
    assert "Kubernetes & Containers: Kubernetes (multi-master" not in parsed["skills"]
    assert "Go" in parsed["skills"]
    assert "Kubernetes (multi-master, HA)" in parsed["skills"]
    assert "Prometheus Operator" in parsed["skills"]


def test_parse_resume_text_merges_wrapped_experience_highlights() -> None:
    content = """
    Alex Builder
    alex@example.com

    EXPERIENCE
    Platform Engineer at Forge Labs
    Jan 2024 - Present
    - Built a production-ready Kubernetes platform with kubeadm, containerd,
    HAProxy/Keepalived and an internal Harbor registry.
    """

    parsed = parse_resume_text(content)

    assert parsed["experience"][0]["highlights"] == [
        "Built a production-ready Kubernetes platform with kubeadm, containerd, HAProxy/Keepalived and an internal Harbor registry."
    ]
