import pytest

from app.services.chunking import chunk_pages
from app.services.pdf_parser import PDFPage


def test_chunking_preserves_page_numbers_and_overlap() -> None:
    text = " ".join(f"word-{number}" for number in range(100))
    chunks = chunk_pages([PDFPage(number=7, text=text)], chunk_size=120, overlap=20)

    assert len(chunks) > 1
    assert all(chunk.page_number == 7 for chunk in chunks)
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [(0, 0), (100, -1), (100, 100), (100, 101)],
)
def test_chunking_rejects_invalid_configuration(chunk_size: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        chunk_pages([PDFPage(number=1, text="hello")], chunk_size=chunk_size, overlap=overlap)
