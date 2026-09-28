import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class ParcelCreate(BaseModel):
    name: str
    weight: float = Field(gt=0)
    content_value: Decimal = Field(gt=0)
    type_id: int


class ParcelResponse(BaseModel):
    id: uuid.UUID
    name: str
    weight: float
    content_value: Decimal
    type_id: int
    type_name: str | None = None
    delivery_cost: Decimal | str | None

    model_config = {"from_attributes": True}

    @field_serializer("delivery_cost")
    def serialize_delivery_cost(self, v: Decimal | None) -> Decimal | str:
        if v is None:
            return "Не рассчитано"
        return v
