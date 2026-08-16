import re
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from app.core.config import Settings

STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "how",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "bir",
    "bu",
    "için",
    "ile",
    "nedir",
    "nasıl",
}


class AnswerProvider(ABC):
    name: str

    @abstractmethod
    async def answer(self, question: str, contexts: list[str]) -> str:
        raise NotImplementedError


class LocalAnswerProvider(AnswerProvider):
    name = "local"

    async def answer(self, question: str, contexts: list[str]) -> str:
        query_terms = {
            term.lower()
            for term in re.findall(r"\w+", question)
            if len(term) > 2 and term.lower() not in STOPWORDS
        }
        candidates: list[tuple[int, str, int]] = []
        for source_number, context in enumerate(contexts, start=1):
            for sentence in re.split(r"(?<=[.!?])\s+", context):
                score = sum(term in sentence.lower() for term in query_terms)
                if score:
                    candidates.append((score, sentence.strip(), source_number))

        if not candidates:
            return (
                "I could not find enough information in the uploaded documents "
                "to answer that question."
            )

        candidates.sort(key=lambda item: item[0], reverse=True)
        selected = candidates[:3]
        return " ".join(f"{sentence} [{source}]" for _, sentence, source in selected)


class OpenAIAnswerProvider(AnswerProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_chat_model

    async def answer(self, question: str, contexts: list[str]) -> str:
        context_block = "\n\n".join(
            f"SOURCE [{number}]\n{context}" for number, context in enumerate(contexts, start=1)
        )
        response = await self.client.responses.create(
            model=self.model,
            instructions=(
                "Answer only from the supplied sources. Cite every factual claim with [n]. "
                "If the sources do not contain the answer, say so clearly. Do not invent citations."
            ),
            input=f"Question: {question}\n\n{context_block}",
        )
        return response.output_text.strip()


def build_answer_provider(settings: Settings) -> AnswerProvider:
    if settings.llm_provider == "openai":
        return OpenAIAnswerProvider(settings)
    return LocalAnswerProvider()
