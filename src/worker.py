import asyncio

from celery import Celery

from src.services.currency import get_usd_rate
from src.services.delivery import calculate_pending_deliveries

celery_app = Celery(
    "shipping_task",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
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
    usd_rate = asyncio.run(get_usd_rate())
    asyncio.run(calculate_pending_deliveries(usd_rate))
    return usd_rate
