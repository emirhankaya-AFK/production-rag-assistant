import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import Document, DocumentChunk
from app.schemas import AnswerResponse, Citation
from app.services.embeddings import build_embedding_provider
from app.services.llm import build_answer_provider


@dataclass(slots=True)
class RetrievedChunk:
    chunk: DocumentChunk
    filename: str
    distance: float


async def retrieve_chunks(
    session: AsyncSession,
    query_embedding: list[float],
    *,
    document_ids: list[uuid.UUID] | None,
    top_k: int,
) -> list[RetrievedChunk]:
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
    statement = (
        select(DocumentChunk, Document.filename, distance.label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.status == "ready")
        .order_by(distance)
        .limit(top_k)
    )
    if document_ids:
        statement = statement.where(DocumentChunk.document_id.in_(document_ids))

    rows = (await session.execute(statement)).all()
    return [RetrievedChunk(chunk=row[0], filename=row[1], distance=float(row[2])) for row in rows]


async def answer_question(
    session: AsyncSession,
    settings: Settings,
    *,
    question: str,
    document_ids: list[uuid.UUID] | None,
    top_k: int | None,
) -> AnswerResponse:
    embedding_provider = build_embedding_provider(settings)
    answer_provider = build_answer_provider(settings)
    query_embedding = (await embedding_provider.embed([question]))[0]
    matches = await retrieve_chunks(
        session,
        query_embedding,
        document_ids=document_ids,
        top_k=top_k or settings.retrieval_top_k,
    )

    if not matches:
        return AnswerResponse(
            answer="No indexed document passages were found.",
            citations=[],
            provider=answer_provider.name,
        )

    contexts = [match.chunk.content for match in matches]
    answer = await answer_provider.answer(question, contexts)
    citations = [
        Citation(
            number=index,
            document_id=match.chunk.document_id,
            filename=match.filename,
            page=match.chunk.page_number,
            chunk_id=match.chunk.id,
            score=round(max(0.0, 1.0 - match.distance), 4),
            excerpt=match.chunk.content[:280],
        )
        for index, match in enumerate(matches, start=1)
    ]
    return AnswerResponse(answer=answer, citations=citations, provider=answer_provider.name)
