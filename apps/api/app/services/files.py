import hashlib
from pathlib import Path
from uuid import uuid4

from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from app.core.config import settings

ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_UPLOAD_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_resume_upload(filename: str, mime_type: str | None, size_bytes: int) -> None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError("Unsupported file extension")
    if mime_type and mime_type not in ALLOWED_UPLOAD_MIME_TYPES:
        raise ValueError("Unsupported file type")
    if size_bytes > MAX_UPLOAD_BYTES:
        raise ValueError("Resume file exceeds the 5MB limit")


def save_upload(filename: str, content: bytes) -> str:
    ensure_directory(settings.storage_path)
    safe_name = Path(filename).name
    target = Path(settings.storage_path) / f"{uuid4()}_{safe_name}"
    target.write_bytes(content)
    return str(target)


def render_resume_pdf(content: dict) -> str:
    ensure_directory(settings.storage_path)
    target = Path(settings.storage_path) / f"resume_{uuid4()}.pdf"
    c = canvas.Canvas(str(target), pagesize=letter)
    y = 770
    margin = 48
    width = 520

    def draw_block(title: str, body_lines: list[str]) -> None:
        nonlocal y
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, title)
        y -= 16
        c.setFont("Helvetica", 10)
        for line in body_lines:
            for wrapped in simpleSplit(line, "Helvetica", 10, width):
                c.drawString(margin, y, wrapped)
                y -= 14
        y -= 8

    basics = content.get("basics", {})
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, basics.get("full_name", "Candidate"))
    y -= 20
    c.setFont("Helvetica", 10)
    contact_parts = [basics.get("email", ""), basics.get("phone", ""), basics.get("location", "")]
    c.drawString(margin, y, " | ".join(part for part in contact_parts if part))
    y -= 24
    draw_block("Summary", [content.get("summary", "")])
    draw_block("Skills", [", ".join(content.get("skills", []))])
    draw_block(
        "Experience",
        [
            f"{item.get('title', '')} at {item.get('company', '')}".strip()
            for item in content.get("experience", [])
        ]
        or ["No experience entries yet."],
    )
    c.save()
    return str(target)
