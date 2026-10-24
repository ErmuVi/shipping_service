from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_TITLE: str = "Shipping Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # Кука сессии: 1 год, чтобы посылки не терялись после закрытия браузера
    SESSION_COOKIE_MAX_AGE: int = 60 * 60 * 24 * 365
    COOKIE_SECURE: bool = False

    # Список origin'ов для CORS (пусто = выключен, фронтенд работает через прокси)
    CORS_ORIGINS: list[str] = []

    OPENROUTER_API_KEY: str = Field(default=...)
    DB_HOST: str = Field(default=...)
    DB_PORT: int = Field(default=...)
    DB_USER: str = Field(default=...)
    DB_PASSWORD: str = Field(default=...)
    DB_NAME: str = Field(default=...)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def database_url(self) -> str:

        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
