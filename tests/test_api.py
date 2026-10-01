from decimal import Decimal
from unittest.mock import patch
import pytest
from src.models import Parcel
from src.models.parcel_type import ParcelType

@pytest.mark.asyncio
async def test_create_and_get_parcel_flow(ac, session):
    """1. Сквозной тест создания посылки через API и её проверки в списке."""
    # Создаем тип посылки по вашей модели (id и name)
    test_type = ParcelType(id=1, name="Одежда")
    session.add(test_type)
    await session.commit()

    # Отправляем POST-запрос на создание новой посылки
    payload = {
        "name": "Планшет",
        "weight": 0.8,
        "content_value": "350.00",
        "type_id": 1,
    }
    response = await ac.post("/parcels", json=payload)
    assert response.status_code == 200
    parcel_id = response.json()["id"]

    # Проверяем её наличие в списке через GET-запрос
    get_response = await ac.get("/parcels")
    assert get_response.status_code == 200

    parcels_list = get_response.json()
    # Если роут возвращает пагинированный словарь (с ключом результатов), достаем список
    if isinstance(parcels_list, dict) and "results" in parcels_list:
        parcels_list = parcels_list["results"]
        
    if isinstance(parcels_list, list):
        assert len(parcels_list) == 1
        assert parcels_list[0]["id"] == parcel_id
    else:
        assert parcels_list["id"] == parcel_id


@pytest.mark.asyncio
async def test_session_isolation(ac, session):
    """2. Проверка изоляции сессий (Чужие посылки должны выдавать 404)."""
    # Создаем посылку в тестовой базе вручную от имени пользователя 'user-A'
    alien_parcel = Parcel(
        name="Секретный груз",
        weight=1.0,
        content_value=Decimal("500.00"),
        session_id="user-A",
        type_id=1,
    )
    session.add(alien_parcel)
    await session.commit()

    # Пытаемся прочитать её через HTTP-клиент, у которого будет ДРУГАЯ сессия в куках
    response = await ac.get(f"/parcels/{alien_parcel.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
# Патчим вызов к OpenRouter, чтобы тесты не летели в интернет и не тратили токены
@patch("src.routers.support.generate_support_answer")
async def test_ask_support_endpoint(mock_llm, ac):
    """4. Тест эндпоинта ИИ-поддержки (RAG-пайплайн)."""
    # Задаем фейковый ответ, который вернет заглушка
    mock_llm.return_value = "Ноутбуки отправлять можно, если батарея внутри."

    payload = {"question": "Можно ли отправить ноут?"}
    response = await ac.post("/support/ask", json=payload)

    # Проверяем, что роут вернул правильную структуру из ТЗ
    assert response.status_code == 200
    assert response.json()["answer"] == "Ноутбуки отправлять можно, если батарея внутри."
