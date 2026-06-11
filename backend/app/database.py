import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

db_url = settings.DATABASE_URL

# Normaliza schemes do Postgres para o driver psycopg2
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Fallback para SQLite em /tmp somente quando DATABASE_URL já aponta para sqlite
# (nunca ativa se houver uma URL Postgres configurada)
if os.getenv("VERCEL") and db_url and db_url.startswith("sqlite"):
    db_url = "sqlite:////tmp/psicometrico.db"

is_postgres = db_url and db_url.startswith("postgresql")

if is_postgres:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 5},
    )
else:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
