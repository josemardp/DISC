import sys
import os
import pytest
from pathlib import Path

os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENABLE_DEMO_SEED"] = "true"
os.environ["AUTO_CREATE_SCHEMA"] = "true"

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

@pytest.fixture(scope="session", autouse=True)
def create_tables_and_seed():
    from backend.app.database import Base, engine, SessionLocal
    from backend.app.seed import seed_db
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
