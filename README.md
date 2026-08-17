# Production RAG Assistant

[English](README.md) | [Türkçe](README_TR.md) | [Deutsch](README_DE.md)

A source-grounded PDF question-answering application built with FastAPI, PostgreSQL, pgvector, Docker, and a small responsive web interface. It supports a zero-key local demo mode and an OpenAI-backed mode for production-quality embeddings and answers.

## What it demonstrates

- Async REST API design with FastAPI and SQLAlchemy
- PostgreSQL persistence and pgvector cosine similarity search
- Validated PDF upload, page-aware chunking, and batched embeddings
- Answers with document, page, relevance score, and excerpt citations
- Provider abstraction: deterministic local mode or OpenAI API
- Docker Compose startup with database health checks
- Error handling, upload limits, typed schemas, and safe filename handling
- Unit/API tests, Ruff checks, and GitHub Actions CI
- English and Turkish documentation

## Architecture

```text
Browser UI
   │
   ├── POST /api/v1/documents ──> PDF parser ──> chunker ──> embeddings
   │                                                     │
   │                                                     ▼
   │                                              PostgreSQL + pgvector
   │                                                     ▲
   └── POST /api/v1/chat/ask ──> question embedding ──> cosine search
                                                         │
                                                         ▼
                                               grounded answer + citations
```

## Evaluation checklist

- Retrieval: verify that the expected page appears in the top-k results.
- Grounding: reject answers without supporting excerpts.
- Regression set: keep representative PDFs and questions under tests/evals.
- Operations: track upload latency, retrieval latency, answer latency and citation coverage.

## Quick start with Docker

Requirements: Docker Desktop with Compose.

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Application: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`

The default `LLM_PROVIDER=local` mode works without an API key. It uses deterministic hashed embeddings and an extractive answer generator, making the complete upload/retrieval/citation pipeline easy to test locally.

## OpenAI mode

Set these values in `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_CHAT_MODEL=gpt-5-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

If you change embedding models or dimensions after indexing documents, recreate the database volume and re-index the documents so stored vectors remain compatible.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health |
| `POST` | `/api/v1/documents` | Upload and index a PDF |
| `GET` | `/api/v1/documents` | List indexed documents |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document and its chunks |
| `POST` | `/api/v1/chat/ask` | Ask a grounded question |

Example question request:

```json
{
  "question": "What are the main deployment risks?",
  "document_ids": null,
  "top_k": 5
}
```

## Local development

Start PostgreSQL:

```bash
docker compose up -d db
```

Create a virtual environment and run the API:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

When the API runs outside Docker, change the database hostname in `.env` from `db` to `localhost` and use port `5433`.

## Quality checks

```bash
ruff check .
pytest -q
```

CI runs both commands for every pull request and push to `main`.

## Current limitations

- Scanned PDFs require OCR and are rejected with a clear validation error.
- Authentication and tenant isolation are not part of this first vertical slice.
- Database tables are bootstrapped at application startup; Alembic migrations are planned before hosted deployment.
- Local mode is for pipeline testing, not high-quality semantic retrieval.

## Production roadmap

1. Add Alembic migrations and background ingestion jobs.
2. Add JWT authentication, workspaces, and document-level authorization.
3. Add OCR, hybrid full-text/vector search, reranking, and evaluation datasets.
4. Add rate limiting, structured observability, and cloud object storage.
5. Deploy to a managed PostgreSQL/pgvector service and a container platform.
