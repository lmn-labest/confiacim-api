from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="confiacim_api_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
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

    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    VISIBILITY_TIMEOUT: int = 86400


settings = Settings()  # type: ignore
