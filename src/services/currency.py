import httpx
import redis.asyncio as aioredis

redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)


async def get_usd_rate() -> float:

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
