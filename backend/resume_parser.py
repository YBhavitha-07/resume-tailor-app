import os
import re
from io import BytesIO

import fitz
from docx import Document

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

RESUME_SECTION_PATTERNS = {
    "summary": ["summary", "profile", "about me", "professional summary", "overview"],
    "experience": ["work experience", "professional experience", "experience", "employment history"],
    "skills": ["skills", "technical skills", "core competencies", "strengths"],
    "education": ["education", "academic background", "qualification"],
    "projects": ["projects", "portfolio", "selected projects"],
    "certifications": ["certifications", "licenses", "training", "awards"],
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\r\n+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        document = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for page in document:
            pages.append(page.get_text())
        document.close()
        return normalize_text("\n".join(pages))
    except Exception as exc:
        raise ValueError("Unable to read PDF content. Please verify the file is not corrupted.") from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        document = Document(BytesIO(file_bytes))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return normalize_text("\n".join(paragraphs))
    except Exception as exc:
        raise ValueError("Unable to read DOCX content. Please verify the file is valid.") from exc


def detect_resume_sections(text: str) -> list[str]:
    cleaned = normalize_text(text).lower()
    if not cleaned:
        return []

    found_sections: list[str] = []
    for section_name, patterns in RESUME_SECTION_PATTERNS.items():
        if any(pattern in cleaned for pattern in patterns):
            found_sections.append(section_name.title())

    if not found_sections:
        return ["Unstructured"]

    return found_sections


def extract_resume_text(file_name: str, file_bytes: bytes) -> str:
    extension = os.path.splitext(file_name)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX resume files are supported.")

    if extension == ".pdf":
        return extract_text_from_pdf(file_bytes)

    return extract_text_from_docx(file_bytes)
