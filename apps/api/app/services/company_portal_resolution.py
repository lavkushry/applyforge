from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.entities import Company, CompanyCareerPortal


def _clean_url(url: str) -> str:
    return url.strip().rstrip("/")


def _board_slug_from_url(url: str) -> str:
    path_bits = [bit for bit in urlparse(url).path.split("/") if bit]
    return path_bits[-1] if path_bits else ""


def _infer_portal_payload(url: str) -> dict | None:
    cleaned_url = _clean_url(url)
    if not cleaned_url:
        return None

    hostname = (urlparse(cleaned_url).hostname or "").lower()
    if "greenhouse.io" in hostname:
        board_token = _board_slug_from_url(cleaned_url)
        return {
            "provider_kind": "greenhouse",
            "base_url": cleaned_url,
            "board_token": board_token,
            "health_status": "resolved",
            "supports_structured_fetch": True,
            "resolution_metadata": {
                "resolution_kind": "heuristic",
                "resolved_from": cleaned_url,
            },
        }

    if hostname == "jobs.lever.co" or hostname.endswith(".lever.co") or hostname.endswith(".lever.co.uk"):
        board_token = _board_slug_from_url(cleaned_url)
        return {
            "provider_kind": "lever",
            "base_url": cleaned_url,
            "board_token": board_token,
            "health_status": "resolved",
            "supports_structured_fetch": True,
            "resolution_metadata": {
                "resolution_kind": "heuristic",
                "resolved_from": cleaned_url,
            },
        }

    return {
        "provider_kind": "direct_site",
        "base_url": cleaned_url,
        "board_token": "",
        "health_status": "resolved",
        "supports_structured_fetch": False,
        "resolution_metadata": {
            "resolution_kind": "heuristic",
            "resolved_from": cleaned_url,
        },
    }


def resolve_company_portals(db: Session, *, company: Company) -> list[CompanyCareerPortal]:
    candidate_urls = [company.careers_url]
    resolved: list[CompanyCareerPortal] = []

    for candidate_url in candidate_urls:
        payload = _infer_portal_payload(candidate_url)
        if payload is None:
            continue

        existing = (
            db.query(CompanyCareerPortal)
            .filter(
                CompanyCareerPortal.company_id == company.id,
                CompanyCareerPortal.provider_kind == payload["provider_kind"],
                CompanyCareerPortal.base_url == payload["base_url"],
                CompanyCareerPortal.board_token == payload["board_token"],
            )
            .first()
        )
        if existing:
            existing.health_status = payload["health_status"]
            existing.supports_structured_fetch = payload["supports_structured_fetch"]
            existing.resolution_metadata = payload["resolution_metadata"]
            resolved.append(existing)
            continue

        portal = CompanyCareerPortal(company_id=company.id, notes="Resolved from company careers URL", **payload)
        db.add(portal)
        db.flush()
        resolved.append(portal)

    db.commit()
    for portal in resolved:
        db.refresh(portal)
    return resolved
