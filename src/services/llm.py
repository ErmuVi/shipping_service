import httpx

from src.config import settings


async def generate_support_answer(question: str, context: str) -> str:
    """Отправляет контекст из базы знаний и вопрос в бесплатную модель

    LiquidAI.
    """

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "Ты — профессиональный ассистент службы поддержки службы" 
        "доставки Shipping Service. "
        "Ответь на вопрос пользователя, используя ТОЛЬКО "
        "предоставленный ниже контекст (правила). "
        "Если в контексте нет ответа на этот вопрос, вежливо ответь: "
        "'К сожалению, у меня нет информации по данному вопросу'. "
        "Не придумывай ничего от себя.\n\n"
        f"Контекст (Правила компании):\n{context}"
    )

    payload = {
        "model": "liquid/lfm-2.5-2.6b:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=30.0)

    if response.status_code != 200:
        print(
            "!!! ОШИБКА OPENROUTER !!! "
            f"Статус: {response.status_code}, "
            f"Текст: {response.text}"
        )
        return "Служба поддержки временно недоступна. Попробуйте позже."

    data = response.json()
    return data["choices"][0]["message"]["content"]
