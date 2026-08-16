from app.services.llm import LocalAnswerProvider


async def test_local_answer_uses_relevant_sentence_and_citation() -> None:
    provider = LocalAnswerProvider()
    answer = await provider.answer(
        "Which database stores the vectors?",
        [
            "The interface is served by FastAPI.",
            "PostgreSQL stores document chunks and vector embeddings.",
        ],
    )

    assert "PostgreSQL" in answer
    assert "[2]" in answer


async def test_local_answer_is_honest_when_context_does_not_match() -> None:
    provider = LocalAnswerProvider()
    answer = await provider.answer("What is the deployment region?", ["The document is a PDF."])

    assert "could not find enough information" in answer
