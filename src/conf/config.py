from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # postgres_db: str
    # postgres_user: str
    # postgres_password: str
    # postgres_host: str
    # postgres_port: str
    sqlalchemy_database_url: str | None = None

    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()