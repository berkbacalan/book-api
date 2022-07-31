import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "book-api_mongodb_1"
    mongo_db: str = "book-api_mongodb_1"

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")