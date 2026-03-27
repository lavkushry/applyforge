from pathlib import Path

from pypdf import PdfReader


def parse_resume_file(path: str) -> dict:
    file_path = Path(path)
    text = ''
    if file_path.suffix.lower() == '.pdf':
        reader = PdfReader(path)
        text = '\n'.join((page.extract_text() or '') for page in reader.pages)
    else:
        text = file_path.read_text(errors='ignore')

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skills = [s.strip() for s in ['Python', 'FastAPI', 'SQL', 'React'] if s.lower() in text.lower()]
    return {
        'basics': {'full_name': lines[0] if lines else 'Unknown Candidate'},
        'summary': lines[1] if len(lines) > 1 else 'Generated summary placeholder.',
        'skills': skills,
        'experience': [],
        'projects': [],
        'education': [],
        'certifications': [],
        'links': [],
        'fact_locked': True,
    }
