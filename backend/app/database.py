import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Se estiver rodando na Vercel e o banco for SQLite, usa a pasta /tmp para escrita
if os.getenv("VERCEL") and db_url and db_url.startswith("sqlite"):
    db_url = "sqlite:////tmp/psicometrico.db"

# Ajuste especial para SQLite devido ao acesso multi-thread do FastAPI
connect_args = {}
if db_url and db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
