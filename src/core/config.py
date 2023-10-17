import os
from logging import config as logging_config

from core.logger import LOGGING

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    app_title: str = "FastAPI exp app"
    database_dsn: PostgresDsn = "postgresql+asyncpg://me:1111111@pg_02:5432/my"
    BLACK_LIST: list[str] = []
    PROJECT_HOST: str = '0.0.0.0'
    PROJECT_PORT: int = 8000

    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    echo_query: bool = True

    class Config:
        env_file = '../.env'


app_settings = AppSettings()
