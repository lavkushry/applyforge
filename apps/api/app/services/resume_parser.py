import re
from pathlib import Path
from urllib.parse import urlparse

from docx import Document
from pypdf import PdfReader


SECTION_HEADERS = {
    "summary": {"summary", "professional summary", "profile", "about"},
    "skills": {"skills", "technical skills", "core skills", "core competencies", "technologies"},
    "experience": {"experience", "work experience", "professional experience", "employment", "employment history", "work history"},
    "projects": {"projects", "project experience", "open source"},
    "education": {"education", "academic background"},
    "certifications": {"certifications", "licenses", "certificates"},
    "links": {"links", "profiles"},
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
URL_RE = re.compile(r"(?:https?://|www\.)[^\s|•·]+")
MONTH_PATTERN = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
NUMERIC_MONTH_YEAR_PATTERN = r"(?:\d{1,2}[/-]\d{4})"
DATE_PART_PATTERN = rf"(?:{MONTH_PATTERN}\s+\d{{4}}|{NUMERIC_MONTH_YEAR_PATTERN}|\d{{4}}|Present|Current)"
DATE_RANGE_RE = re.compile(rf"(?P<start>{DATE_PART_PATTERN})\s*(?:-|–|—|to)\s*(?P<end>{DATE_PART_PATTERN})", re.IGNORECASE)
BULLET_RE = re.compile(r"^(?:[-*•▪◦]\s+)(.+)$")
ROLE_KEYWORDS = {
    "engineer",
    "developer",
    "manager",
    "architect",
    "analyst",
    "consultant",
    "administrator",
    "specialist",
    "platform",
    "backend",
    "frontend",
    "full-stack",
    "full",
    "devops",
    "sre",
    "software",
    "site",
    "lead",
    "staff",
    "principal",
    "intern",
}


def extract_resume_text(path: str) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    return file_path.read_text(errors="ignore")


def _clean_line(line: str) -> str:
    cleaned = line.replace("\u00a0", " ")
    cleaned = re.sub(r"[⌢⌣☎✉♂♀]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _normalize_header(line: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z&/ ]+", "", line).strip().lower()
    return cleaned.replace("/", " ").replace("  ", " ")


def _split_segments(line: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"\s*[|•·]\s*", line) if segment.strip()]


def _split_contact_segments(line: str) -> list[str]:
    normalized = re.sub(r"\b(?:phone|mobile|tel|email|envel)\b", " ", line, flags=re.IGNORECASE)
    parts = re.split(r"\s*(?:[|•·]|\s+[–—]\s+)\s*", normalized)
    return [part.strip(" /-–—") for part in parts if part.strip(" /-–—")]


def _split_outside_parentheses(text: str, delimiters: set[str]) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0

    for char in text:
        if char in "([{":
            depth += 1
        elif char in ")]}" and depth > 0:
            depth -= 1

        if depth == 0 and char in delimiters:
            segment = "".join(current).strip()
            if segment:
                parts.append(segment)
            current = []
            continue

        current.append(char)

    final = "".join(current).strip()
    if final:
        parts.append(final)
    return parts


def _contains_role_keyword(text: str) -> bool:
    lowered = text.lower()
    for keyword in ROLE_KEYWORDS:
        pattern = r"\b" + re.escape(keyword).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, lowered):
            return True
    return False


def _is_section_header(line: str) -> str | None:
    normalized = _normalize_header(line.rstrip(":"))
    for section, variants in SECTION_HEADERS.items():
        if normalized in variants:
            return section
    return None


def _is_contact_line(line: str) -> bool:
    return bool(EMAIL_RE.search(line) or PHONE_RE.search(line) or URL_RE.search(line) or len(_split_segments(line)) > 1)


def _extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> str:
    match = PHONE_RE.search(text)
    return _clean_line(match.group(1)) if match else ""


def _looks_like_location(segment: str) -> bool:
    lowered = segment.lower()
    if _contains_role_keyword(lowered):
        return False
    if any(token in lowered for token in ("labs", "systems", "technologies", "inc", "llc", "corp", "company")):
        return False
    if any(token in lowered for token in ("remote", "hybrid", "onsite", "india", "usa", "united states", "uk", "canada")):
        return True
    if "," in segment and "@" not in segment and "http" not in lowered:
        return True
    words = segment.split()
    return 1 < len(words) <= 5 and segment == segment.title()


def _normalize_url(url: str) -> str:
    cleaned = url.rstrip(".,);")
    return cleaned if cleaned.startswith("http") else f"https://{cleaned}"


def _label_for_url(url: str) -> str:
    hostname = urlparse(_normalize_url(url)).netloc.lower().removeprefix("www.")
    if "linkedin.com" in hostname:
        return "linkedin"
    if "github.com" in hostname:
        return "github"
    if "gitlab.com" in hostname:
        return "gitlab"
    if "portfolio" in hostname:
        return "portfolio"
    if hostname:
        return hostname.split(".")[0]
    return "profile"


def _extract_links(text: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_url in URL_RE.findall(text):
        normalized = _normalize_url(raw_url)
        if normalized in seen:
            continue
        seen.add(normalized)
        links.append({"label": _label_for_url(normalized), "url": normalized})
    return links


def _extract_basics(lines: list[str], text: str) -> dict:
    first_section_index = next((index for index, line in enumerate(lines) if _is_section_header(line)), len(lines))
    header_lines = lines[: min(first_section_index, 6)]
    name = header_lines[0] if header_lines else "Unknown Candidate"

    headline = ""
    for line in header_lines[1:]:
        if _is_contact_line(line) or _is_section_header(line):
            continue
        headline = line
        break

    location = ""
    for line in header_lines[1:]:
        if not _is_contact_line(line) and "," not in line:
            continue
        segments = _split_contact_segments(line) if _is_contact_line(line) else [line]
        for segment in segments:
            if EMAIL_RE.search(segment) or PHONE_RE.search(segment) or URL_RE.search(segment):
                continue
            if _looks_like_location(segment):
                location = segment
                break
        if location:
            break

    return {
        "full_name": name,
        "headline": headline,
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "location": location,
    }


def _extract_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {key: [] for key in SECTION_HEADERS}
    first_section_index = next((index for index, line in enumerate(lines) if _is_section_header(line)), None)

    if first_section_index is None:
        sections["summary"] = lines[2:6]
        return sections

    current_section = "summary"
    for line in lines[first_section_index:]:
        matched = _is_section_header(line.rstrip(":"))
        if matched:
            current_section = matched
            continue
        sections[current_section].append(line)
    return sections


def _parse_skills(lines: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()

    for line in lines:
        cleaned_line = _clean_line(line)
        if not cleaned_line:
            continue
        payload = cleaned_line.split(":", 1)[1].strip() if ":" in cleaned_line else cleaned_line
        for part in _split_outside_parentheses(payload, {",", ";", "|", "•", "·"}):
            cleaned = _clean_line(part)
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            unique.append(cleaned)
    return unique


def _bullet_text(line: str) -> str | None:
    match = BULLET_RE.match(line)
    return _clean_line(match.group(1)) if match else None


def _extract_date_range(text: str) -> tuple[str, str]:
    match = DATE_RANGE_RE.search(text)
    if not match:
        return "", ""
    return _clean_line(match.group("start")), _clean_line(match.group("end"))


def _is_date_only_line(line: str) -> bool:
    return bool(DATE_RANGE_RE.fullmatch(line.strip()))


def _looks_like_company_line(line: str) -> bool:
    cleaned = _clean_line(line)
    if not cleaned or "." in cleaned or "http" in cleaned.lower() or _looks_like_location(cleaned):
        return False
    lowered = cleaned.lower()
    if _contains_role_keyword(lowered):
        return False
    words = cleaned.split()
    if len(words) > 6:
        return False
    return (
        cleaned == cleaned.title()
        or cleaned.isupper()
        or any(token in cleaned.lower() for token in ("labs", "systems", "technologies", "inc", "llc", "corp", "company"))
    )


def _looks_like_experience_header(line: str) -> bool:
    cleaned = _clean_line(line)
    if not cleaned or _is_date_only_line(cleaned) or _looks_like_company_line(cleaned) or _looks_like_location(cleaned):
        return False
    lowered = cleaned.lower()
    if "|" in cleaned or re.search(r"\s+at\s+", cleaned, re.IGNORECASE):
        return True
    words = lowered.split()
    if len(words) > 10:
        return False
    return _contains_role_keyword(lowered)


def _parse_title_company(line: str) -> tuple[str, str]:
    cleaned = DATE_RANGE_RE.sub("", line).strip(" |-–—,")
    if "|" in cleaned:
        parts = _split_outside_parentheses(cleaned, {"|"})
        if len(parts) >= 2:
            return parts[0], parts[1]
    at_match = re.match(r"(?P<title>.+?)\s+at\s+(?P<company>.+)", cleaned, re.IGNORECASE)
    if at_match:
        return _clean_line(at_match.group("title")), _clean_line(at_match.group("company"))
    if "," in cleaned:
        title, company = cleaned.split(",", 1)
        company = _clean_line(company)
        if _looks_like_company_line(company):
            return _clean_line(title), company
    dash_parts = re.split(r"\s+[–—-]\s+", cleaned, maxsplit=1)
    if len(dash_parts) == 2 and _looks_like_company_line(dash_parts[1]):
        return _clean_line(dash_parts[0]), _clean_line(dash_parts[1])
    return cleaned, ""

def _empty_experience_entry() -> dict[str, str | list[str]]:
    return {"title": "", "company": "", "start_date": "", "end_date": "", "highlights": []}


def _finalize_experience_entry(entry: dict[str, str | list[str]]) -> dict:
    return {
        "title": entry["title"],
        "company": entry["company"],
        "start_date": entry["start_date"],
        "end_date": entry["end_date"],
        "highlights": list(dict.fromkeys(entry["highlights"])),
    }


def _parse_experience(lines: list[str]) -> list[dict]:
    entries: list[dict] = []
    current: dict[str, str | list[str]] | None = None

    for line in lines:
        cleaned = _clean_line(line)
        if not cleaned:
            continue
        bullet = _bullet_text(line)
        if bullet:
            if current is None:
                current = _empty_experience_entry()
            current["highlights"].append(bullet)
            continue

        if current and current["highlights"] and not _looks_like_experience_header(cleaned):
            current["highlights"][-1] = f"{current['highlights'][-1]} {cleaned}".strip()
            continue

        if _is_date_only_line(cleaned):
            if current is None:
                current = _empty_experience_entry()
            if not current["start_date"]:
                current["start_date"], current["end_date"] = _extract_date_range(cleaned)
            continue

        if current and not current["company"] and _looks_like_company_line(cleaned):
            current["company"] = cleaned
            continue

        if current and _looks_like_location(cleaned):
            continue

        if current and any((current["title"], current["company"], current["highlights"])):
            entries.append(_finalize_experience_entry(current))

        title, company = _parse_title_company(cleaned)
        start_date, end_date = _extract_date_range(cleaned)
        current = {
            "title": title,
            "company": company,
            "start_date": start_date,
            "end_date": end_date,
            "highlights": [],
        }

    if current and any((current["title"], current["company"], current["highlights"])):
        entries.append(_finalize_experience_entry(current))

    return [entry for entry in entries if entry["title"] or entry["company"]][:6]


def _finalize_named_block(lines: list[str], highlights: list[str], key: str) -> dict:
    name = lines[0] if lines else ""
    for line in lines[1:]:
        cleaned = _clean_line(line)
        if cleaned:
            highlights.append(cleaned)
    return {key: name, "highlights": list(dict.fromkeys(highlights))}


def _parse_projects(lines: list[str]) -> list[dict]:
    entries: list[dict] = []
    current_lines: list[str] = []
    current_highlights: list[str] = []

    for line in lines:
        bullet = _bullet_text(line)
        if bullet:
            current_highlights.append(bullet)
            continue
        if not current_lines:
            current_lines = [line]
            continue
        if current_highlights:
            entries.append(_finalize_named_block(current_lines, current_highlights, "name"))
            current_lines = [line]
            current_highlights = []
            continue
        entries.append(_finalize_named_block(current_lines, current_highlights, "name"))
        current_lines = [line]

    if current_lines:
        entries.append(_finalize_named_block(current_lines, current_highlights, "name"))

    return [entry for entry in entries if entry["name"]][:6]


def _parse_education(lines: list[str]) -> list[dict]:
    entries: list[dict] = []
    for line in lines:
        cleaned = _clean_line(line)
        if not cleaned or _bullet_text(cleaned):
            continue
        if "|" in cleaned:
            parts = [part.strip() for part in cleaned.split("|") if part.strip()]
            degree = parts[0]
            institution_parts = [part for part in parts[1:] if not _is_date_only_line(part) and not DATE_RANGE_RE.search(part)]
            institution = ", ".join(institution_parts[:2]) if institution_parts else ""
        elif "," in cleaned:
            degree, institution = [part.strip() for part in cleaned.split(",", 1)]
        elif re.search(r"\s+at\s+", cleaned, re.IGNORECASE):
            degree, institution = re.split(r"\s+at\s+", cleaned, maxsplit=1, flags=re.IGNORECASE)
        else:
            degree, institution = cleaned, ""
        entries.append({"degree": degree, "institution": institution})
    return entries[:4]


def _parse_certifications(lines: list[str]) -> list[dict]:
    entries = []
    for line in lines:
        cleaned = _bullet_text(line) or _clean_line(line)
        if cleaned:
            entries.append({"name": cleaned, "issuer": ""})
    return entries[:6]


def parse_resume_text(text: str) -> dict:
    lines = [_clean_line(line) for line in text.splitlines() if _clean_line(line)]
    sections = _extract_sections(lines)
    basics = _extract_basics(lines, text)
    links = _extract_links(text)
    summary_lines = sections["summary"]
    summary = " ".join(
        line
        for line in summary_lines
        if line
        and not _is_contact_line(line)
        and line.lower() not in {basics["full_name"].lower(), basics["headline"].lower()}
    ).strip()

    return {
        "basics": basics,
        "summary": summary or (lines[2] if len(lines) > 2 and not _is_contact_line(lines[2]) else ""),
        "skills": _parse_skills(sections["skills"]),
        "experience": _parse_experience(sections["experience"]),
        "projects": _parse_projects(sections["projects"]),
        "education": _parse_education(sections["education"]),
        "certifications": _parse_certifications(sections["certifications"]),
        "links": links,
        "preferences": {},
        "saved_answers": {},
        "fact_locked": True,
    }


def parse_resume_file(path: str) -> dict:
    return parse_resume_text(extract_resume_text(path))
