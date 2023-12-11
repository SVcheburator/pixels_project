from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # postgres_db: str
    # postgres_user: str
    # postgres_password: str
    # postgres_host: str
    # postgres_port: str
    sqlalchemy_database_url: str | None = None

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str

    redis_host: str
    redis_port: int

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str


    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
