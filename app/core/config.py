from __future__ import annotations

from pathlib import Path

from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "telegram-chats-api"
    APP_ENV: str = "dev"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # DB (основная схема подключения)
    DB_SCHEME: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    # SQLite fallback
    USE_SQLITE: bool = False
    SQLITE_PATH: str = "./data/app.db"

    # Явный URL для alembic (если хочется переопределить)
    ALEMBIC_DB_URL: str | None = None

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Итоговый URL подключения:
        1) Если USE_SQLITE=True → sqlite+aiosqlite:///<abs_path>
        2) Если задан ALEMBIC_DB_URL → берём его
        3) Иначе собираем из DB_*
        """
        if self.USE_SQLITE:
            path = Path(self.SQLITE_PATH).absolute()
            return f"sqlite+aiosqlite:///{path}"

        if self.ALEMBIC_DB_URL:
            return self.ALEMBIC_DB_URL

        assert (
            self.DB_SCHEME
            and self.DB_HOST
            and self.DB_PORT
            and self.DB_USER
            and self.DB_PASSWORD
            and self.DB_NAME
        ), "DB env is incomplete"

        return (
            f"{self.DB_SCHEME}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
