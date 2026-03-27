def score_job(candidate: dict, job_description: str, title: str) -> dict:
    skills = set([s.lower() for s in candidate.get('skills', [])])
    jd = job_description.lower()
    overlaps = [skill for skill in skills if skill in jd]
    missing = [s for s in ['python', 'sql', 'aws', 'docker'] if s not in jd and s in skills]

    role_bonus = 15 if candidate.get('basics', {}).get('target_role', '').lower() in title.lower() else 5
    score = min(100, 40 + len(overlaps) * 12 + role_bonus)
    recommendation = 'high priority' if score >= 75 else 'maybe' if score >= 55 else 'skip'

    return {
        'overall_score': float(score),
        'missing_skills': missing,
        'strengths': overlaps,
        'reasons': [
            f"Matched {len(overlaps)} known skills",
            f"Role alignment bonus applied: {role_bonus}",
        ],
        'recommendation': recommendation,
    }
