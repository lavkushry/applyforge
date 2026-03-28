from __future__ import annotations

import importlib
import logging
from collections.abc import Iterable
from typing import Any

from app.models.entities import TargetRoleSource

JOBSPY_SOURCE_KIND = "jobspy_search"
JOBSPY_DEFAULT_SITES = ["linkedin", "indeed", "glassdoor", "google"]
JOBSPY_SUPPORTED_SITES = {
    "linkedin",
    "indeed",
    "glassdoor",
    "google",
    "zip_recruiter",
    "bayt",
    "naukri",
    "bdjobs",
}
JOBSPY_SITE_ALIASES = {
    "ziprecruiter": "zip_recruiter",
    "zip-recruiter": "zip_recruiter",
    "zip recruiter": "zip_recruiter",
}
INDEED_COUNTRY_HINTS = {
    "usa": "USA",
    "us": "USA",
    "united states": "USA",
    "united states of america": "USA",
    "india": "India",
    "bangalore": "India",
    "bengaluru": "India",
    "hyderabad": "India",
    "pune": "India",
    "mumbai": "India",
    "new delhi": "India",
    "delhi": "India",
    "gurgaon": "India",
    "noida": "India",
    "bangladesh": "Bangladesh",
    "dhaka": "Bangladesh",
    "uae": "United Arab Emirates",
    "united arab emirates": "United Arab Emirates",
    "dubai": "United Arab Emirates",
    "abu dhabi": "United Arab Emirates",
    "uk": "UK",
    "united kingdom": "UK",
    "england": "UK",
    "canada": "Canada",
    "toronto": "Canada",
    "vancouver": "Canada",
    "germany": "Germany",
    "berlin": "Germany",
}

logger = logging.getLogger(__name__)


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def normalize_jobspy_site_name(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_")
    return JOBSPY_SITE_ALIASES.get(normalized, normalized)


def parse_jobspy_site_names(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        candidates = value.replace("\n", ",").split(",")
    elif isinstance(value, Iterable):
        candidates = list(value)
    else:
        candidates = [value]

    sites: list[str] = []
    for candidate in candidates:
        site_name = normalize_jobspy_site_name(_clean_string(candidate))
        if site_name and site_name in JOBSPY_SUPPORTED_SITES and site_name not in sites:
            sites.append(site_name)
    return sites


def _default_jobspy_location(preferred_locations: list[str], remote_preference: str) -> str:
    for location in preferred_locations:
        cleaned = _clean_string(location)
        if cleaned and cleaned.lower() != "remote":
            return cleaned
    return "Remote" if remote_preference == "remote" else ""


def infer_indeed_country(*location_hints: str) -> str:
    combined = " ".join(hint.lower() for hint in location_hints if hint).strip()
    for hint, country in INDEED_COUNTRY_HINTS.items():
        if hint in combined:
            return country
    return "USA"


def build_jobspy_source_config(
    config: dict | None,
    *,
    role_name: str,
    preferred_locations: list[str],
    remote_preference: str,
) -> dict:
    raw_config = dict(config or {})
    site_names = parse_jobspy_site_names(raw_config.get("site_names") or raw_config.get("site_name")) or list(JOBSPY_DEFAULT_SITES)
    search_term = _clean_string(raw_config.get("search_term")) or role_name.strip()
    location = _clean_string(raw_config.get("location")) or _default_jobspy_location(preferred_locations, remote_preference)
    hydrated = {
        **raw_config,
        "site_names": site_names,
        "search_term": search_term,
        "results_wanted": _coerce_positive_int(raw_config.get("results_wanted"), 25),
        "hours_old": _coerce_positive_int(raw_config.get("hours_old"), 168),
    }
    if location:
        hydrated["location"] = location
    if "is_remote" not in hydrated and remote_preference == "remote":
        hydrated["is_remote"] = True
    if "linkedin_fetch_description" not in hydrated:
        hydrated["linkedin_fetch_description"] = True
    if "google" in site_names and not _clean_string(hydrated.get("google_search_term")):
        google_query = f"{search_term} jobs in {location}".strip() if location else search_term
        hydrated["google_search_term"] = google_query
    if any(site in {"indeed", "glassdoor"} for site in site_names) and not _clean_string(hydrated.get("country_indeed")):
        hydrated["country_indeed"] = infer_indeed_country(location, *preferred_locations)
    return hydrated


def prepare_target_role_source_payload(
    *,
    kind: str,
    label: str,
    base_url: str,
    config: dict | None,
    enabled: bool,
    role_name: str,
    preferred_locations: list[str],
    remote_preference: str,
) -> dict:
    prepared_config = dict(config or {})
    if kind == JOBSPY_SOURCE_KIND:
        prepared_config = build_jobspy_source_config(
            prepared_config,
            role_name=role_name,
            preferred_locations=preferred_locations,
            remote_preference=remote_preference,
        )
    return {
        "kind": kind,
        "label": label,
        "base_url": base_url,
        "config": prepared_config,
        "enabled": enabled,
    }


def _load_jobspy_scrape_jobs():
    try:
        module = importlib.import_module("jobspy")
    except ImportError as exc:
        raise RuntimeError(
            "python-jobspy is not installed. Rebuild the API image after installing apps/api/requirements.txt."
        ) from exc
    scrape_jobs = getattr(module, "scrape_jobs", None)
    if not callable(scrape_jobs):
        raise RuntimeError("python-jobspy is installed but jobspy.scrape_jobs is unavailable.")
    return scrape_jobs


def _records_from_jobspy_result(result: Any) -> list[dict]:
    if hasattr(result, "to_dict"):
        records = result.to_dict(orient="records")
    elif isinstance(result, list):
        records = result
    else:
        raise RuntimeError("JobSpy returned an unsupported result shape.")
    return [record for record in records if isinstance(record, dict)]


def _jobspy_kwargs_for_site(config: dict[str, Any], site_name: str) -> dict[str, Any]:
    search_term = _clean_string(config.get("search_term"))
    if not search_term:
        raise RuntimeError("JobSpy sources require a search_term in source.config.")

    kwargs: dict[str, Any] = {
        "site_name": site_name,
        "search_term": search_term,
        "results_wanted": _coerce_positive_int(config.get("results_wanted"), 25),
        "hours_old": _coerce_positive_int(config.get("hours_old"), 168),
    }
    location = _clean_string(config.get("location"))
    if location:
        kwargs["location"] = location
    google_search_term = _clean_string(config.get("google_search_term"))
    if google_search_term:
        kwargs["google_search_term"] = google_search_term
    country_indeed = _clean_string(config.get("country_indeed"))
    if country_indeed and site_name in {"indeed", "glassdoor"}:
        kwargs["country_indeed"] = country_indeed
    if isinstance(config.get("is_remote"), bool):
        kwargs["is_remote"] = config["is_remote"]
    job_type = _clean_string(config.get("job_type"))
    if job_type:
        kwargs["job_type"] = job_type
    if isinstance(config.get("linkedin_fetch_description"), bool) and site_name == "linkedin":
        kwargs["linkedin_fetch_description"] = config["linkedin_fetch_description"]
    return kwargs


def _summarize_jobspy_error(site_name: str, exc: Exception) -> str:
    message = _clean_string(exc) or exc.__class__.__name__
    return f"{site_name}: {message}"


def _format_amount(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return ""
    if amount.is_integer():
        return f"{int(amount):,}"
    return f"{amount:,.2f}".rstrip("0").rstrip(".")


def _format_salary(record: dict) -> str:
    low_raw = record.get("min_amount")
    high_raw = record.get("max_amount")
    low = _format_amount(low_raw)
    high = _format_amount(high_raw)
    if low and high:
        low_number = float(low_raw)
        high_number = float(high_raw)
        if low_number > high_number:
            low, high = high, low
        amount_text = f"{low} - {high}"
    else:
        amount_text = low or high
    if not amount_text:
        return ""
    currency = _clean_string(record.get("currency"))
    interval = _clean_string(record.get("interval"))
    salary = " ".join(part for part in [currency, amount_text] if part)
    if interval:
        salary = f"{salary} / {interval}"
    return salary


def _flatten_location(location: Any) -> str:
    if isinstance(location, dict):
        parts = [_clean_string(location.get(key)) for key in ("city", "state", "country")]
        return ", ".join(part for part in parts if part)
    return _clean_string(location)


def _as_list_of_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        cleaned = _clean_string(value)
        return [cleaned] if cleaned else []
    if isinstance(value, Iterable):
        return [item for item in (_clean_string(part) for part in value) if item]
    return []


def _jobspy_remote_type(record: dict, location: str, description: str) -> str:
    if record.get("is_remote") is True:
        return "remote"
    work_from_home_type = _clean_string(record.get("work_from_home_type")).lower()
    if "hybrid" in work_from_home_type:
        return "hybrid"
    if "remote" in work_from_home_type:
        return "remote"
    combined = f"{location} {description}".lower()
    if "hybrid" in combined:
        return "hybrid"
    if "remote" in combined:
        return "remote"
    return "unknown"


def fetch_jobspy_jobs(source: TargetRoleSource) -> list[dict]:
    config = dict(source.config or {})
    site_names = parse_jobspy_site_names(config.get("site_names") or config.get("site_name")) or list(JOBSPY_DEFAULT_SITES)
    scrape_jobs = _load_jobspy_scrape_jobs()
    search_term = _clean_string(config.get("search_term"))
    records: list[dict] = []
    errors: list[str] = []

    for site_name in site_names:
        try:
            result = scrape_jobs(**_jobspy_kwargs_for_site(config, site_name))
        except Exception as exc:
            error_summary = _summarize_jobspy_error(site_name, exc)
            logger.warning("jobspy_site_failed: %s", error_summary)
            errors.append(error_summary)
            continue
        records.extend(_records_from_jobspy_result(result))

    if not records and errors:
        raise RuntimeError(
            "JobSpy returned no jobs. "
            + "; ".join(errors[:4])
            + ("; additional site failures omitted" if len(errors) > 4 else "")
        )

    jobs: list[dict] = []
    for record in records:
        title = _clean_string(record.get("title"))
        company = _clean_string(record.get("company"))
        application_url = _clean_string(record.get("job_url"))
        description = _clean_string(record.get("description")) or title
        location_text = _flatten_location(record.get("location"))
        site_name = normalize_jobspy_site_name(_clean_string(record.get("site")))
        tags = _as_list_of_strings(record.get("skills")) + _as_list_of_strings(record.get("emails"))
        jobs.append(
            {
                "title": title or "Job board role",
                "company": company or source.label or "Unknown Company",
                "location": location_text,
                "remote_type": _jobspy_remote_type(record, location_text, description),
                "salary": _format_salary(record),
                "employment_type": _clean_string(record.get("job_type")),
                "application_url": application_url,
                "description": description,
                "source": site_name or "jobspy",
                "tags": sorted(set(tags)),
                "source_metadata": {
                    "aggregator": "jobspy",
                    "site": site_name or "jobspy",
                    "search_term": search_term,
                    "source_label": source.label,
                    "source_kind": source.kind,
                    "company_url": _clean_string(record.get("company_url")),
                    "job_level": _clean_string(record.get("job_level")),
                    "date_posted": _clean_string(record.get("date_posted")),
                },
            }
        )
    return jobs
