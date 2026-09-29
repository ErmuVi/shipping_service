import logging
from decimal import Decimal

from sqlalchemy import select

from src.database import session_maker
from src.models import Parcel

logger = logging.getLogger(__name__)


async def calculate_pending_deliveries(usd_rate: float) -> int:
    rate_decimal = Decimal(str(usd_rate))

    logger.info(
        "Запущена фоновая задача расчёта стоимостей."
        f" Актуальный курс USD: {usd_rate} руб."
    )

    async with session_maker() as session:
        query = select(Parcel).where(Parcel.delivery_cost.is_(None))
        result = await session.execute(query)
        parcels = result.scalars().all()

        if not parcels:
            logger.info(
                "Необработанных посылок в базе данных не найдено. Расчёт завершён."
            )
            return 0

        logger.info(
            f"Найдено {len(parcels)} необработанных посылок. Начинаем пересчёт..."
        )

        for parcel in parcels:
            weight_decimal = Decimal(str(parcel.weight))
            cost = (
                weight_decimal * Decimal("0.5") + parcel.content_value * Decimal("0.01")
            ) * rate_decimal
            parcel.delivery_cost = round(cost, 2)

        await session.commit()

        logger.info(
            f"Расчёт успешно завершён. Обновлено посылок в базе: {len(parcels)}"
        )
    return len(parcels)
