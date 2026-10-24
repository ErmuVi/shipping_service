import logging
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as aioredis
from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.database import get_async_session
from src.middlewares.session import SessionMiddleware
from src.routers.parcel import router as parcels_router
from src.routers.support import router as support_router
from src.routers.types import router as types_read
from src.seed import seed_parcel_types
from src.services.rag import init_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

# Детальные логи приложения в dev-режиме, без шума от сторонних библиотек
if settings.DEBUG:
    logging.getLogger("src").setLevel(logging.DEBUG)

# Собранный фронтенд (frontend/dist) при сборке Docker-образа копируется сюда
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# При запуске сервиса инициилизируем создание типов посылок
# и превращаем нашу базу знаний в вектора
@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_parcel_types()
    await init_vector_store()
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    logger.warning(
        f"Ошибка валидации данных при запросе на {request.url.path}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Переданы некорректные данные",
            "details": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.warning(
        f"HTTP Ошибка {exc.status_code} на пути {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "details": None,
        },
    )


app.add_middleware(SessionMiddleware)

# CORS нужен только если фронтенд запускается на отдельном origin.
# В обычном режиме Vite проксирует запросы, и куки остаются same-origin.
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(parcels_router, prefix="/api")
app.include_router(types_read, prefix="/api")
app.include_router(support_router, prefix="/api")


@app.get("/healthcheck")
async def healthcheck(db: AsyncSession = Depends(get_async_session)):
    checks = {"database": False, "redis": False, "qdrant": False}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as exc:  # noqa: BLE001 - healthcheck не должен падать
        logger.error(f"Проверка PostgreSQL не удалась: {exc}")

    redis_client = aioredis.from_url(settings.redis_url)
    try:
        checks["redis"] = bool(await redis_client.ping())
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Проверка Redis не удалась: {exc}")
    finally:
        await redis_client.aclose()

    qdrant_client = AsyncQdrantClient(
        url=settings.qdrant_url, timeout=5, check_compatibility=False
    )
    try:
        await qdrant_client.get_collections()
        checks["qdrant"] = True
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Проверка Qdrant не удалась: {exc}")
    finally:
        await qdrant_client.close()

    is_healthy = checks["database"]
    return JSONResponse(
        status_code=200 if is_healthy else 503,
        content={
            "status": "ok" if is_healthy else "unhealthy",
            "environment": settings.ENVIRONMENT,
            "checks": checks,
        },
    )


class SPAStaticFiles(StaticFiles):
    """Отдает index.html для любого несуществующего пути (клиентский роутинг)."""

    async def get_response(self, path, scope):  # type: ignore[override]
        # Неизвестные /api-пути должны давать 404, а не index.html
        if path == "api" or path.startswith("api/"):
            raise StarletteHTTPException(status_code=404)

        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


# Монтируем фронтенд последним, чтобы API-роуты имели приоритет
if STATIC_DIR.is_dir():
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="frontend")
else:
    logger.info(
        "Директория со сборкой фронтенда не найдена (%s). "
        "API работает без веб-интерфейса.",
        STATIC_DIR,
    )
