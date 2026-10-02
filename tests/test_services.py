from decimal import Decimal
from unittest.mock import patch

import pytest
from sqlalchemy import select

from src.models import Parcel
from src.services.delivery import calculate_pending_deliveries


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

    processed_count = await calculate_pending_deliveries(usd_rate=100.00, session_maker=mock_session_maker)
    assert processed_count == 1

    result = await session.execute(
        select(Parcel).where(Parcel.name == "Тестовый ноутбук")
    )
    updated_parcel = result.scalars().first()

    assert updated_parcel is not None
    assert updated_parcel.delivery_cost == Decimal("200.00")
