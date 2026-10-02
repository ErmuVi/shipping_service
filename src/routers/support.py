from fastapi import APIRouter

from src.schemas.support import SupportRequest, SupportResponse
from src.services.llm import generate_support_answer
from src.services.rag import search_knowledge_base

router = APIRouter(prefix="/support", tags=["Support"])

#Эндпоинт отвечающий за rag систему
#Как я понимаю эту систему - мы берем вопрос пользователя, он превращается в эмбендинг(я еще не совсем понимаю что это),
#и отпровляется в векторную бд(квадрант в нашем случае), там математически находятся похожие обзацы(поделены нами на чанки заранее в другой функц.),
#и потом этот обзац из наших правил и вопрос пользователя отправляются в llm в контекстом(промтом), и от туда мы уже берем ответ.
@router.post("/ask", response_model=SupportResponse)
async def ask_support(payload: SupportRequest):
    question = payload.question

    context = await search_knowledge_base(question)

    answer = await generate_support_answer(question, context)

    return SupportResponse(answer=answer)
