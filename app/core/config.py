from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import urllib.parse
import sys
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
    for _ in range(2): # 2階層上がプロジェクトルート
        base_path = os.path.dirname(base_path)
env_path = os.path.join(base_path, ".env")

class Settings(BaseSettings):
    APP_NAME: str = "Shipping App"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # Environment
    ENV: str

    # Development settings
    DEV_SQL_SERVER: str
    DEV_SQL_PORT: str
    DEV_SQL_DB: str
    DEV_SQL_USER: str
    DEV_SQL_PASSWORD: str

    # Production settings
    PROD_SQL_SERVER: str
    PROD_SQL_PORT: str
    PROD_SQL_DB: str
    PROD_SQL_USER: str
    PROD_SQL_PASSWORD: str

    DATABASE_URL: Optional[str] = None
    SQL_PORT: Optional[str] = None
    SQL_SERVER: Optional[str] = None
    SQL_DB: Optional[str] = None
    SQL_USER: Optional[str] = None
    SQL_PASSWORD: Optional[str] = None

    CARRIER_UNASSIGNED_CODE: str = "95"

    class Config:
        env_file = env_path

    def __init__(self, **data):
        super().__init__(**data)

        self.SQL_SERVER = self.DEV_SQL_SERVER if self.ENV == "Development" else self.PROD_SQL_SERVER
        self.SQL_PORT = self.DEV_SQL_PORT if self.ENV == "Development" else self.PROD_SQL_PORT
        self.SQL_DB = self.DEV_SQL_DB if self.ENV == "Development" else self.PROD_SQL_DB
        self.SQL_USER = self.DEV_SQL_USER if self.ENV == "Development" else self.PROD_SQL_USER
        self.SQL_PASSWORD = self.DEV_SQL_PASSWORD if self.ENV == "Development" else self.PROD_SQL_PASSWORD
        encoded_password = urllib.parse.quote_plus(self.SQL_PASSWORD)

        self.DATABASE_URL = (
            f"mssql+pyodbc://{self.SQL_USER}:{encoded_password}@"
            f"{self.SQL_SERVER}:{self.SQL_PORT}/{self.SQL_DB}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
            "&TrustServerCertificate=yes"
            "&Encrypt=no"
            "&timeout=60"
            "&connection_timeout=60"
            "&query_timeout=60"
            "&pool_timeout=60"
            "&max_pool_size=20"
            "&min_pool_size=5"
            "&pool_pre_ping=true"
        )

@lru_cache
def get_settings():
    """Read configuration optimization"""
    return Settings()

settings = get_settings()
