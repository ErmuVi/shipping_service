import asyncio

from celery import Celery

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
        await calculate_pending_deliveries(usd_rate)
        return usd_rate

    return asyncio.run(run_pipeline())
