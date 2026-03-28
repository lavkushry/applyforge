import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.entities import Company, CompanyCareerPortal

LEGAL_SUFFIXES = {
    "co",
    "company",
    "corp",
    "corporation",
    "gmbh",
    "inc",
    "incorporated",
    "limited",
    "llc",
    "ltd",
    "plc",
}


def normalize_company_name(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", name.lower().replace("&", " and "))
    tokens = [token for token in cleaned.split() if token and token not in LEGAL_SUFFIXES]
    return " ".join(tokens)


def hostname_from_url(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    return hostname.lower().removeprefix("www.")


def _company_hostname_matches(company: Company, hostname: str) -> bool:
    if not hostname:
        return False
    candidate_hosts = {
        hostname_from_url(company.website_url),
        hostname_from_url(company.careers_url),
        hostname_from_url(company.linkedin_url),
    }
    candidate_hosts.discard("")
    return hostname in candidate_hosts


def resolve_company_for_job(
    db: Session,
    *,
    user_id: int,
    company_name: str,
    application_url: str = "",
    source_url: str = "",
    explicit_company_id: int | None = None,
) -> Company | None:
    if explicit_company_id:
        return (
            db.query(Company)
            .filter(Company.id == explicit_company_id, Company.user_id == user_id)
            .first()
        )

    normalized_name = normalize_company_name(company_name)
    if normalized_name:
        by_name = (
            db.query(Company)
            .filter(
                Company.user_id == user_id,
                Company.normalized_name == normalized_name,
                Company.active.is_(True),
            )
            .first()
        )
        if by_name:
            return by_name

    candidate_hostnames = [hostname_from_url(application_url), hostname_from_url(source_url)]
    candidate_hostnames = [hostname for hostname in candidate_hostnames if hostname]
    if not candidate_hostnames:
        return None

    companies = db.query(Company).filter(Company.user_id == user_id, Company.active.is_(True)).all()
    for hostname in candidate_hostnames:
        for company in companies:
            if _company_hostname_matches(company, hostname):
                return company

    portals = (
        db.query(CompanyCareerPortal, Company)
        .join(Company, Company.id == CompanyCareerPortal.company_id)
        .filter(Company.user_id == user_id, Company.active.is_(True))
        .all()
    )
    for hostname in candidate_hostnames:
        for portal, company in portals:
            portal_hostname = hostname_from_url(portal.base_url)
            if portal_hostname and portal_hostname == hostname:
                return company

    return None
