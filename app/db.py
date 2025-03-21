"""
db.py (Database Connection & Session Management)

Configures SQLAlchemy and database engine.
Defines the session factory to interact with the database.
Provides the get_db function for dependency injection in FastAPI.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite3 db URL
SQL_ALCHEMY_DB_URL = "sqlite:///./blog-app.db"

# Create an engine to interact with the SQLite database
engine = create_engine(SQL_ALCHEMY_DB_URL, connect_args={"check_same_thread": False})

# Create a session maker, which will be used to create sessions to interact with the db
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for defining ORM 
Base = declarative_base()

def get_db():
    db = LocalSession
    try:
        yield db
    finally:
        db.close()

