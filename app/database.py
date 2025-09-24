from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
import socket

# Get database URL from environment variable or use default SQLite file
# DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///plants.db")
# DATABASE_PATH = os.environ.get("DATABASE_PATH", "database/plants.db")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

# Get database connection parameters from environment variables
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
# Default to 'db' for Docker
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "db")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")  # Default to 5432

# Construct database URL
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    return SessionLocal()
