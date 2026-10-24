from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.parcel import MAX_PARCEL_WEIGHT_KG, ParcelCreate


def test_parcel_create_valid_data():
    # Проверяем что схема работает)
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


# Проверяем правильная ли валидация веса: ноль, отрицательные числа
# и превышение лимита из правил доставки
@pytest.mark.parametrize(
    "weight, content_value",
    [
        (-0.5, Decimal("10.00")),  # Отрицательный вес
        (0.0, Decimal("10.00")),  # Нулевой вес
        (1.5, Decimal("-50.00")),  # Отрицательная стоимость
        (MAX_PARCEL_WEIGHT_KG + 0.1, Decimal("10.00")),  # Тяжелее лимита
    ],
)
# Одна функция на некорректные цифры
def test_parcel_create_invalid_data(weight, content_value):
    with pytest.raises(ValidationError):
        ParcelCreate(name="Тест", weight=weight, content_value=content_value, type_id=1)


def test_parcel_create_max_weight_is_allowed():
    parcel = ParcelCreate(
        name="На пределе",
        weight=MAX_PARCEL_WEIGHT_KG,
        content_value=Decimal("10.00"),
        type_id=1,
    )
    assert parcel.weight == MAX_PARCEL_WEIGHT_KG


@pytest.mark.parametrize("name", ["", "   "])
def test_parcel_create_empty_name_is_rejected(name):
    with pytest.raises(ValidationError):
        ParcelCreate(
            name=name,
            weight=1.0,
            content_value=Decimal("10.00"),
            type_id=1,
        )


def test_parcel_create_strips_name():
    parcel = ParcelCreate(
        name="  Кроссовки  ",
        weight=1.0,
        content_value=Decimal("10.00"),
        type_id=1,
    )
    assert parcel.name == "Кроссовки"
