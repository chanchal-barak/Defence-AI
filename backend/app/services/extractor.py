from pathlib import Path
import re

import fitz

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def clean_text(text: str) -> str:
    """Normalize extracted document text."""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Fix spaces before punctuation
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    return text.strip()


def extract_from_txt(path: str) -> tuple[str, dict]:
    text = Path(path).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    text = clean_text(text)

    return text, {
        "method": "plain_text",
        "pages": 1,
        "ocr_used": False,
        "character_count": len(text),
        "word_count": len(text.split()),
    }


def extract_from_pdf(path: str) -> tuple[str, dict]:

    pages = []
    total_pages = 0

    # -----------------------------------
    # Method 1: PyMuPDF
    # -----------------------------------

    document = fitz.open(path)
    total_pages = len(document)

    for page_number, page in enumerate(document, start=1):

        page_text = page.get_text("text")

        pages.append({
            "page": page_number,
            "text": page_text
        })

    document.close()

    text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"].strip()
    )

    text = clean_text(text)

    # -----------------------------------
    # Method 2: pdfplumber fallback
    # -----------------------------------

    if len(text) < 50 and pdfplumber:

        try:

            plumber_pages = []

            with pdfplumber.open(path) as pdf:

                for page_number, page in enumerate(
                    pdf.pages,
                    start=1
                ):

                    page_text = page.extract_text() or ""

                    plumber_pages.append({
                        "page": page_number,
                        "text": page_text
                    })

            plumber_text = "\n\n".join(
                page["text"]
                for page in plumber_pages
                if page["text"].strip()
            )

            plumber_text = clean_text(plumber_text)

            if len(plumber_text) > len(text):
                text = plumber_text

        except Exception:
            pass

    return text, {
        "method": "pymupdf",
        "pages": total_pages,
        "ocr_used": False,
        "character_count": len(text),
        "word_count": len(text.split()),
        "extraction_quality": (
            "good" if len(text) >= 100
            else "low"
        )
    }


def extract_text(path: str, suffix: str):

    suffix = suffix.lower()

    if suffix == ".txt":
        return extract_from_txt(path)

    if suffix == ".pdf":
        return extract_from_pdf(path)

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )