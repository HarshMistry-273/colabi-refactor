from contextlib import contextmanager
import pymongo
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.config import Config
from sqlalchemy.orm import scoped_session
from contextlib import contextmanager
from typing import Generator

engine = create_engine(Config.DATABSE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Create a scoped session
ScopedSession = scoped_session(SessionLocal)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@contextmanager
def get_db_session_celery() -> Generator:
    """
    Context manager for handling database sessions safely
    """
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
        ScopedSession.remove()


db = SessionLocal()

try:
    # Creating a MongoClient to connect to the local MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Selecting a specific database named 'your_database_name'
    database = client["colabi"]
except Exception as e:
    print(f"Error: {e}")


def get_collection():
    collection = database["chat_history"]
    yield collection
