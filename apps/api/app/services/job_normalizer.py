import hashlib


def infer_remote_type(location: str, description: str) -> str:
    combined = f"{location} {description}".lower()
    if "hybrid" in combined:
        return "hybrid"
    if "remote" in combined:
        return "remote"
    if "onsite" in combined or "on-site" in combined:
        return "onsite"
    return "unknown"


def infer_seniority(title: str, description: str) -> str:
    combined = f"{title} {description}".lower()
    for seniority in ("staff", "principal", "lead", "senior", "mid", "junior", "intern"):
        if seniority in combined:
            return seniority
    return "unknown"


def infer_employment_type(description: str) -> str:
    lowered = description.lower()
    if "contract" in lowered:
        return "contract"
    if "part-time" in lowered:
        return "part-time"
    if "intern" in lowered:
        return "internship"
    return "full-time"


def infer_tags(title: str, description: str) -> tuple[list[str], list[str]]:
    lowered = f"{title} {description}".lower()
    stack_tags = [
        tag
        for tag in ("python", "fastapi", "react", "typescript", "docker", "kubernetes", "postgresql", "ai")
        if tag in lowered
    ]
    domain_tags = [tag for tag in ("saas", "ai", "fintech", "healthcare", "data", "platform") if tag in lowered]
    return sorted(set(stack_tags)), sorted(set(domain_tags))


def build_dedupe_key(title: str, company: str, application_url: str, description: str) -> str:
    seed = "|".join([title.strip().lower(), company.strip().lower(), application_url.strip().lower(), description[:200]])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def normalize_job_payload(payload: dict) -> dict:
    stack_tags, domain_tags = infer_tags(payload.get("title", ""), payload.get("description", ""))
    remote_type = payload.get("remote_type") or infer_remote_type(payload.get("location", ""), payload.get("description", ""))
    seniority = payload.get("seniority") or infer_seniority(payload.get("title", ""), payload.get("description", ""))
    employment_type = payload.get("employment_type") or infer_employment_type(payload.get("description", ""))
    dedupe_key = build_dedupe_key(
        payload.get("title", ""),
        payload.get("company", ""),
        payload.get("application_url", ""),
        payload.get("description", ""),
    )

    normalized_description = {
        "summary": payload.get("description", "")[:500],
        "remote_type": remote_type,
        "seniority": seniority,
        "employment_type": employment_type,
    }

    return {
        **payload,
        "remote_type": remote_type,
        "seniority": seniority,
        "employment_type": employment_type,
        "stack_tags": stack_tags,
        "domain_tags": domain_tags,
        "tags": sorted(set(payload.get("tags", []) + stack_tags + domain_tags)),
        "normalized_description": normalized_description,
        "dedupe_key": dedupe_key,
    }
