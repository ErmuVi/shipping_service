import logging

from sqlalchemy import select

from src.database import session_maker
from src.models import ParcelType

# Настраиваем логирование, чтобы в консоли было видно, что происходит
logger = logging.getLogger(__name__)


async def seed_parcel_types() -> None:
    """
    Автоматически наполняет таблицу типов посылок базовыми значениями,
    если она пустая (Одежда, Электроника, Разное).
    """
    REQUIRED_TYPES = ["Одежда", "Электроника", "Разное"]

    async with session_maker() as session:
        result = await session.execute(select(ParcelType))
        existing_types = result.scalars().all()

        if not existing_types:
            logger.info(
                "Таблица типов посылок пуста. Начинаем наполнение базовыми данными..."
            )

            new_types = [ParcelType(name=name) for name in REQUIRED_TYPES]

            session.add_all(new_types)
            await session.commit()

            logger.info("Базовые типы посылок успешно добавлены в базу данных!")
        else:
            logger.info(
                "Базовые типы посылок уже существуют в базе. Пропускаем наполнение."
            )
