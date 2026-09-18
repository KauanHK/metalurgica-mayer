from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da aplicação, lida do ambiente (e do `.env` em dev).

    `extra="forbid"` é deliberado: uma chave a mais no `.env` derruba a app na
    subida em vez de ser silenciosamente ignorada. É por isso que o `.env` da
    raiz (o do docker-compose, que carrega `COMPOSE_PROJECT_NAME` e afins) não
    serve como `backend/.env` — são arquivos diferentes, com chaves diferentes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # Nome exibido no OpenAPI e nos logs.
    APP_NAME: str = "Metalúrgica Mayer — API"
    # `local`, `homolog` ou `production`. Só muda diagnóstico e defaults de CORS.
    ENVIRONMENT: Literal["local", "homolog", "production"] = "local"

    # Nível do root logger (ver app/core/logging_config.py). Sem isso configurado,
    # `logger.info`/`logger.debug` da aplicação não aparecem em lugar nenhum.
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Origens liberadas no CORS, separadas por vírgula. Em produção o nginx serve
    # front e API na mesma origem e a lista pode ficar vazia; em dev o Next roda
    # em :3000 e a API em :8000, que são origens distintas.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Conexão com o Postgres. `DATABASE_URL` tem precedência; sem ela, a URI é
    # montada a partir das POSTGRES_* (ver `sqlalchemy_database_uri`).
    DATABASE_URL: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    # Autenticação. `core/security` monta e valida os tokens a partir destas
    # chaves; quem os emite e os exige é o módulo `users` (login e
    # `get_current_actor`).
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MIN: int = 30
    REFRESH_TOKEN_EXPIRES_DAYS: int = 7

    @property
    def cors_origins(self) -> list[str]:
        """Lista de origens do CORS, já sem espaços e sem entradas vazias."""

        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def sqlalchemy_database_uri(self) -> str:
        """URI de conexão do SQLAlchemy, com driver assíncrono (asyncpg)."""

        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
