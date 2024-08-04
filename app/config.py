from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    DB_SYSTEM: str
    DB_DRIVER: str
    DB_NAME: str
    DB_USERNAME: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_ECHO: bool = False

    SUPERADMIN_EMAIL: str
    SUPERADMIN_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORYTHM: str
    JWT_ACCESS_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRE_DAYS: int

    api_v1_prefix: str = "/api/v1"
    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).resolve().parent.parent}/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return URL.create(
            drivername=f"{self.DB_SYSTEM}+{self.DB_DRIVER}",
            database=self.DB_NAME,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
        ).render_as_string(hide_password=False)


settings = Settings()  # type: ignore
print(settings.database_url)
