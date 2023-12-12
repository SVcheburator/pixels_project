from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlalchemy_database_url: str | None = None

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 465
    mail_server: str = "localhost"

    redis_host: str = "localhost"
    redis_port: int = 6379

    cloudinary_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
