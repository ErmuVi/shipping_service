from pydantic import BaseModel


class ParcelTypeRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
