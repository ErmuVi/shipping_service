from fastapi import APIRouter

from src.schemas.support import SupportRequest, SupportResponse
from src.services.llm import generate_support_answer
from src.services.rag import search_knowledge_base

router = APIRouter(prefix="/support", tags=["Support"])

# Эндпоинт RAG-системы:
# 1. Вопрос пользователя превращается в эмбеддинг.
# 2. В векторной БД (Qdrant) находятся похожие чанки правил.
# 3. Чанки и вопрос отправляются в LLM как контекст, ответ возвращается клиенту.
@router.post("/ask", response_model=SupportResponse)
async def ask_support(payload: SupportRequest):
    question = payload.question

    context = await search_knowledge_base(question)

    answer = await generate_support_answer(
        question,
        context,
        history=[message.model_dump() for message in payload.history],
    )

    return SupportResponse(answer=answer)
