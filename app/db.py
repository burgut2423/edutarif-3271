import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edutarif.db")
connect_args = {"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session
