from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.base import engine, Base
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create database tables
try:
    if settings.ENV == 'Development':
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        logger.info(f"Connected to database at {settings.DEV_SQL_SERVER if settings.ENV == 'Development' else settings.PROD_SQL_SERVER}")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Shipping API",
        "environment": settings.ENV,
        "database": settings.DEV_SQL_SERVER if settings.ENV == "Development" else settings.PROD_SQL_SERVER
    }

# This block is only used when running app/main.py directly
# When running from main.py, this block is skipped
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENV} mode")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 