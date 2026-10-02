import httpx
import redis.asyncio as aioredis

from src.config import settings

#Функция которая выдает курс, берет его из кеша редис если его там нет то идет на на сайт центробанка
async def get_usd_rate() -> float:
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

    try:

        usd_rate = await redis_client.get("usd_rate")

        if usd_rate is not None:
            return float(usd_rate)

        url = "https://www.cbr-xml-daily.ru/daily_json.js"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        rate = float(data["Valute"]["USD"]["Value"])

        await redis_client.set("usd_rate", str(rate), ex=3600)
        return rate

    finally:
        await redis_client.aclose()
