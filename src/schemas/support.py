from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    question: str = Field(
        ...,
        description="Вопрос пользователя к службе поддержки",
        examples=["Можно ли отправить ноутбук?"],
    )


class SupportResponse(BaseModel):
    answer: str = Field(
        ...,
        description="Сгенерированный ответ ИИ-ассистента",
    )
