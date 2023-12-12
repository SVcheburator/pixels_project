from os import environ
from pathlib import Path
# from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH_PROJECT = Path(__file__).resolve().parent.parent
BASE_PATH = BASE_PATH_PROJECT.parent
ENV_PATH = BASE_PATH.joinpath(".env")
assert ENV_PATH.is_file(), f"ENV_PATH must be {ENV_PATH}"
# load_dotenv(ENV_PATH)

class Settings(BaseSettings):
    sqlalchemy_database_url: str | None = None

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 465
    mail_server: str = "localhost"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    cloudinary_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    model_config = SettingsConfigDict(
        extra="ignore", env_file=str(ENV_PATH), env_file_encoding="utf-8"
    )


settings = Settings()
# print(f"settings : {ENV_PATH=}")
# print(f"settings {settings.sqlalchemy_database_url=}")
