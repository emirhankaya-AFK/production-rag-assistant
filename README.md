# Production RAG Assistant

[English](#english) | [Türkçe](#türkçe) | [Deutsch](#deutsch)

## English

### Purpose
A source‑grounded PDF question‑answering application built with FastAPI, PostgreSQL, pgvector, Docker, and a small responsive web interface. It supports a zero‑key local demo mode and an OpenAI‑backed mode for production‑quality embeddings and answers.

### Verified Features
- Async REST API design with FastAPI and SQLAlchemy  
- PostgreSQL persistence with pgvector cosine similarity search  
- Validated PDF upload, page‑aware chunking, and batched embeddings  
- Answers that include document, page, relevance score, and excerpt citations  
- Provider abstraction: deterministic local mode (no API key) or OpenAI API  
- Docker Compose startup with database health checks  
- Error handling, upload limits, typed schemas, and safe filename handling  
- Unit and API tests, Ruff linting, and GitHub Actions CI  
- English and Turkish documentation  

### Stack
- **Language**: Python  
- **Web framework**: FastAPI (with Uvicorn)  
- **ORM**: SQLAlchemy  
- **Database**: PostgreSQL + pgvector extension  
- **Containerization**: Docker & Docker Compose  
- **Code quality**: Ruff  
- **Testing**: pytest  
- **CI**: GitHub Actions  

### Setup & Usage (Docker)
1. Copy the example environment file:  
   ```bash
   cp .env.example .env
   ```
2. Build and start the services:  
   ```bash
   docker compose up --build
   ```
3. Open the application:  
   - UI: `http://localhost:8000`  
   - Swagger UI: `http://localhost:8000/docs`  
   - Health endpoint: `http://localhost:8000/health`  

The default `LLM_PROVIDER=local` mode works without an API key and uses deterministic hashed embeddings for easy local testing.

### OpenAI Mode
Set the following in `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_CHAT_MODEL=gpt-5-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```
If you change embedding models or dimensions after indexing, recreate the database volume and re‑index documents to keep vector compatibility.

### Local Development (without Docker)
```bash
# Start PostgreSQL only
docker compose up -d db

# Python environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```
When running outside Docker, change the database host in `.env` from `db` to `localhost` and use port `5433`.

### Testing
```bash
ruff check .
pytest -q
```
Both commands are run by GitHub Actions on every pull request and push to `main`.

### Limitations
- Scanned PDFs require OCR and are rejected with a clear validation error.  
- Authentication and tenant isolation are not implemented in this vertical slice.  
- Database tables are created at application startup; Alembic migrations are planned for future hosted deployment.  
- The local mode is intended for pipeline testing, not for high‑quality semantic retrieval.  

### License
See the [LICENSE](LICENSE) file for details.

## Türkçe
See [README_TR.md](README_TR.md) for the Turkish version.

## Deutsch
See [README_DE.md](README_DE.md) for the German version.
