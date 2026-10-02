from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.parcel import ParcelCreate


def test_parcel_create_valid_data():
    # Проверям что схема работает)
    data = {
        "name": "Кроссовки",
        "weight": 1.5,
        "content_value": Decimal("120.50"),
        "type_id": 1,
    }
    parcel = ParcelCreate(**data)
    assert parcel.name == "Кроссовки"
    assert parcel.weight == 1.5
    assert parcel.content_value == Decimal("120.50")


# Проверям правильная ли валидация веса, ноль и отрицательные числа
@pytest.mark.parametrize(
    "weight, content_value",
    [
        (-0.5, Decimal("10.00")),  # Отрицательный вес
        (0.0, Decimal("10.00")),  # Нулевой вес
        (1.5, Decimal("-50.00")),  # Отрицательная стоимость
    ],
)
# Одна функция на некоректные цифры
def test_parcel_create_invalid_data(weight, content_value):
    with pytest.raises(ValidationError):
        ParcelCreate(name="Тест", weight=weight, content_value=content_value, type_id=1)
