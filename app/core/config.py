from pydantic_settings import BaseSettings
import os
from typing import Optional
import urllib.parse


class Settings(BaseSettings):
    APP_NAME: str = "Shipping App"
    API_PREFIX: str = "/api"
    DEBUG: bool = bool(os.getenv("DEBUG", False))
    
    # Environment
    ENV: str = os.getenv("ENV", "development")  # development or production
    
    # Database settings
    # Development settings (Docker/SQL Server)
    DEV_SQL_SERVER: str = os.getenv("DEV_SQL_SERVER", "localhost")
    DEV_SQL_PORT: str = os.getenv("DEV_SQL_PORT", "1433")
    DEV_SQL_DB: str = os.getenv("DEV_SQL_DB", "shipping_db")
    DEV_SQL_USER: str = os.getenv("DEV_SQL_USER", "sa")
    DEV_SQL_PASSWORD: str = os.getenv("DEV_SQL_PASSWORD", "YourStrong@Passw0rd")
    
    # Production settings (Remote server)
    PROD_SQL_SERVER: str = os.getenv("PROD_SQL_SERVER", "db.example.com")
    PROD_SQL_PORT: str = os.getenv("PROD_SQL_PORT", "1433")
    PROD_SQL_DB: str = os.getenv("PROD_SQL_DB", "shipping_db")
    PROD_SQL_USER: str = os.getenv("PROD_SQL_USER", "sa")
    PROD_SQL_PASSWORD: str = os.getenv("PROD_SQL_PASSWORD", "YourStrong@Passw0rd")
    
    DATABASE_URL: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Get the appropriate settings based on environment
        sql_server = self.DEV_SQL_SERVER if self.ENV == "development" else self.PROD_SQL_SERVER
        sql_port = self.DEV_SQL_PORT if self.ENV == "development" else self.PROD_SQL_PORT
        sql_db = self.DEV_SQL_DB if self.ENV == "development" else self.PROD_SQL_DB
        sql_user = self.DEV_SQL_USER if self.ENV == "development" else self.PROD_SQL_USER
        sql_password = self.DEV_SQL_PASSWORD if self.ENV == "development" else self.PROD_SQL_PASSWORD

        # URL encode the password to handle special characters
        encoded_password = urllib.parse.quote_plus(sql_password)
        
        # Create SQLAlchemy connection URL with proper ODBC configuration
        self.DATABASE_URL = (
            "mssql+pyodbc://"
            f"{sql_user}:{encoded_password}@"
            f"{sql_server}:{sql_port}/{sql_db}"
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

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 