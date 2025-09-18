from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Get database URL from environment variable or use default SQLite file
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///plants.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
