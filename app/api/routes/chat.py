from fastapi import APIRouter

from app.api.dependencies import SessionDep, SettingsDep
from app.schemas import AnswerResponse, QuestionRequest
from app.services.rag import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> AnswerResponse:
    return await answer_question(
        session,
        settings,
        question=request.question,
        document_ids=request.document_ids,
        top_k=request.top_k,
    )
