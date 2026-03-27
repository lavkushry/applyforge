from pathlib import Path
from uuid import uuid4

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.core.config import settings


def save_upload(filename: str, content: bytes) -> str:
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)
    target = Path(settings.storage_path) / f"{uuid4()}_{filename}"
    target.write_bytes(content)
    return str(target)


def render_resume_pdf(content: dict) -> str:
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)
    target = Path(settings.storage_path) / f"resume_{uuid4()}.pdf"
    c = canvas.Canvas(str(target), pagesize=letter)
    y = 760
    c.drawString(40, y, content.get('basics', {}).get('full_name', 'Candidate'))
    y -= 20
    c.drawString(40, y, content.get('summary', '')[:110])
    y -= 30
    c.drawString(40, y, 'Skills: ' + ', '.join(content.get('skills', [])))
    c.save()
    return str(target)
