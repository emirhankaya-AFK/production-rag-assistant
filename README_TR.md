# Production RAG Assistant

[English](README.md) | [Türkçe](README_TR.md) | [Deutsch](README_DE.md)

FastAPI, PostgreSQL, pgvector, Docker ve basit bir web arayüzüyle geliştirilmiş; PDF dosyalarına kaynak göstererek soru sorulmasını sağlayan RAG uygulamasıdır. API anahtarı gerektirmeyen yerel demo modu ve OpenAI destekli gerçek kullanım modu bulunur.

## Gösterdiği yetkinlikler

- FastAPI ve SQLAlchemy ile asenkron REST API
- PostgreSQL kalıcı veri katmanı ve pgvector benzerlik araması
- PDF doğrulama, sayfa bazlı parçalama ve toplu embedding üretimi
- Dosya adı, sayfa, benzerlik puanı ve alıntı içeren kaynaklar
- Yerel ve OpenAI sağlayıcılarını ayıran temiz servis mimarisi
- Sağlık kontrolü kullanan Docker Compose kurulumu
- Dosya boyutu sınırı, hata yönetimi ve tip güvenli şemalar
- Pytest, Ruff ve GitHub Actions CI

## Docker ile çalıştırma

```bash
copy .env.example .env
docker compose up --build
```

Ardından şu adresleri açın:

- Uygulama: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Sağlık kontrolü: `http://localhost:8000/health`

Varsayılan `LLM_PROVIDER=local` modu API anahtarı olmadan çalışır. PDF yükleme, indeksleme, arama ve kaynak gösterme akışının tamamı bu modda denenebilir.

## OpenAI modu

`.env` dosyasını düzenleyin:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=kendi_anahtariniz
OPENAI_CHAT_MODEL=gpt-5-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

Embedding modeli veya boyutu değiştirildiğinde mevcut vektörler uyumsuz olacağından veritabanı yeniden oluşturulmalı ve belgeler yeniden indekslenmelidir.

## API uçları

| Metot | Adres | Amaç |
|---|---|---|
| `GET` | `/health` | Servis sağlık durumu |
| `POST` | `/api/v1/documents` | PDF yükleme ve indeksleme |
| `GET` | `/api/v1/documents` | Belgeleri listeleme |
| `DELETE` | `/api/v1/documents/{id}` | Belgeyi ve parçalarını silme |
| `POST` | `/api/v1/chat/ask` | Kaynaklı soru sorma |

## Test ve kod kalitesi

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
```

## Mevcut sınırlar ve sonraki adımlar

Değerlendirme checklist'i: top-k sonuçlarda beklenen sayfanın bulunması, desteklenmeyen cevapların reddi, temsili PDF/soru regresyon seti ve upload/retrieval/answer latency ile citation coverage metriklerinin izlenmesi.

- Taranmış PDF dosyaları için OCR eklenecek.
- Alembic migration sistemi ve arka plan iş kuyruğu eklenecek.
- JWT kimlik doğrulama ve çoklu çalışma alanı desteği eklenecek.
- Hibrit arama, reranker ve RAG değerlendirme veri seti hazırlanacak.
- Uygulama yönetilen PostgreSQL ve container hizmetine dağıtılacak.
