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

    DB_HOST: str = Field(default=...)
    DB_PORT: int = Field(default=...)
    DB_USER: str = Field(default=...)
    DB_PASSWORD: str = Field(default=...)
    DB_NAME: str = Field(default=...)


    @property
    def database_url(self) -> str:

        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
