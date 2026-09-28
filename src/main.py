from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.middlewares.session import SessionMiddleware
from src.routers.parcel import router as parcels_router
from src.routers.types import router as types_read
from src.seed import seed_parcel_types


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_parcel_types()
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware)

app.include_router(parcels_router)
app.include_router(types_read)


@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "working",
        "environment": settings.ENVIRONMENT,
        "database_connected": bool(settings.DB_HOST),
    }
