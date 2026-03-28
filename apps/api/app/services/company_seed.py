from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.entities import Company
from app.services.company_directory import normalize_company_name

AWESOME_CAREER_PAGES_PAGE_URL = "https://github.com/CSwala/awesome-career-pages?tab=readme-ov-file"
INTERNATIONAL_COMPANIES_GIST_PAGE_URL = "https://gist.github.com/idontknowjs/22f3257bed32dd3ab99ff22316e51eb8"
LOW_SIGNAL_HOSTS = {
    "angel.co",
    "linkedin.com",
    "naukri.com",
    "www.linkedin.com",
    "www.naukri.com",
}


@dataclass(frozen=True, slots=True)
class CompanySeed:
    name: str
    careers_url: str = ""
    website_url: str = ""
    linkedin_url: str = ""
    hq_location: str = ""
    industry: str = ""
    notes: str = ""


@dataclass(frozen=True, slots=True)
class CompanySeedUpsertResult:
    requested_count: int
    created_count: int
    updated_count: int
    unchanged_count: int


def normalize_seed_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned:
        return ""
    if cleaned.startswith(("http://", "https://")):
        return cleaned
    if cleaned.startswith("//"):
        return f"https:{cleaned}"
    return f"https://{cleaned.lstrip('/')}"


def _company_seed_key(name: str) -> str:
    return normalize_company_name(name).replace(" ", "")


def _hostname(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def _url_quality(url: str) -> tuple[int, int]:
    hostname = _hostname(url)
    is_low_signal = 1 if hostname in LOW_SIGNAL_HOSTS else 0
    # Prefer non-social/non-aggregator hosts, then shorter URLs for cleaner canonicalization.
    return (-is_low_signal, -len(url))


def _should_replace_url(existing_url: str, candidate_url: str) -> bool:
    if not candidate_url:
        return False
    if not existing_url:
        return True
    return _url_quality(candidate_url) > _url_quality(existing_url)


def _parse_markdown_link(text: str) -> tuple[str, str] | None:
    content = text.strip()
    if not content.startswith("["):
        return None

    depth = 0
    closing_index: int | None = None
    for index, char in enumerate(content):
        if char == "[":
            depth += 1
            continue
        if char == "]":
            depth -= 1
            if depth == 0:
                closing_index = index
                break

    if closing_index is None:
        return None
    if closing_index + 1 >= len(content) or content[closing_index + 1] != "(":
        return None

    name = " ".join(content[1:closing_index].split())
    remainder = content[closing_index + 2 :]
    url_end_index = remainder.rfind(")")
    if url_end_index == -1:
        return None
    url = normalize_seed_url(remainder[:url_end_index].strip())
    if not name or not url:
        return None
    return name, url


def _parse_heading_link(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped.startswith("###"):
        return None

    return _parse_markdown_link(stripped.lstrip("#").strip())


def parse_awesome_career_pages_markdown(
    markdown: str,
    *,
    source_page_url: str = AWESOME_CAREER_PAGES_PAGE_URL,
) -> list[CompanySeed]:
    note = f"Imported from Awesome Career Pages: {source_page_url}"
    records: dict[str, CompanySeed] = {}

    for line in markdown.splitlines():
        parsed = _parse_heading_link(line)
        if parsed is None:
            continue

        name, careers_url = parsed
        key = _company_seed_key(name)
        if not key:
            continue

        seed = CompanySeed(name=name, careers_url=careers_url, notes=note)
        existing = records.get(key)
        if existing is None:
            records[key] = seed
            continue

        if _should_replace_url(existing.careers_url, careers_url):
            records[key] = CompanySeed(
                name=existing.name,
                careers_url=careers_url,
                website_url=existing.website_url,
                linkedin_url=existing.linkedin_url,
                hq_location=existing.hq_location,
                industry=existing.industry,
                notes=existing.notes,
            )

    return sorted(records.values(), key=lambda item: item.name.casefold())


def _international_location_heading(line: str) -> str | None:
    match = re.match(r"^\*\*(.+?)\*\*", line.strip())
    if not match:
        return None
    heading = match.group(1).strip().rstrip(":")
    if heading in {"FAQs", "Q", "A"}:
        return None
    return heading


def _parse_international_company_entry(raw_name: str) -> tuple[str, str]:
    cleaned = raw_name.strip().strip("-").strip()
    if not cleaned or cleaned.startswith("Mentioned in "):
        return "", ""
    parsed_link = _parse_markdown_link(cleaned)
    careers_url = ""
    if parsed_link is not None:
        cleaned, careers_url = parsed_link
    if "," in cleaned:
        head, tail = cleaned.split(",", 1)
        if 0 < len(tail.split()) <= 3:
            cleaned = head.strip()
    return cleaned, careers_url


def parse_international_companies_markdown(
    markdown: str,
    *,
    source_page_url: str = INTERNATIONAL_COMPANIES_GIST_PAGE_URL,
) -> list[CompanySeed]:
    locations_by_key: dict[str, set[str]] = {}
    seeds_by_key: dict[str, CompanySeed] = {}
    current_location = ""

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        maybe_heading = _international_location_heading(line)
        if maybe_heading is not None:
            current_location = maybe_heading
            continue

        if not current_location or not line.startswith("* "):
            continue

        name, careers_url = _parse_international_company_entry(line[2:])
        if not name:
            continue

        key = _company_seed_key(name)
        if not key:
            continue
        locations_by_key.setdefault(key, set()).add(current_location)
        existing = seeds_by_key.get(key)
        if existing is None:
            seeds_by_key[key] = CompanySeed(name=name, careers_url=careers_url)
            continue
        if _should_replace_url(existing.careers_url, careers_url):
            seeds_by_key[key] = CompanySeed(name=existing.name, careers_url=careers_url)

    seeds: list[CompanySeed] = []
    for key, locations in locations_by_key.items():
        seed = seeds_by_key[key]
        sorted_locations = sorted(locations, key=str.casefold)
        note = (
            "Imported from international companies hiring list: "
            f"{source_page_url}. Mentioned hiring/relocation locations: {'; '.join(sorted_locations)}"
        )
        seeds.append(
            CompanySeed(
                name=seed.name,
                careers_url=seed.careers_url,
                notes=note,
            )
        )
    return sorted(seeds, key=lambda item: item.name.casefold())


def cleanup_imported_markdown_link_companies(
    db: Session,
    *,
    user_id: int,
    source_page_url: str,
) -> int:
    companies = (
        db.query(Company)
        .filter(Company.user_id == user_id, Company.notes.contains(source_page_url))
        .all()
    )
    deleted_count = 0
    for company in companies:
        if company.name.startswith("[") and "](" in company.name and company.name.endswith(")"):
            db.delete(company)
            deleted_count += 1
    return deleted_count


def _find_company_for_seed(db: Session, *, user_id: int, seed: CompanySeed) -> Company | None:
    normalized_name = normalize_company_name(seed.name)
    company = (
        db.query(Company)
        .filter(Company.user_id == user_id, Company.normalized_name == normalized_name)
        .first()
    )
    if company is not None:
        return company

    compact_name = normalized_name.replace(" ", "")
    if not compact_name:
        return None

    companies = db.query(Company).filter(Company.user_id == user_id).all()
    for candidate in companies:
        if candidate.normalized_name.replace(" ", "") == compact_name:
            return candidate
    return None


def upsert_company_seeds(
    db: Session,
    *,
    user_id: int,
    seeds: list[CompanySeed],
) -> CompanySeedUpsertResult:
    created_count = 0
    updated_count = 0
    unchanged_count = 0

    for seed in seeds:
        normalized_name = normalize_company_name(seed.name)
        if not normalized_name:
            continue

        company = _find_company_for_seed(db, user_id=user_id, seed=seed)
        if company is None:
            db.add(
                Company(
                    user_id=user_id,
                    name=seed.name,
                    normalized_name=normalized_name,
                    website_url=seed.website_url,
                    careers_url=seed.careers_url,
                    linkedin_url=seed.linkedin_url,
                    hq_location=seed.hq_location,
                    industry=seed.industry,
                    notes=seed.notes,
                    active=True,
                )
            )
            created_count += 1
            continue

        changed = False
        if seed.website_url and not company.website_url:
            company.website_url = seed.website_url
            changed = True
        if seed.careers_url and not company.careers_url:
            company.careers_url = seed.careers_url
            changed = True
        if seed.linkedin_url and not company.linkedin_url:
            company.linkedin_url = seed.linkedin_url
            changed = True
        if seed.hq_location and not company.hq_location:
            company.hq_location = seed.hq_location
            changed = True
        if seed.industry and not company.industry:
            company.industry = seed.industry
            changed = True
        if seed.notes and seed.notes not in company.notes:
            company.notes = "\n\n".join(part for part in [company.notes.strip(), seed.notes] if part).strip()
            changed = True

        if changed:
            updated_count += 1
        else:
            unchanged_count += 1

    db.commit()
    return CompanySeedUpsertResult(
        requested_count=len(seeds),
        created_count=created_count,
        updated_count=updated_count,
        unchanged_count=unchanged_count,
    )
