from os import environ
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_PATH_PROJECT = Path(__file__).resolve().parent.parent
BASE_PATH = BASE_PATH_PROJECT.parent
ENV_PATH = BASE_PATH.joinpath(".env")

class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    sqlalchemy_database_url: str | None = None

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 465
    mail_server: str = "localhost"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    cloudinary_name: str = 'name'
    cloudinary_api_key: int = 247459982199157
    cloudinary_api_secret: str = 'secret'

    app_host: str = "0.0.0.0"
    app_port: int = 9000
    SPHINX_DIRECTORY: str = str(BASE_PATH.joinpath("docs", "_build", "html"))
    STATIC_DIRECTORY: str = str(BASE_PATH.joinpath("static"))

    model_config = SettingsConfigDict(
        extra="ignore", env_file=str(ENV_PATH), env_file_encoding="utf-8"
    )

    # class Config:
    #     extra = "ignore"
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


settings = Settings()


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

# Встановлення URL-рядка підключення у налаштуваннях
settings.sqlalchemy_database_url = SQLALCHEMY_DATABASE_URL