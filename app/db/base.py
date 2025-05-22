from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import time
import sys
import pyodbc

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_database():
    """Create database if it doesn't exist"""
    try:
        master_conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings.SQL_SERVER},{settings.SQL_PORT};"
            f"DATABASE=master;"
            f"UID={settings.SQL_USER};"
            f"PWD={settings.SQL_PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        
        master_conn = pyodbc.connect(master_conn_str, autocommit=True)
        cursor = master_conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{settings.SQL_DB}'")
        if not cursor.fetchone():
            logger.info(f"Creating database {settings.SQL_DB}")
            # Create database with simple recovery model
            create_db_sql = f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{settings.SQL_DB}')
            BEGIN
                CREATE DATABASE [{settings.SQL_DB}]
                ALTER DATABASE [{settings.SQL_DB}] SET RECOVERY SIMPLE;
                ALTER DATABASE [{settings.SQL_DB}] SET AUTO_CLOSE OFF;
                ALTER DATABASE [{settings.SQL_DB}] SET MULTI_USER;
            END
            """
            cursor.execute(create_db_sql)
            logger.info(f"Database {settings.SQL_DB} created successfully")
            
            # Give SQL Server a moment to initialize the database
            time.sleep(5)
        else:
            logger.info(f"Database {settings.SQL_DB} already exists")
            
            # Ensure database is properly configured
            cursor.execute(f"""
            ALTER DATABASE [{settings.SQL_DB}] SET RECOVERY SIMPLE;
            ALTER DATABASE [{settings.SQL_DB}] SET AUTO_CLOSE OFF;
            ALTER DATABASE [{settings.SQL_DB}] SET MULTI_USER;
            """)
        
        cursor.close()
        master_conn.close()
        
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

def create_user():
    """Create user if it doesn't exist"""
    # Skip user creation for sa account
    if settings.SQL_USER.lower() == 'sa':
        logger.info("Using sa account - skipping user creation")
        return
        
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Connect to the new database
            db_conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.SQL_SERVER},{settings.SQL_PORT};"
                f"DATABASE={settings.SQL_DB};"
                f"UID={settings.SQL_USER};"
                f"PWD={settings.SQL_PASSWORD};"
                "TrustServerCertificate=yes;"
            )
            
            logger.info(f"Setting up user in database: {settings.SQL_DB}")
            db_conn = pyodbc.connect(db_conn_str, autocommit=True)
            cursor = db_conn.cursor()
            
            # Check if login exists first
            cursor.execute(f"SELECT name FROM sys.server_principals WHERE name = '{settings.SQL_USER}'")
            if not cursor.fetchone():
                logger.info(f"Creating login {settings.SQL_USER}")
                cursor.execute(f"CREATE LOGIN [{settings.SQL_USER}] WITH PASSWORD = '{settings.SQL_PASSWORD}'")
            
            # Then check if user exists
            cursor.execute(f"SELECT name FROM sys.database_principals WHERE name = '{settings.SQL_USER}'")
            if not cursor.fetchone():
                logger.info(f"Creating user {settings.SQL_USER}")
                cursor.execute(f"CREATE USER [{settings.SQL_USER}] FOR LOGIN [{settings.SQL_USER}]")
                cursor.execute(f"ALTER ROLE db_owner ADD MEMBER [{settings.SQL_USER}]")
            
            cursor.close()
            db_conn.close()
            logger.info("User setup completed successfully")
            return
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Error setting up user after {max_retries} attempts: {str(e)}")
                raise

def create_db_engine(max_retries=3, retry_delay=2):
    """Create database engine with retry logic"""
    retries = 0
    last_error = None

    if settings.IS_BUILDING:
        return
    
    while retries < max_retries:
        try:
            # if settings.ENV == "Development":
            #     create_database()
            #     time.sleep(2)
            #     create_user()
            
            # Create engine with proper connection pooling and timeouts
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                connect_args={
                    "timeout": 30
                }
            )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Successfully connected to {settings.ENV} database at {settings.SQL_SERVER}")
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

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 