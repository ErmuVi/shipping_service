from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

import pytest

from src.models import Parcel
from src.models.parcel_type import ParcelType


async def _create_type(session) -> ParcelType:
    test_type = ParcelType(id=1, name="Одежда")
    session.add(test_type)
    await session.commit()
    return test_type


@pytest.mark.asyncio
async def test_create_and_get_parcel_flow(ac, session):
    """1. Сквозной тест создания посылки через API и её проверки в списке."""
    await _create_type(session)

    payload = {
        "name": "Планшет",
        "weight": 0.8,
        "content_value": "350.00",
        "type_id": 1,
    }
    response = await ac.post("/api/parcels", json=payload)
    assert response.status_code == 201

    created = response.json()
    assert created["name"] == "Планшет"
    assert created["type_name"] == "Одежда"
    assert created["is_calculated"] is False
    assert created["delivery_cost"] is None
    assert created["created_at"] is not None

    # Проверяем её наличие в списке через GET-запрос
    get_response = await ac.get("/api/parcels")
    assert get_response.status_code == 200

    page = get_response.json()
    assert page["total"] == 1
    assert page["limit"] == 10
    assert page["offset"] == 0
    assert len(page["items"]) == 1
    assert page["items"][0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_parcels_pagination(ac, session):
    """2. Пагинация возвращает корректные total/limit/offset."""
    await _create_type(session)

    for index in range(3):
        response = await ac.post(
            "/api/parcels",
            json={
                "name": f"Посылка {index}",
                "weight": 1.0,
                "content_value": "10.00",
                "type_id": 1,
            },
        )
        assert response.status_code == 201

    first_page = (
        await ac.get("/api/parcels", params={"limit": 2, "offset": 0})
    ).json()
    second_page = (
        await ac.get("/api/parcels", params={"limit": 2, "offset": 2})
    ).json()

    assert first_page["total"] == 3
    assert len(first_page["items"]) == 2
    assert second_page["total"] == 3
    assert len(second_page["items"]) == 1

    ids = {item["id"] for item in first_page["items"]} | {
        item["id"] for item in second_page["items"]
    }
    assert len(ids) == 3


@pytest.mark.asyncio
async def test_parcels_filter_by_calculation_status(ac, session):
    """3. Фильтр is_calculated разделяет рассчитанные и нерассчитанные посылки."""
    await _create_type(session)

    for index in range(2):
        await ac.post(
            "/api/parcels",
            json={
                "name": f"Посылка {index}",
                "weight": 1.0,
                "content_value": "10.00",
                "type_id": 1,
            },
        )

    parcels = (await ac.get("/api/parcels")).json()["items"]
    calculated_parcel_id = parcels[0]["id"]

    # Помечаем одну посылку рассчитанной напрямую в БД
    parcel = await session.get(Parcel, UUID(calculated_parcel_id))
    parcel.delivery_cost = Decimal("100.00")
    await session.commit()

    calculated = (await ac.get("/api/parcels", params={"is_calculated": "true"})).json()
    pending = (await ac.get("/api/parcels", params={"is_calculated": "false"})).json()

    assert calculated["total"] == 1
    assert calculated["items"][0]["is_calculated"] is True
    assert pending["total"] == 1
    assert pending["items"][0]["is_calculated"] is False


@pytest.mark.asyncio
async def test_session_isolation(ac, session):
    """4. Проверка изоляции сессий (Чужие посылки должны выдавать 404)."""
    await _create_type(session)

    alien_parcel = Parcel(
        name="Секретный груз",
        weight=1.0,
        content_value=Decimal("500.00"),
        session_id="user-A",
        type_id=1,
    )
    session.add(alien_parcel)
    await session.commit()

    response = await ac.get(f"/api/parcels/{alien_parcel.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_parcel(ac, session):
    """5. Удаление своей посылки и запрет удаления чужой."""
    await _create_type(session)

    created = (
        await ac.post(
            "/api/parcels",
            json={
                "name": "На удаление",
                "weight": 1.0,
                "content_value": "10.00",
                "type_id": 1,
            },
        )
    ).json()

    assert (await ac.delete(f"/api/parcels/{created['id']}")).status_code == 204
    assert (await ac.get(f"/api/parcels/{created['id']}")).status_code == 404

    alien_parcel = Parcel(
        name="Чужая посылка",
        weight=1.0,
        content_value=Decimal("10.00"),
        session_id="user-A",
        type_id=1,
    )
    session.add(alien_parcel)
    await session.commit()

    assert (await ac.delete(f"/api/parcels/{alien_parcel.id}")).status_code == 404


@pytest.mark.asyncio
async def test_create_parcel_weight_limit(ac, session):
    """6. Посылка тяжелее 31.5 кг не принимается."""
    await _create_type(session)

    response = await ac.post(
        "/api/parcels",
        json={
            "name": "Слишком тяжелая",
            "weight": 40,
            "content_value": "10.00",
            "type_id": 1,
        },
    )

    assert response.status_code == 422
    assert response.json()["status"] == "error"


@pytest.mark.asyncio
# Патчим вызов к OpenRouter, чтобы тесты не летели в интернет и не тратили токены
@patch("src.routers.support.generate_support_answer")
async def test_ask_support_endpoint(mock_llm, ac):
    """7. Поддержка принимает историю диалога и передает ее в LLM."""
    mock_llm.return_value = "Да, если аккумулятор внутри устройства."

    payload = {
        "question": "А почему?",
        "history": [
            {"role": "user", "content": "Можно ли отправить ноут?"},
            {"role": "assistant", "content": "Можно, если батарея внутри."},
        ],
    }
    response = await ac.post("/api/support/ask", json=payload)

    assert response.status_code == 200
    assert response.json()["answer"] == "Да, если аккумулятор внутри устройства."

    mock_llm.assert_awaited_once()
    _, kwargs = mock_llm.await_args
    assert kwargs["history"] == payload["history"]


@pytest.mark.asyncio
async def test_ask_support_rejects_too_long_history(ac):
    """8. Слишком длинная история диалога отклоняется."""
    payload = {
        "question": "Привет",
        "history": [
            {"role": "user", "content": f"Сообщение {index}"} for index in range(25)
        ],
    }

    response = await ac.post("/api/support/ask", json=payload)

    assert response.status_code == 422
    assert response.json()["status"] == "error"
