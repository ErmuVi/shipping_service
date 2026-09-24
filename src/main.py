from fastapi import FastAPI

from src.config import settings

app = FastAPI(
    title=settings.APP_TITLE,
    debug=settings.DEBUG,
)


@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "working",
        "environment": settings.ENVIRONMENT,
        "database_connected": bool(settings.DB_HOST),
    }
