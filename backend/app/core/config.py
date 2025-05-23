from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SECURITY_SECRET_KEY: str = os.environ.get("SECRET_KEY")
    SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS: int = 12 * 24 * 60 * 60 # 12 days
    SECURITY_ALGORITHM: str = "HS256"

    DATABASE_URL: str = f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@db:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}'

settings = Settings()