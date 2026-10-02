import asyncio

from celery import Celery
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import settings
from src.services.currency import get_usd_rate
from src.services.delivery import calculate_pending_deliveries

celery_app = Celery(
    "shipping_task",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.beat_schedule = {
    "calculate-delivery-every-5-minute": {
        "task": "src.worker.calculate_delivery_task",
        "schedule": 300.0,
    }
}
celery_app.conf.timezone = "UTC"


@celery_app.task
def calculate_delivery_task():
    async def run_pipeline():
        usd_rate = await get_usd_rate()

        local_engine = create_async_engine(settings.database_url)
        local_session_maker = async_sessionmaker(local_engine, expire_on_commit=False)

        try:
            await calculate_pending_deliveries(
                usd_rate, session_maker=local_session_maker
            )
        finally:
            await local_engine.dispose()

        return usd_rate

    return asyncio.run(run_pipeline())
