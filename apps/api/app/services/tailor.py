def tailor_resume(profile: dict, job: dict) -> dict:
    summary = f"{profile.get('summary', '')} Tailored for {job.get('title', 'role')} at {job.get('company', 'company')}."
    skills = profile.get('skills', [])
    jd = job.get('description', '').lower()
    ranked_skills = sorted(skills, key=lambda x: 0 if x.lower() in jd else 1)
    return {
        'basics': profile.get('basics', {}),
        'summary': summary,
        'skills': ranked_skills,
        'experience': profile.get('experience', []),
        'projects': profile.get('projects', []),
        'education': profile.get('education', []),
        'certifications': profile.get('certifications', []),
        'links': profile.get('links', []),
        'fact_locked': True,
    }


def generate_cover_letter(profile: dict, job: dict) -> str:
    return (
        f"Dear Hiring Team at {job.get('company')},\n\n"
        f"I am excited to apply for the {job.get('title')} role. "
        f"My background in {', '.join(profile.get('skills', [])[:3])} aligns with your needs.\n\n"
        "I would value the opportunity to contribute and discuss this further.\n\n"
        "Sincerely,\n"
        f"{profile.get('basics', {}).get('full_name', 'Candidate')}"
    )
