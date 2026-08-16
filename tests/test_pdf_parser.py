import pytest

from app.services.pdf_parser import PDFValidationError, extract_pdf_pages


def test_parser_rejects_non_pdf_content() -> None:
    with pytest.raises(PDFValidationError, match="valid PDF"):
        extract_pdf_pages(b"not-a-pdf")
