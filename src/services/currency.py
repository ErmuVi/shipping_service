import logging

import httpx
import redis.asyncio as aioredis

from src.config import settings

logger = logging.getLogger(__name__)

CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


async def get_usd_rate() -> float:
    """Отдает курс USD из кеша Redis.

    Если кеша нет — идем в API ЦБ. Если ЦБ недоступен, используем последнее
    успешно сохраненное значение (без TTL), чтобы фоновый расчет не падал.
    """
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

    try:
        cached_rate = await redis_client.get("usd_rate")
        if cached_rate is not None:
            return float(cached_rate)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(CBR_URL)
                response.raise_for_status()
                data = response.json()

            rate = float(data["Valute"]["USD"]["Value"])

        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            stale_rate = await redis_client.get("usd_rate:last")
            if stale_rate is not None:
                logger.warning(
                    "Не удалось получить курс USD (%s). "
                    "Используем последнее сохраненное значение: %s",
                    exc,
                    stale_rate,
                )
                return float(stale_rate)

            logger.error("Не удалось получить курс USD и нет сохраненного: %s", exc)
            raise

        await redis_client.set("usd_rate", str(rate), ex=3600)
        # Последнее известное значение без TTL — аварийный фолбэк
        await redis_client.set("usd_rate:last", str(rate))

        return rate

    finally:
        await redis_client.aclose()
