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
        de postgresql+asyncpg://…  — normalizamos aqui.

        asyncpg NÃO entende o parâmetro `sslmode` da libpq — precisa ser removido
        da URL (o SSL vai ser configurado via connect_args no database.py).
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]

        # Neon manda sslmode= e channel_binding= no URL, ambos são libpq-only.
        # asyncpg negocia SSL/channel-binding via connect_args, então removemos daqui.
        STRIP = {"sslmode", "channel_binding"}
        if any(f"{k}=" in url for k in STRIP):
            from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
            p = urlsplit(url)
            q = [(k, v) for k, v in parse_qsl(p.query) if k.lower() not in STRIP]
            url = urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), p.fragment))
        return url

    @property
    def requires_ssl(self) -> bool:
        """True se a URL original pediu sslmode=require (Neon, RDS gerenciados, etc.)."""
        return "sslmode=require" in self.database_url.lower()

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
