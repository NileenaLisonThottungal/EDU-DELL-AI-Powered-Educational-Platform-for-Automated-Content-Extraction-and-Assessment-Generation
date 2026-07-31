"""PDF text extraction (Section 3.2.1 of the Abstract: PyPDF2 / pdfminer)."""
import io

import pdfplumber
from PyPDF2 import PdfReader


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from a PDF, preferring pdfplumber and falling back to PyPDF2
    for pages/files pdfplumber fails to parse (scanned or malformed layouts)."""
    pages = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text)
    except Exception:
        pages = []

    if not any(p.strip() for p in pages):
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]

    return "\n".join(pages)
