from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
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
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "details": None,
        },
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
