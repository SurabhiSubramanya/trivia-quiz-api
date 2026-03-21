# SQLAlchemy engine + session
# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trivia.db")

# connect_args only needed for SQLite (allows multi-threaded use)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that provides a DB session per request and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
