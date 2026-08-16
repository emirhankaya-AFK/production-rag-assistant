import math

from app.services.embeddings import LocalEmbeddingProvider


async def test_local_embeddings_are_deterministic_and_normalized() -> None:
    provider = LocalEmbeddingProvider(dimensions=64)
    first, second = await provider.embed(["FastAPI PostgreSQL", "FastAPI PostgreSQL"])

    assert first == second
    assert math.isclose(math.sqrt(sum(value * value for value in first)), 1.0)


async def test_local_embeddings_change_with_content() -> None:
    provider = LocalEmbeddingProvider(dimensions=64)
    first, second = await provider.embed(["database migrations", "computer vision"])

    assert first != second
