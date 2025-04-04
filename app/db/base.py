from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import time
import sys

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_db_engine(max_retries=3, retry_delay=2):
    """Create database engine with retry logic"""
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            engine = create_engine(settings.DATABASE_URL)
            # Test the connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info(f"Successfully connected to {settings.ENV} database at {settings.DATABASE_URL.split('@')[1]}")
            return engine
        except Exception as e:
            last_error = e
            retries += 1
            if retries < max_retries:
                logger.warning(f"Database connection attempt {retries} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(last_error)}")
                logger.error("Please check your database configuration and ensure the database server is running.")
                sys.exit(1)

# Create the engine with retry logic
engine = create_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 