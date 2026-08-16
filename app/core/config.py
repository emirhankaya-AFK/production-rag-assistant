from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Production RAG Assistant"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"
    llm_provider: str = "local"
    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-5-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    max_upload_mb: int = 15
    chunk_size: int = 1_200
    chunk_overlap: int = 180
    retrieval_top_k: int = Field(default=5, ge=1, le=12)
    allowed_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]

    @field_validator("llm_provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"local", "openai"}:
            raise ValueError("LLM_PROVIDER must be 'local' or 'openai'")
        return normalized

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, value: int, info) -> int:
        chunk_size = info.data.get("chunk_size", 1_200)
        if value < 0 or value >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
