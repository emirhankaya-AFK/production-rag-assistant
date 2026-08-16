from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


class PDFValidationError(ValueError):
    """Raised when an uploaded PDF cannot be safely processed."""


@dataclass(frozen=True, slots=True)
class PDFPage:
    number: int
    text: str


def extract_pdf_pages(data: bytes) -> list[PDFPage]:
    if not data.startswith(b"%PDF"):
        raise PDFValidationError("The uploaded file is not a valid PDF")

    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:
        raise PDFValidationError("The PDF could not be opened") from exc

    if reader.is_encrypted:
        raise PDFValidationError("Encrypted PDFs are not supported")

    pages: list[PDFPage] = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            raise PDFValidationError(f"Could not extract text from page {number}") from exc
        normalized = " ".join(text.split())
        if normalized:
            pages.append(PDFPage(number=number, text=normalized))

    if not pages:
        raise PDFValidationError(
            "No selectable text was found. Scanned PDFs require an OCR pipeline."
        )
    return pages
