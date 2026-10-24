import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
)

# Максимальный вес посылки из правил службы доставки (knowledge_base.txt)
MAX_PARCEL_WEIGHT_KG = 31.5


class ParcelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    weight: float = Field(gt=0, le=MAX_PARCEL_WEIGHT_KG)
    content_value: Decimal = Field(gt=0)
    type_id: int = Field(gt=0)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Название посылки не может быть пустым")
        return cleaned


class ParcelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    weight: float
    content_value: Decimal
    type_id: int
    type_name: str | None = None
    carrier_name: str | None = None
    delivery_cost: Decimal | None = None
    created_at: datetime

    # Фронтенду не нужно парсить строку "Не рассчитано":
    # стоимость приходит как null, а статус отдельным булевым полем
    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_calculated(self) -> bool:
        return self.delivery_cost is not None

    @field_serializer("content_value", "delivery_cost")
    def serialize_money(self, value: Decimal | None) -> float | None:
        if value is None:
            return None
        return float(value)


class ParcelPage(BaseModel):
    items: list[ParcelResponse]
    total: int
    limit: int
    offset: int
