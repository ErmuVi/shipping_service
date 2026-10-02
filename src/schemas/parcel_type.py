from pydantic import BaseModel

# Правила валидации, для запросов к этой таблице
class ParcelTypeRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
