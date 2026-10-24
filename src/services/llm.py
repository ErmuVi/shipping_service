import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "liquid/lfm-2.5-2.6b:free"

SYSTEM_PROMPT = (
    "Ты — дружелюбный ассистент службы международной доставки Shipping Service. "
    "Ты общаешься как живой собеседник: можешь отвечать на любые вопросы, "
    "а не только про посылки, поддерживать светскую беседу, шутить, "
    "объяснять и давать советы.\n\n"
    "Правила компании (таможня, ограничения по весу, запрещённые товары, пошлины) "
    "бери ТОЛЬКО из блока «Контекст» ниже. "
    "Если пользователь спрашивает про правила Shipping Service, а в контексте "
    "ответа нет — честно скажи, что у тебя нет такой информации, и предложи "
    "уточнить у оператора. Не выдумывай факты о компании, тарифах и сроках.\n\n"
    "На общие вопросы (погода, технологии, советы, болтовня) отвечай из своих "
    "знаний — контекст для них не нужен.\n\n"
    "Отвечай на языке пользователя, естественно и по делу. "
    "Не начинай каждый ответ с приветствия и не повторяй правила, "
    "если о них не спрашивали."
)


def build_system_prompt(context: str) -> str:
    context_block = context.strip() or "релевантных фрагментов правил не найдено"
    return f"{SYSTEM_PROMPT}\n\nКонтекст (правила компании):\n{context_block}"


async def generate_support_answer(
    question: str,
    context: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    """Отвечает на вопрос с учетом истории диалога.

    Контекст из базы знаний используется только как справка о правилах
    компании, поэтому ассистент может поговорить и на отвлеченные темы.
    """
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    messages: list[dict[str, str]] = [
        {"role": "system", "content": build_system_prompt(context)}
    ]

    for message in history or []:
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": question})

    payload = {"model": MODEL_NAME, "messages": messages}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_URL, headers=headers, json=payload, timeout=30.0
            )
    except httpx.HTTPError as exc:
        logger.error("Не удалось связаться с OpenRouter: %s", exc)
        return "Служба поддержки временно недоступна. Попробуйте позже."

    if response.status_code != 200:
        logger.error(
            "Ошибка OpenRouter. Статус: %s, текст: %s",
            response.status_code,
            response.text,
        )
        return "Служба поддержки временно недоступна. Попробуйте позже."

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        logger.error("Неожиданный ответ OpenRouter: %s (%s)", response.text, exc)
        return "Не удалось подготовить ответ. Попробуйте переформулировать вопрос."
