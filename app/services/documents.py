from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import Document, DocumentChunk
from app.services.chunking import chunk_pages
from app.services.embeddings import build_embedding_provider
from app.services.pdf_parser import extract_pdf_pages


async def ingest_pdf(
    session: AsyncSession,
    settings: Settings,
    *,
    filename: str,
    content_type: str,
    data: bytes,
) -> Document:
    safe_filename = Path(filename).name[:255] or "document.pdf"
    pages = extract_pdf_pages(data)
    chunks = chunk_pages(
        pages,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    if not chunks:
        raise ValueError("The PDF did not produce any indexable text chunks")

    provider = build_embedding_provider(settings)
    embeddings: list[list[float]] = []
    for start in range(0, len(chunks), 64):
        batch = chunks[start : start + 64]
        embeddings.extend(await provider.embed([chunk.content for chunk in batch]))

    document = Document(
        filename=safe_filename,
        content_type=content_type or "application/pdf",
        page_count=len(pages),
        chunk_count=len(chunks),
        status="ready",
    )
    session.add(document)
    await session.flush()

    session.add_all(
        [
            DocumentChunk(
                document_id=document.id,
                page_number=chunk.page_number,
                chunk_index=chunk.index,
                content=chunk.content,
                embedding=embedding,
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
    )
    await session.commit()
    await session.refresh(document)
    return document
