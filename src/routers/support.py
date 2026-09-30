from fastapi import APIRouter

from src.schemas.support import SupportRequest, SupportResponse
from src.services.llm import generate_support_answer
from src.services.rag import search_knowledge_base

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/ask", response_model=SupportResponse)
async def ask_support(payload: SupportRequest):
    question = payload.question

    context = await search_knowledge_base(question)

    answer = await generate_support_answer(question, context)

    return SupportResponse(answer=answer)
