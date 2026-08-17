# Production RAG Assistant

[English](README.md) | [Türkçe](README_TR.md) | [Deutsch](README_DE.md)

Quellenbasierter PDF-Frage-Antwort-Assistent mit FastAPI, PostgreSQL, pgvector, Docker und Weboberfläche.

## Funktionen
- PDF-Upload, seitenbewusstes Chunking und Embeddings
- Cosine-Suche in pgvector
- Antworten mit Dokument-, Seiten- und Auszug-Zitaten
- Lokaler Demo-Modus ohne API-Key sowie OpenAI-Adapter
- Tests, Fehlerbehandlung und GitHub Actions

![Architektur](docs/demo.svg)

## Start

    cp .env.example .env
    docker compose up --build

Anwendung: http://localhost:8000, Swagger: /docs.

Die Evaluation sollte Top-k-Retrieval, Citation Coverage, Grounding und Upload/Retrieval/Answer-Latenz messen.

