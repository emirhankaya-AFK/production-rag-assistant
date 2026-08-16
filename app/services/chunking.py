from dataclasses import dataclass

from app.services.pdf_parser import PDFPage


@dataclass(frozen=True, slots=True)
class TextChunk:
    page_number: int
    index: int
    content: str


def chunk_pages(
    pages: list[PDFPage], *, chunk_size: int = 1_200, overlap: int = 180
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks: list[TextChunk] = []
    chunk_index = 0
    step = chunk_size - overlap

    for page in pages:
        start = 0
        while start < len(page.text):
            end = min(start + chunk_size, len(page.text))
            if end < len(page.text):
                boundary = page.text.rfind(" ", start + chunk_size // 2, end)
                if boundary > start:
                    end = boundary

            content = page.text[start:end].strip()
            if content:
                chunks.append(
                    TextChunk(page_number=page.number, index=chunk_index, content=content)
                )
                chunk_index += 1

            if end >= len(page.text):
                break
            next_start = end - overlap
            start = next_start if next_start > start else start + step

    return chunks
