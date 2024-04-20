from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    SQLALCHEMY_ECHO: bool = False
    CORS: str | None = None
    SENTINEL_MASTER_NAME: str
    SENTINEL_PASSWORD: str


settings = Settings()  # type: ignore
