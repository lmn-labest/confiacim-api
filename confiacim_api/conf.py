from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int = 5432

    SQLALCHEMY_ECHO: bool = False
    CORS: str | None = None

    SENTINEL_HOST: str
    SENTINEL_MASTER_NAME: str | None = None
    SENTINEL_PASSWORD: str | None = None
    SENTINEL_PORT: int = 26379


settings = Settings()  # type: ignore
