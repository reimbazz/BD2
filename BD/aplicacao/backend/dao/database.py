from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql://paulo:1234@localhost:5432/trabalhoBD2'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def connect():
    return SessionLocal

def get_engine():
    return engine
