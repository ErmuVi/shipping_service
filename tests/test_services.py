from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy import select

from src.models import Parcel
from src.services.currency import get_usd_rate
from src.services.delivery import calculate_pending_deliveries
from src.services.llm import generate_support_answer


def make_async_client_mock() -> tuple[MagicMock, AsyncMock]:
    """Подменяет httpx.AsyncClient корректным async context manager."""
    client = AsyncMock()
    client_cls = MagicMock()
    client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
    client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
    return client_cls, client


@pytest.mark.asyncio
@patch("src.services.delivery.global_session_maker")
async def test_calculate_pending_deliveries_math(mock_session_maker, session):
    # Проверка точности подсчета стоимости доставки
    mock_session_maker.return_value = session

    test_parcel = Parcel(
        name="Тестовый ноутбук",
        weight=2.0,
        content_value=Decimal("100.00"),
        session_id="test-session-uuid-12345",
        type_id=1,
        delivery_cost=None,
    )
    session.add(test_parcel)
    await session.commit()

    processed_count = await calculate_pending_deliveries(
        usd_rate=100.00, session_maker=mock_session_maker
    )
    assert processed_count == 1

    result = await session.execute(
        select(Parcel).where(Parcel.name == "Тестовый ноутбук")
    )
    updated_parcel = result.scalars().first()

    assert updated_parcel is not None
    assert updated_parcel.delivery_cost == Decimal("200.00")


@pytest.mark.asyncio
@patch("src.services.currency.aioredis.from_url")
async def test_get_usd_rate_uses_cache(mock_from_url):
    """Курс берется из Redis, если он там есть."""
    redis_client = AsyncMock()
    redis_client.get.return_value = "92.5"
    mock_from_url.return_value = redis_client

    rate = await get_usd_rate()

    assert rate == 92.5
    redis_client.set.assert_not_called()


@pytest.mark.asyncio
@patch("src.services.currency.aioredis.from_url")
async def test_get_usd_rate_falls_back_to_stale_cache(mock_from_url):
    """Если ЦБ недоступен, используется последнее сохраненное значение."""
    redis_client = AsyncMock()
    # Первый get — кеш с TTL пуст, второй — аварийный кеш без TTL
    redis_client.get.side_effect = [None, "95.5"]
    mock_from_url.return_value = redis_client

    client_cls, http_client = make_async_client_mock()
    http_client.get.side_effect = httpx.ConnectError("ЦБ недоступен")

    with patch("src.services.currency.httpx.AsyncClient", new=client_cls):
        rate = await get_usd_rate()

    assert rate == 95.5
    redis_client.set.assert_not_called()


@pytest.mark.asyncio
async def test_generate_support_answer_passes_history_to_llm():
    """История диалога уходит в LLM перед текущим вопросом."""
    response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": "Привет! Чем помочь?"}}]},
    )

    client_cls, http_client = make_async_client_mock()
    http_client.post.return_value = response

    with patch("src.services.llm.httpx.AsyncClient", new=client_cls):
        answer = await generate_support_answer(
            "А что с ноутбуками?",
            "Правила про ноутбуки",
            history=[
                {"role": "user", "content": "Привет"},
                {"role": "assistant", "content": "Здравствуйте!"},
            ],
        )

    assert answer == "Привет! Чем помочь?"

    messages = http_client.post.call_args.kwargs["json"]["messages"]
    assert [message["role"] for message in messages] == [
        "system",
        "user",
        "assistant",
        "user",
    ]
    assert messages[-1]["content"] == "А что с ноутбуками?"


@pytest.mark.asyncio
async def test_generate_support_answer_handles_network_error():
    """Сетевая ошибка не роняет эндпоинт, а возвращает понятный текст."""
    client_cls, http_client = make_async_client_mock()
    http_client.post.side_effect = httpx.ConnectError("нет сети")

    with patch("src.services.llm.httpx.AsyncClient", new=client_cls):
        answer = await generate_support_answer("Привет", "")

    assert "временно недоступна" in answer
