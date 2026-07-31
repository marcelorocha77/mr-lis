from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+asyncpg://mr:mr_dev_pw@db:5432/mrlis"
    redis_url: str = "redis://redis:6379/0"

    cors_origins: str = "http://localhost:3000"

    @property
    def normalized_database_url(self) -> str:
        """Neon/Fly.io entregam a URL como postgresql://… ; SQLAlchemy async precisa
        de postgresql+asyncpg://…  — normalizamos aqui."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
