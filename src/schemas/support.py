from typing import Literal

from pydantic import BaseModel, Field

# Сколько предыдущих сообщений диалога учитывать
MAX_HISTORY_MESSAGES = 20


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"] = Field(description="Автор сообщения")
    content: str = Field(
        min_length=1,
        max_length=4000,
        description="Текст сообщения",
    )


class SupportRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Вопрос пользователя к службе поддержки",
        examples=["Можно ли отправить ноутбук?"],
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=MAX_HISTORY_MESSAGES,
        description="Предыдущие сообщения диалога — нужны, чтобы ассистент "
        "понимал продолжение разговора",
    )


class SupportResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Сгенерированный ответ ИИ-ассистента",
    )
