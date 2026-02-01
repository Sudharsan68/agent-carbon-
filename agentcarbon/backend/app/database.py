from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback or error - usually we want to fail fast, but for now lets print a warning
    print("WARNING: DATABASE_URL not set.")
    # For now, default to a local user if not set, or leave it empty causing error later
    # DATABASE_URL = "postgresql://user:password@localhost/agentcarbon"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
