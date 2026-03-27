import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader


SECTION_HEADERS = {
    "summary": {"summary", "professional summary", "profile"},
    "skills": {"skills", "technical skills", "core skills"},
    "experience": {"experience", "work experience", "professional experience"},
    "projects": {"projects"},
    "education": {"education"},
    "certifications": {"certifications", "licenses"},
    "links": {"links", "profiles"},
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


def parse_resume_text(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections: dict[str, list[str]] = {key: [] for key in SECTION_HEADERS}
    current_section = "summary"

    for line in lines[2:]:
        lowered = line.lower().strip(":")
        matched_section = next((key for key, variants in SECTION_HEADERS.items() if lowered in variants), None)
        if matched_section:
            current_section = matched_section
            continue
        sections[current_section].append(line)

    skills_text = " ".join(sections["skills"])
    raw_skills = []
    for part in skills_text.replace("|", ",").split(","):
        cleaned = part.strip()
        if cleaned:
            raw_skills.append(cleaned)

    unique_skills = list(dict.fromkeys(raw_skills))
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    links = re.findall(r"https?://\S+", text)
    basics = {
        "full_name": lines[0] if lines else "Unknown Candidate",
        "headline": lines[1] if len(lines) > 1 else "",
        "email": email_match.group(0) if email_match else None,
        "location": next((line for line in lines if "," in line and "@" not in line and "http" not in line), ""),
    }

    return {
        "basics": basics,
        "summary": " ".join(sections["summary"]).strip() or (lines[2] if len(lines) > 2 else ""),
        "skills": unique_skills,
        "experience": [{"title": item, "company": "", "highlights": []} for item in sections["experience"][:5]],
        "projects": [{"name": item, "highlights": []} for item in sections["projects"][:4]],
        "education": [{"institution": item} for item in sections["education"][:4]],
        "certifications": [{"name": item} for item in sections["certifications"][:4]],
        "links": [{"label": "profile", "url": link} for link in links],
        "preferences": {},
        "saved_answers": {},
        "fact_locked": True,
    }


def parse_resume_file(path: str) -> dict:
    return parse_resume_text(extract_resume_text(path))
