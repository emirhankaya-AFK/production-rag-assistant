import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    content_type: str
    page_count: int
    chunk_count: int
    status: str
    created_at: datetime


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    document_ids: list[uuid.UUID] | None = None
    top_k: int | None = Field(default=None, ge=1, le=12)


class Citation(BaseModel):
    number: int
    document_id: uuid.UUID
    filename: str
    page: int
    chunk_id: uuid.UUID
    score: float
    excerpt: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    provider: str
