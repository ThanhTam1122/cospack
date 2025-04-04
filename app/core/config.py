from pydantic_settings import BaseSettings
import os
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Shipping App"
    API_PREFIX: str = "/api"
    DEBUG: bool = bool(os.getenv("DEBUG", False))
    
    # Environment
    ENV: str = os.getenv("ENV", "development")  # development or production
    
    # Database settings
    # Development settings (Docker/MySQL)
    DEV_MYSQL_USER: str = os.getenv("DEV_MYSQL_USER", "shipping_user")
    DEV_MYSQL_PASSWORD: str = os.getenv("DEV_MYSQL_PASSWORD", "shipping_password")
    DEV_MYSQL_HOST: str = os.getenv("DEV_MYSQL_HOST", "localhost")
    DEV_MYSQL_PORT: str = os.getenv("DEV_MYSQL_PORT", "3306")
    DEV_MYSQL_DB: str = os.getenv("DEV_MYSQL_DB", "shipping_db")
    
    # Production settings (Remote server)
    PROD_MYSQL_USER: str = os.getenv("PROD_MYSQL_USER", "shipping_user")
    PROD_MYSQL_PASSWORD: str = os.getenv("PROD_MYSQL_PASSWORD", "shipping_password")
    PROD_MYSQL_HOST: str = os.getenv("PROD_MYSQL_HOST", "db.example.com")
    PROD_MYSQL_PORT: str = os.getenv("PROD_MYSQL_PORT", "3306")
    PROD_MYSQL_DB: str = os.getenv("PROD_MYSQL_DB", "shipping_db")
    
    DATABASE_URL: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.ENV == "development":
            print(f"mysql+pymysql://{self.DEV_MYSQL_USER}:{self.DEV_MYSQL_PASSWORD}@{self.DEV_MYSQL_HOST}:{self.DEV_MYSQL_PORT}/{self.DEV_MYSQL_DB}")
            # Use development database settings
            self.DATABASE_URL = f"mysql+pymysql://{self.DEV_MYSQL_USER}:{self.DEV_MYSQL_PASSWORD}@{self.DEV_MYSQL_HOST}:{self.DEV_MYSQL_PORT}/{self.DEV_MYSQL_DB}"
        else:
            # Use production database settings
            self.DATABASE_URL = f"mysql+pymysql://{self.PROD_MYSQL_USER}:{self.PROD_MYSQL_PASSWORD}@{self.PROD_MYSQL_HOST}:{self.PROD_MYSQL_PORT}/{self.PROD_MYSQL_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 